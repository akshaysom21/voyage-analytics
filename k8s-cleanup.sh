#!/bin/bash
# Kubernetes cleanup script
# Removes all Voyage Analytics resources from the cluster

set -e

# Default namespace
NAMESPACE="${1:-voyage-analytics}"

echo "========================================="
echo "Kubernetes Cleanup Script"
echo "========================================="
echo "Namespace: $NAMESPACE"
echo "========================================="
echo ""
echo "  WARNING: This will delete all resources in namespace: $NAMESPACE"
read -p "Continue? (yes/no) " -n 3 -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo ""
echo "Deleting resources..."

# Delete deployment
echo "Deleting deployment..."
kubectl delete deployment voyage-analytics -n "$NAMESPACE" --ignore-not-found=true
echo " -> Deployment deleted"

# Delete service
echo "Deleting service..."
kubectl delete service voyage-analytics-service -n "$NAMESPACE" --ignore-not-found=true
echo " -> Service deleted"

# Delete configmap
echo "Deleting configmap..."
kubectl delete configmap voyage-analytics-config -n "$NAMESPACE" --ignore-not-found=true
echo " -> ConfigMap deleted"

# Wait for pods to terminate
echo ""
echo "Waiting for pods to terminate..."
kubectl wait --for=delete pod -l app=voyage-analytics -n "$NAMESPACE" --timeout=30s 2>/dev/null || true
echo " -> Pods terminated"

# Optional: delete namespace
read -p "Delete namespace '$NAMESPACE'? (yes/no) " -n 3 -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Deleting namespace..."
    kubectl delete namespace "$NAMESPACE"
    echo " -> Namespace deleted"
fi

echo ""
echo "========================================="
echo "Cleanup Complete!"
echo "========================================="
