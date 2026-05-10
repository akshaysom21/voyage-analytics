#!/bin/bash
# Docker build and push script
# Usage: ./docker-build.sh [image-tag] [registry-url]

set -e

# Default values
IMAGE_TAG="${1:-1.0.0}"
REGISTRY="${2}"
IMAGE_NAME="voyage-analytics"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Docker Build & Push Script"
echo "========================================="
echo "Project Root: $PROJECT_ROOT"
echo "Image Name: $IMAGE_NAME"
echo "Image Tag: $IMAGE_TAG"
if [ -n "$REGISTRY" ]; then
    echo "Registry: $REGISTRY"
    FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
else
    FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"
    echo "Local build (no registry)"
fi
echo "========================================="

# Build image
echo ""
echo "Building Docker image..."
docker build -f "$PROJECT_ROOT/docker/Dockerfile" \
    -t "$FULL_IMAGE" \
    "$PROJECT_ROOT"

echo "-> Image built successfully: $FULL_IMAGE"

# Check image
echo ""
echo "Image info:"
docker images | grep "$IMAGE_NAME" | head -1

# Push to registry if provided
if [ -n "$REGISTRY" ]; then
    echo ""
    echo "Pushing to registry..."
    docker push "$FULL_IMAGE"
    echo "-> Image pushed successfully to: $FULL_IMAGE"
else
    echo ""
    echo " To push to a registry, run:"
    echo "  docker tag $FULL_IMAGE <registry>/$FULL_IMAGE"
    echo "  docker push <registry>/$FULL_IMAGE"
fi

echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="
