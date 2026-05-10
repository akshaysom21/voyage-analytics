#!/bin/bash
# Kubernetes test and validation script
# Tests the deployment and validates it's working correctly

set -e

NAMESPACE="${1:-voyage-analytics}"
SERVICE_NAME="voyage-analytics-service"
TIMEOUT="${2:-300}"

echo "========================================="
echo "Kubernetes Deployment Test Script"
echo "========================================="
echo "Namespace: $NAMESPACE"
echo "Service: $SERVICE_NAME"
echo "Timeout: ${TIMEOUT}s"
echo "========================================="

# Check if namespace exists
echo ""
echo "Checking namespace..."
if ! kubectl get namespace "$NAMESPACE" > /dev/null 2>&1; then
    echo " -> Namespace '$NAMESPACE' does not exist"
    exit 1
fi
echo " -> Namespace exists: $NAMESPACE"

# Check deployment status
echo ""
echo "Checking deployment..."
if ! kubectl get deployment voyage-analytics -n "$NAMESPACE" > /dev/null 2>&1; then
    echo " -> Deployment 'voyage-analytics' not found"
    exit 1
fi
echo " -> Deployment exists"

# Check if pods are running
echo ""
echo "Checking pods..."
POD_COUNT=$(kubectl get pods -n "$NAMESPACE" -l app=voyage-analytics --field-selector=status.phase=Running -o jsonpath='{.items | length}')
if [ "$POD_COUNT" -eq 0 ]; then
    echo " -> No running pods found"
    echo ""
    echo "Pod status:"
    kubectl get pods -n "$NAMESPACE" -l app=voyage-analytics
    exit 1
fi
echo " -> $POD_COUNT pod(s) running"

# Check service
echo ""
echo "Checking service..."
if ! kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" > /dev/null 2>&1; then
    echo " -> Service '$SERVICE_NAME' not found"
    exit 1
fi
echo " -> Service exists: $SERVICE_NAME"

# Get service endpoints
echo ""
echo "Checking service endpoints..."
ENDPOINT_COUNT=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress | length}' 2>/dev/null || echo 0)
echo "  Load Balancer Endpoints: $ENDPOINT_COUNT"

# Try to access the API
echo ""
echo "Testing API endpoint..."
POD_NAME=$(kubectl get pods -n "$NAMESPACE" -l app=voyage-analytics -o jsonpath='{.items[0].metadata.name}')
echo "  Using pod: $POD_NAME"

# Port forward and test
kubectl port-forward -n "$NAMESPACE" "pod/$POD_NAME" 5000:5000 > /dev/null 2>&1 &
PF_PID=$!

# Wait for port forward to be ready
sleep 2

echo "  Testing /health endpoint..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo " -> Health check passed"
else
    echo " -> Health check failed"
    kill $PF_PID 2>/dev/null || true
    exit 1
fi

echo "  Testing /model/info endpoint..."
if curl -f http://localhost:5000/model/info > /dev/null 2>&1; then
    echo " -> Model info endpoint works"
else
    echo " -> Model info endpoint failed"
fi

# Clean up port forward
kill $PF_PID 2>/dev/null || true

# Check pod logs for errors
echo ""
echo "Checking pod logs for errors..."
ERROR_COUNT=$(kubectl logs -n "$NAMESPACE" -l app=voyage-analytics --tail=100 | grep -i "error\|exception" | wc -l)
if [ $ERROR_COUNT -eq 0 ]; then
    echo " -> No errors found in logs"
else
    echo " -> Found $ERROR_COUNT error(s) in logs"
fi

# Display summary
echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo " -> Namespace: $NAMESPACE"
echo " -> Deployment: voyage-analytics"
echo " -> Running Pods: $POD_COUNT"
echo " -> Service: $SERVICE_NAME"
echo " -> API Health: OK"
echo ""
echo "========================================="
echo "Deployment appears to be working correctly!"
echo "========================================="
echo ""
echo "To view logs:"
echo "  kubectl logs -n $NAMESPACE -l app=voyage-analytics -f"
echo ""
echo "To access the service:"
echo "  kubectl port-forward -n $NAMESPACE svc/$SERVICE_NAME 5000:80"
echo ""
