# Kubernetes Overlays - Environment-Specific Configurations

This directory contains Kustomize overlays for different deployment environments.

## 📁 Directory Structure

```
kubernetes/
├── base/                           # Base configuration
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
└── overlays/
    ├── development/                # Development environment
    │   └── kustomization.yaml
    ├── staging/                    # Staging environment
    │   └── kustomization.yaml
    └── production/                 # Production environment
        └── kustomization.yaml
```

## 🎯 Environment Configurations

### Development
- **Namespace**: `voyage-analytics-dev`
- **Replicas**: 1
- **Image**: `voyage-analytics:latest` (local/development)
- **Image Pull Policy**: `IfNotPresent` (use local image)
- **Resource Requests**: 256Mi memory, 250m CPU
- **Resource Limits**: 512Mi memory, 500m CPU
- **Environment**: Development (debug logs)

### Staging
- **Namespace**: `voyage-analytics-staging`
- **Replicas**: 2
- **Image**: `your-registry.com/voyage-analytics:1.0.0-rc` (from registry)
- **Image Pull Policy**: `Always` (always pull)
- **Resource Requests**: 512Mi memory, 500m CPU
- **Resource Limits**: 1Gi memory, 1000m CPU
- **Environment**: Staging (info logs)

### Production
- **Namespace**: `voyage-analytics-prod`
- **Replicas**: 3
- **Image**: `your-registry.com/voyage-analytics:1.0.0` (from registry)
- **Image Pull Policy**: `Always` (always pull)
- **Resource Requests**: 512Mi memory, 500m CPU
- **Resource Limits**: 1Gi memory, 1000m CPU
- **Environment**: Production (warning logs)
- **Features**: Pod anti-affinity, rolling updates

## 🚀 Deployment Commands

### Deploy to Development

```bash
# Build image locally
docker build -f docker/Dockerfile -t voyage-analytics:latest .

# Deploy using development overlay
kubectl apply -k kubernetes/overlays/development

# Or using kustomize:
kustomize build kubernetes/overlays/development | kubectl apply -f -
```

### Deploy to Staging

```bash
# Build and push image
docker build -f docker/Dockerfile -t your-registry.com/voyage-analytics:1.0.0-rc .
docker push your-registry.com/voyage-analytics:1.0.0-rc

# Deploy using staging overlay
kubectl apply -k kubernetes/overlays/staging
```

### Deploy to Production

```bash
# Build and push image
docker build -f docker/Dockerfile -t your-registry.com/voyage-analytics:1.0.0 .
docker push your-registry.com/voyage-analytics:1.0.0

# Deploy using production overlay
kubectl apply -k kubernetes/overlays/production

# Verify deployment
kubectl -n voyage-analytics-prod get all
```

## 📋 Verification Commands

### Check Overlay Configuration Before Applying

```bash
# Preview what will be deployed (development)
kustomize build kubernetes/overlays/development

# Preview with validation
kubectl apply -k kubernetes/overlays/development --dry-run=client -o yaml

# Preview for staging
kubectl apply -k kubernetes/overlays/staging --dry-run=client -o yaml

# Preview for production
kubectl apply -k kubernetes/overlays/production --dry-run=client -o yaml
```

### Verify Deployed Resources

```bash
# Check development deployment
kubectl -n voyage-analytics-dev get all
kubectl -n voyage-analytics-dev describe deployment voyage-analytics

# Check staging deployment
kubectl -n voyage-analytics-staging get all
kubectl -n voyage-analytics-staging describe deployment voyage-analytics

# Check production deployment
kubectl -n voyage-analytics-prod get all
kubectl -n voyage-analytics-prod describe deployment voyage-analytics
```

## 🔄 Customization

### Modifying Environment-Specific Settings

To customize an environment overlay:

1. **Edit the overlay's kustomization.yaml**:
   ```bash
   vi kubernetes/overlays/<environment>/kustomization.yaml
   ```

2. **Common customizations**:
   - Change `newTag` for different image versions
   - Modify `replicas` for scaling
   - Update `resources` for different memory/CPU requirements
   - Change `LOG_LEVEL` or other environment variables

3. **Example - Increase production replicas**:
   ```yaml
   replicas:
     - name: voyage-analytics
       count: 5  # Changed from 3
   ```

4. **Apply the changes**:
   ```bash
   kubectl apply -k kubernetes/overlays/production
   ```

### Adding New Configuration

To add application-specific configuration to an environment:

1. **Add to environment's kustomization.yaml**:
   ```yaml
   configMapGenerator:
     - name: voyage-analytics-config
       behavior: merge
       literals:
         - MY_CONFIG=value
   ```

2. **Or create a new ConfigMap patch**:
   ```bash
   cat > kubernetes/overlays/<environment>/configmap-patch.yaml << EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: voyage-analytics-config
   data:
     NEW_VAR: "value"
   EOF
   ```

3. **Add to kustomization.yaml**:
   ```yaml
   patchesStrategicMerge:
     - configmap-patch.yaml
   ```

## 💾 Backup & Recovery

### Backup Current Configuration

```bash
# Backup deployment from development
kubectl -n voyage-analytics-dev get deployment voyage-analytics -o yaml > voyage-analytics-dev-backup.yaml

# Backup all resources from staging
kubectl -n voyage-analytics-staging get all -o yaml > voyage-analytics-staging-backup.yaml
```

### Restore from Backup

```bash
# Restore to development
kubectl apply -f voyage-analytics-dev-backup.yaml

# Restore to staging
kubectl apply -f voyage-analytics-staging-backup.yaml
```

## 📊 Resource Comparison

| Aspect | Development | Staging | Production |
|--------|-------------|---------|------------|
| Namespace | voyage-analytics-dev | voyage-analytics-staging | voyage-analytics-prod |
| Replicas | 1 | 2 | 3 |
| CPU Request | 250m | 500m | 500m |
| Memory Request | 256Mi | 512Mi | 512Mi |
| CPU Limit | 500m | 1000m | 1000m |
| Memory Limit | 512Mi | 1Gi | 1Gi |
| Image | Local | Registry RC | Registry Release |
| Anti-Affinity | ✗ | ✗ | ✓ |
| Metrics | ✗ | ✓ | ✓ |
| Tracing | ✗ | ✗ | ✓ |

## 🔧 Troubleshooting

### Overlay Not Applying Correctly

```bash
# Verify overlay is valid
kustomize build kubernetes/overlays/<environment>

# Check for YAML syntax errors
kubectl apply -k kubernetes/overlays/<environment> --validate=strict

# See what changed
kubectl apply -k kubernetes/overlays/<environment> --dry-run=client -o yaml | diff -u <(kubectl get all -n voyage-analytics-<env>) -
```

### ConfigMap Not Updating

```bash
# Force pod restart after config change
kubectl rollout restart deployment/voyage-analytics -n voyage-analytics-<env>

# Verify new config
kubectl get configmap voyage-analytics-config -n voyage-analytics-<env> -o yaml
```

### Rolling Back to Previous Overlay

```bash
# View rollout history
kubectl rollout history deployment/voyage-analytics -n voyage-analytics-<env>

# Rollback to previous version
kubectl rollout undo deployment/voyage-analytics -n voyage-analytics-<env>
```

## 📚 Advanced Usage with Kustomize

### Using Multiple Overlays Together

```bash
# Deploy both staging and production simultaneously
kustomize build kubernetes/overlays/staging | kubectl apply -f -
kustomize build kubernetes/overlays/production | kubectl apply -f -
```

### Generate YAML without Applying

```bash
# See everything that will be deployed
kubectl kustomize kubernetes/overlays/production > production-manifest.yaml

# Review before applying
less production-manifest.yaml
kubectl apply -f production-manifest.yaml
```

### Create New Overlay

```bash
# Create a new environment (e.g., testing)
mkdir -p kubernetes/overlays/testing

# Copy from existing overlay
cp kubernetes/overlays/staging/kustomization.yaml kubernetes/overlays/testing/

# Modify for testing environment
vi kubernetes/overlays/testing/kustomization.yaml
```

## 🔗 Related Files

- [Kubernetes Guide](../../DOCKER_KUBERNETES_GUIDE.md)
- [Quick Reference](../../DOCKER_K8S_QUICK_REFERENCE.md)
- [Base Configuration](../deployment.yaml)
- [Service Configuration](../service.yaml)
- [ConfigMap](../configmap.yaml)

## 📖 References

- [Kustomize Documentation](https://kustomize.io/)
- [Kubernetes Overlays Pattern](https://kubernetes.io/docs/concepts/management/overview/)
