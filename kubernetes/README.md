# Kubernetes Configuration Guide

This directory contains Kubernetes manifests for deploying the Voyage Analytics application.

## 📁 Directory Structure

```
kubernetes/
├── deployment.yaml          # Pod deployment configuration
├── service.yaml             # Service exposure configuration
├── configmap.yaml           # Application configuration
├── kustomization.yaml       # Base Kustomize configuration
└── overlays/
    ├── development/         # Development environment
    ├── staging/             # Staging environment
    └── production/          # Production environment
```

## 🎯 Quick Start

### Deploy to Kubernetes

```bash
# Option 1: Using deployment script (recommended)
./k8s-deploy.sh voyage-analytics 1.0.0

# Option 2: Manual deployment
kubectl apply -f kubernetes/

# Option 3: Using environment overlay
kubectl apply -k kubernetes/overlays/production

# Option 4: Using Kustomize
kustomize build kubernetes/ | kubectl apply -f -
```

### Verify Deployment

```bash
# Check deployment status
./k8s-test.sh voyage-analytics

# Or manually:
kubectl get all -l app=voyage-analytics
kubectl logs -l app=voyage-analytics -f
```

### Access Application

```bash
# Port forward
kubectl port-forward svc/voyage-analytics-service 5000:80

# Test API
curl http://localhost:5000/health
```

## 📋 Manifest Files

### deployment.yaml

Kubernetes Deployment object that manages pods running the API.

**Key Configuration**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voyage-analytics
spec:
  replicas: 2  # Number of pod copies
  selector:
    matchLabels:
      app: voyage-analytics
  template:
    # Pod specification
```

**Pod Specification**:
- **Container Name**: `flight-api`
- **Image**: `voyage-analytics:1.0.0`
- **Port**: 5000 (Flask API)
- **Image Pull Policy**: `IfNotPresent` (uses local image)

**Resource Allocation**:
```yaml
resources:
  requests:
    memory: "256Mi"    # Minimum required
    cpu: "250m"        # Minimum required
  limits:
    memory: "512Mi"    # Maximum allowed
    cpu: "500m"        # Maximum allowed
```

**Health Checks**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 20
  periodSeconds: 30
```
- Restarts unhealthy pods
- Waits 20 seconds before first check
- Checks every 30 seconds

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 15
  periodSeconds: 10
```
- Determines if pod is ready for traffic
- Waits 15 seconds before first check
- Checks every 10 seconds

**Security**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: false
```
- Runs as non-root user (user ID 1000)
- Prevents container escapes
- Filesystem remains writable (for logs)

### service.yaml

Kubernetes Service object that exposes the deployment.

**Type**: LoadBalancer
```yaml
kind: Service
metadata:
  name: voyage-analytics-service
spec:
  type: LoadBalancer
  selector:
    app: voyage-analytics
  ports:
  - protocol: TCP
    port: 80              # External port
    targetPort: 5000      # Container port
```

**How it works**:
- Exposes port 80 externally
- Routes traffic to port 5000 on pods
- LoadBalancer creates external IP (cloud environments)
- Local clusters may use NodePort or port-forward

**Service Types**:
- **ClusterIP**: Internal only (default)
- **NodePort**: External via node IP:port
- **LoadBalancer**: Cloud external IP (current)
- **ExternalName**: Routes to external DNS

### configmap.yaml

Kubernetes ConfigMap for application configuration.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voyage-analytics-config
data:
  FLASK_ENV: "production"
  API_VERSION: "1.0.0"
  MODEL_NAME: "Random Forest Regressor"
  WORKERS: "4"
  TIMEOUT: "120"
```

**Usage in Deployment**:
```yaml
envFrom:
- configMapRef:
    name: voyage-analytics-config
```

**Advantages**:
- Non-sensitive configuration management
- Easy to update without rebuilding image
- Reusable across multiple deployments
- Version controlled in git

**When to Update**:
- Change environment (dev/staging/prod)
- Update feature flags
- Adjust performance parameters
- Add new configuration variables

**When NOT to Use**:
- Sensitive data (use Secrets instead)
- Passwords, API keys, tokens
- Binary data

### kustomization.yaml

Base Kustomize configuration for managing Kubernetes manifests.

```yaml
namespace: voyage-analytics
commonLabels:
  app: voyage-analytics
resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml
images:
  - name: voyage-analytics
    newTag: 1.0.0
replicas:
  - name: voyage-analytics
    count: 2
```

**Benefits**:
- Template generation without preprocessing
- Image and replica patching
- Common labels and annotations
- Environment-specific overlays

## 🚀 Deployment Strategies

### Rolling Update (Default)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1           # Extra pods during update
    maxUnavailable: 0     # Never scale below replicas
```
- Gradual pod replacement
- No downtime
- Easy rollback

### Recreate
```yaml
strategy:
  type: Recreate
```
- Kills all pods, then starts new ones
- Simpler but has downtime
- Not recommended for production

## 📊 Resource Management

### Understanding Requests and Limits

**Requests** - Pod guaranteed to receive:
```yaml
resources:
  requests:
    cpu: "250m"      # 0.25 CPU cores
    memory: "256Mi"   # 256 Megabytes
```
- Kubernetes reserves this for the pod
- Used for scheduling decisions
- Pod can be evicted if cluster resources are low

**Limits** - Pod cannot exceed:
```yaml
resources:
  limits:
    cpu: "500m"       # 0.5 CPU cores max
    memory: "512Mi"    # 512 Megabytes max
```
- Pod throttled if CPU limit exceeded
- Pod killed if memory limit exceeded (OOMKilled)

### Sizing Guide

| Environment | Requests | Limits | Replicas |
|------------|----------|--------|----------|
| Dev | 250m/256Mi | 500m/512Mi | 1 |
| Staging | 500m/512Mi | 1000m/1Gi | 2 |
| Prod | 500m/512Mi | 1000m/1Gi | 3+ |

### Calculating Cluster Capacity

Example cluster with 3 nodes, each 4 CPU + 8Gi RAM:
```
Total: 12 CPU + 24Gi RAM
Reserved for system: ~1 CPU + 2Gi RAM per node = 3 CPU + 6Gi RAM
Usable: 9 CPU + 18Gi RAM

With 500m/512Mi per pod:
Max pods: min(9/0.5, 18/0.5) = 18 pods
```

## 🔄 Common Operations

### Scale Deployment
```bash
# Scale to 5 replicas
kubectl scale deployment voyage-analytics --replicas=5

# Check current replicas
kubectl get deployment voyage-analytics
```

### Update Image
```bash
# Update to new version
kubectl set image deployment/voyage-analytics \
  flight-api=voyage-analytics:1.1.0

# Monitor rollout
kubectl rollout status deployment/voyage-analytics

# View history
kubectl rollout history deployment/voyage-analytics

# Rollback if needed
kubectl rollout undo deployment/voyage-analytics
```

### Update Configuration
```bash
# Edit ConfigMap
kubectl edit configmap voyage-analytics-config

# Or apply new ConfigMap
kubectl apply -f kubernetes/configmap.yaml

# Restart pods to pick up new config
kubectl rollout restart deployment/voyage-analytics
```

### View Logs
```bash
# Logs from all pods
kubectl logs -l app=voyage-analytics -f

# Logs from specific pod
kubectl logs <POD_NAME> -f

# Previous logs (from crashed pod)
kubectl logs <POD_NAME> --previous
```

## 🔍 Monitoring & Debugging

### Check Pod Status
```bash
# List pods with details
kubectl get pods -l app=voyage-analytics -o wide

# Describe pod (detailed info)
kubectl describe pod <POD_NAME>

# Watch pod changes
kubectl get pods -l app=voyage-analytics -w
```

### Health Check Status
```bash
# View probe results in pod description
kubectl describe pod <POD_NAME> | grep -A 5 "Conditions"

# Check recent events
kubectl get events --sort-by='.lastTimestamp' | grep voyage
```

### Access Pod Interactive Shell
```bash
# Open bash session
kubectl exec -it <POD_NAME> -- /bin/bash

# Run single command
kubectl exec <POD_NAME> -- curl http://localhost:5000/health

# Run with pod environment variables
kubectl exec <POD_NAME> -- env
```

### Network Debugging
```bash
# Test service DNS
kubectl exec <POD_NAME> -- nslookup voyage-analytics-service

# Test endpoint directly
kubectl exec <POD_NAME> -- curl http://voyage-analytics-service/health

# Check iptables rules
kubectl exec <POD_NAME> -- iptables -L -n
```

## 🛡️ Security Best Practices

### Pod Security
- ✅ Non-root user (implemented)
- ✅ Read-only root filesystem (not implemented - optional)
- ✅ Resource limits set (implemented)

### Optional Enhancements

**Network Policies** (restrict traffic):
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: voyage-analytics-policy
spec:
  podSelector:
    matchLabels:
      app: voyage-analytics
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
```

**Pod Disruption Budgets** (high availability):
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: voyage-analytics-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: voyage-analytics
```

**Secrets** (for sensitive data):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: voyage-analytics-secrets
type: Opaque
data:
  api-key: <base64-encoded-key>
  password: <base64-encoded-password>
```

## 📚 Troubleshooting Guide

### Pod Stuck in Pending
```bash
kubectl describe pod <POD_NAME>
# Check: Insufficient CPU/Memory, PVC not available, Image not found
```

### CrashLoopBackOff
```bash
kubectl logs <POD_NAME> --previous
# Check: Application errors, missing dependencies, wrong command
```

### ImagePullBackOff
```bash
# Verify image exists
docker images | grep voyage-analytics

# Check image path in deployment.yaml
grep "image:" kubernetes/deployment.yaml

# Verify pull policy
grep "imagePullPolicy" kubernetes/deployment.yaml
```

### Service Not Accessible
```bash
# Check service exists
kubectl get service voyage-analytics-service

# Check endpoints
kubectl get endpoints voyage-analytics-service

# Check service selector matches pods
kubectl get pods --show-labels | grep app=voyage-analytics

# Check pod ports
kubectl get pod <POD_NAME> -o yaml | grep -A 2 "ports:"
```

### Health Check Failing
```bash
# Test endpoint manually
kubectl exec <POD_NAME> -- curl -v http://localhost:5000/health

# View health check config
kubectl get pod <POD_NAME> -o yaml | grep -A 10 "livenessProbe"

# Check pod logs around health check time
kubectl logs <POD_NAME> --timestamps=true | grep "GET /health"
```

## 🔗 Related Resources

- [Docker Guide](../docker/README.md)
- [Quick Reference](../DOCKER_K8S_QUICK_REFERENCE.md)
- [Full Guide](../DOCKER_KUBERNETES_GUIDE.md)
- [Kubernetes Overlays](./overlays/README.md)

## 📖 External Documentation

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Deployment Reference](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Service Reference](https://kubernetes.io/docs/concepts/services-networking/service/)
- [ConfigMap Reference](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Pod Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kustomize Documentation](https://kustomize.io/)
