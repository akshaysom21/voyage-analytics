# Docker Configuration Guide

This directory contains Docker configuration files for containerizing the Voyage Analytics application.

## 📁 Files Overview

### Dockerfile
Multi-stage Docker configuration optimized for Python applications:
- **Base Image**: `python:3.11-slim` (lightweight, secure)
- **User**: Non-root user `appuser` (security best practice)
- **Port**: 5000 (Flask API)
- **Server**: Gunicorn (production WSGI server)
- **Health Check**: HTTP endpoint at `/health`

### docker-compose.yml
Local development environment setup:
- Single service: `flight-api`
- Port mapping: `5000:5000`
- Volume mounts for models and data
- Health checks configured
- Automatic restart on failure

### .dockerignore
Optimized build context to exclude:
- Git files
- Python cache and virtual environments
- IDE configurations
- Documentation and notebooks
- Unnecessary files (reduces build size)

## 🚀 Quick Start

### Build Image
```bash
# Using script
./docker-build.sh 1.0.0

# Manual build
docker build -f docker/Dockerfile -t voyage-analytics:1.0.0 .
```

### Run Locally
```bash
# Using Docker Compose (recommended)
./docker-compose-start.sh

# Manual run
docker run -d -p 5000:5000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/data:/app/data:ro \
  -e FLASK_ENV=production \
  voyage-analytics:1.0.0
```

### Test Container
```bash
# Health check
curl http://localhost:5000/health

# API test
curl http://localhost:5000/

# View logs
docker logs -f voyage-flight-api
```

## 📋 Dockerfile Details

### Base Image
```dockerfile
FROM python:3.11-slim
```
- **python:3.11**: Latest Python 3.11 version
- **slim**: Minimal image (only essential packages)
- **Benefits**: Small size, fast pulls, fewer vulnerabilities

### Security Measures
```dockerfile
RUN useradd -m -u 1000 appuser
...
USER appuser
```
- Non-root user prevents container escapes
- Fixed UID (1000) for consistency
- Proper file ownership

### Dependencies
```dockerfile
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
```
- Installs minimal OS dependencies (gcc for compilation)
- Cleans package manager cache (reduces image size)
- Installs Python packages without cache

### Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
```
- Checks every 30 seconds
- Fails if unresponsive for 10 seconds
- Allows 15 seconds startup time
- Fails after 3 consecutive failures

### Entry Point
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--chdir", "app", "app:app"]
```
- Starts Gunicorn WSGI server
- Listens on all interfaces (:5000)
- 4 worker processes for concurrency
- 120-second timeout for long-running requests

## 🔧 Configuration

### Environment Variables
Available in docker-compose.yml:
- `FLASK_ENV`: Application environment (production/development)

### Volume Mounts
- `/app/models`: Read-only access to trained models
- `/app/data`: Read-only access to training data
- Both mounted as read-only (`:ro`) for safety

## 📊 Image Optimization

### Current Size
Typical image size: ~600-700 MB

### Size Optimization Tips
```dockerfile
# Multi-stage build example (future enhancement)
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```
Could reduce size to 400-500 MB.

### Build Caching Strategy
- Requirements change infrequently → separate layer
- Source code changes frequently → later layer
- Leverages Docker layer caching for faster builds

## 🐳 Docker Compose

### Service: flight-api

**Building**:
```yaml
build:
  context: ..
  dockerfile: docker/Dockerfile
```
- Builds from Dockerfile in docker/ directory
- Build context is project root

**Networking**:
```yaml
ports:
  - "5000:5000"
```
- Maps container port 5000 to host port 5000

**Storage**:
```yaml
volumes:
  - ../models:/app/models:ro
  - ../data:/app/data:ro
```
- Mounts models and data directories
- Read-only (`:ro`) prevents accidental modifications

**Health Monitoring**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```
- Regularly checks service health
- Automatically marks container unhealthy if failures exceed threshold

**Restart Policy**:
```yaml
restart: unless-stopped
```
- Automatically restarts on failure
- Doesn't restart if manually stopped

## 🚀 Production Deployment

### Before Pushing to Registry

```bash
# Build with production tag
docker build -f docker/Dockerfile -t your-registry.com/voyage-analytics:1.0.0 .

# Test locally
docker run -d -p 5000:5000 your-registry.com/voyage-analytics:1.0.0

# Push to registry
docker push your-registry.com/voyage-analytics:1.0.0
```

### Registry Options
- **Docker Hub**: `docker.io/username/voyage-analytics`
- **AWS ECR**: `123456789.dkr.ecr.us-east-1.amazonaws.com/voyage-analytics`
- **Google GCR**: `gcr.io/project-id/voyage-analytics`
- **Azure ACR**: `myregistry.azurecr.io/voyage-analytics`
- **Private**: Self-hosted registry

### Image Versions
- **Semantic Versioning**: `1.0.0`, `1.1.0`, `2.0.0`
- **Release Candidate**: `1.0.0-rc1`, `1.0.0-rc2`
- **Development**: `latest`, `dev`, `main`
- **Branch**: `feature-xyz`, `hotfix-123`

## 🔍 Debugging

### View Dockerfile Changes
```bash
# Check what changed in build
docker history voyage-analytics:1.0.0

# Inspect image
docker inspect voyage-analytics:1.0.0

# Check image layers
docker inspect -f "{{json .RootFS.Layers}}" voyage-analytics:1.0.0 | jq
```

### Debug Inside Container
```bash
# Interactive shell
docker run -it --rm voyage-analytics:1.0.0 /bin/bash

# Execute command
docker exec -it <container-id> bash

# Check network
docker exec <container-id> curl http://localhost:5000/health

# Check environment
docker exec <container-id> env
```

### Common Issues

**Port Already in Use**
```bash
# Kill process on port
docker kill <container-id>

# Or find and kill process
lsof -i :5000
kill -9 <pid>
```

**Out of Disk Space**
```bash
# Clean up images and containers
docker system prune -a

# Remove specific image
docker rmi voyage-analytics:1.0.0
```

**Slow Pulls**
```bash
# Check if pulling from correct registry
docker pull voyage-analytics:1.0.0  # Searches Docker Hub
docker pull your-registry.com/voyage-analytics:1.0.0
```

## 📚 Best Practices

### Application Code
- ✅ Use gunicorn for production (not Flask dev server)
- ✅ Proper error handling and logging
- ✅ Health check endpoint required
- ✅ Configuration via environment variables

### Docker
- ✅ Use specific base image versions (not `latest`)
- ✅ Non-root user for security
- ✅ Multi-stage builds for smaller images
- ✅ Health checks configured
- ✅ Proper signal handling for graceful shutdown

### Registry
- ✅ Use semantic versioning for production
- ✅ Scan images for vulnerabilities
- ✅ Private registry for proprietary code
- ✅ Clean up old images regularly

### Kubernetes Integration
- ✅ Image pull policy: `IfNotPresent` for dev, `Always` for production
- ✅ Resource requests and limits defined
- ✅ Liveness and readiness probes
- ✅ Health check endpoint

## 🔗 Related Documentation

- [DOCKER_KUBERNETES_GUIDE.md](../DOCKER_KUBERNETES_GUIDE.md) - Complete guide
- [DOCKER_K8S_QUICK_REFERENCE.md](../DOCKER_K8S_QUICK_REFERENCE.md) - Quick commands
- [kubernetes/README.md](../kubernetes/README.md) - Kubernetes deployment
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask guide
- [Gunicorn Documentation](https://gunicorn.org/) - Gunicorn WSGI

## 📖 External Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Python Docker Best Practices](https://snyk.io/blog/10-docker-image-security-best-practices/)
- [Container Scanning](https://docs.docker.com/desktop/scan/)
- [Docker Security](https://docs.docker.com/engine/security/)
