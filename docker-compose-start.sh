#!/bin/bash
# Local Docker Compose setup script
# Starts the application locally using Docker Compose

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"

echo "========================================="
echo "Docker Compose Startup Script"
echo "========================================="
echo "Project Root: $PROJECT_ROOT"
echo "Compose File: $COMPOSE_FILE"
echo "========================================="

# Check if Docker is running
echo ""
echo "Checking Docker daemon..."
if ! docker ps > /dev/null 2>&1; then
    echo " -> Docker daemon is not running. Please start Docker."
    exit 1
fi
echo " -> Docker is running"

# Build images
echo ""
echo "Building Docker image..."
docker-compose -f "$COMPOSE_FILE" build
echo " -> Image built successfully"

# Start services
echo ""
echo "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d
echo " -> Services started"

# Wait for service to be healthy
echo ""
echo "Waiting for service to be healthy..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo " -> Service is healthy"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts..."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo " -> Service failed to become healthy"
    docker-compose -f "$COMPOSE_FILE" logs
    exit 1
fi

# Display service info
echo ""
echo "========================================="
echo "Service Information"
echo "========================================="
echo ""
echo "Running Containers:"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Access the API:"
echo "   http://localhost:5000"
echo ""
echo "2. Check health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "3. View logs:"
echo "   docker-compose -f docker/docker-compose.yml logs -f flight-api"
echo ""
echo "4. Stop services:"
echo "   docker-compose -f docker/docker-compose.yml down"
echo ""
