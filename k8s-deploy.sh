#!/bin/bash
# Kubernetes deployment script
# Usage: ./k8s-deploy.sh [namespace] [image-tag]

set -e

# Default values
NAMESPACE="${1:-voyage-analytics}"
IMAGE_TAG="${2:-1.0.0}"
K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/kubernetes" && pwd)"

echo "========================================="
echo "Kubernetes Deployment Script"
echo "========================================="
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"
echo "Kubernetes Dir: $K8S_DIR"
echo "========================================="

# Create namespace if it doesn't exist
echo ""
echo "Creating namespace (if doesn't exist)..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
echo " -> Namespace ready: $NAMESPACE"

# Set namespace as default context
echo ""
echo "Setting default namespace..."
kubectl config set-context --current --namespace="$NAMESPACE"
echo " -> Default namespace set to: $NAMESPACE"

# Apply ConfigMap
echo ""
echo "Deploying ConfigMap..."
kubectl apply -f "$K8S_DIR/configmap.yaml" -n "$NAMESPACE"
echo " -> ConfigMap deployed"

# Apply Deployment
echo ""
echo "Deploying Application..."
kubectl apply -f "$K8S_DIR/deployment.yaml" -n "$NAMESPACE"
echo " -> Deployment deployed"

# Apply Service
echo ""
echo "Deploying Service..."
kubectl apply -f "$K8S_DIR/service.yaml" -n "$NAMESPACE"
echo " -> Service deployed"

# Wait for deployment to be ready
echo ""
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/voyage-analytics -n "$NAMESPACE" --timeout=5m
echo " -> Deployment is ready"

# Display status
echo ""
echo "========================================="
echo "Deployment Status"
echo "========================================="
echo ""
echo "Deployments:"
kubectl get deployment -n "$NAMESPACE"

echo ""
echo "Pods:"
kubectl get pods -n "$NAMESPACE" -o wide

echo ""
echo "Services:"
kubectl get service -n "$NAMESPACE"

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Port forward to access the service locally:"
echo "   kubectl port-forward -n $NAMESPACE svc/voyage-analytics-service 5000:80"
echo ""
echo "2. Test the API:"
echo "   curl http://localhost:5000/health"
echo ""
echo "3. View logs:"
echo "   kubectl logs -n $NAMESPACE -l app=voyage-analytics -f"
echo ""
echo "4. Scale deployment:"
echo "   kubectl scale deployment voyage-analytics -n $NAMESPACE --replicas=3"
echo ""
