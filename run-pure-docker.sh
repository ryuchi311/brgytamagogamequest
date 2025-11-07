#!/bin/bash
# Pure Docker run script (no docker-compose) for BRGY TAMAGO Quest Hub

set -e

IMAGE_NAME="brgy-tamago-quest-hub"
CONTAINER_NAME="brgy-tamago-api"
PORT=8080

echo "🚀 Running BRGY TAMAGO Quest Hub with pure Docker on port ${PORT}..."
echo "======================================================================"
echo ""

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  Warning: .env file not found. Using defaults..."
    export SECRET_KEY="dev-secret-key-change-in-production"
fi

# Stop and remove existing container
echo "🛑 Stopping existing container (if any)..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

# Build the image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME} \
  --build-arg REQUIREMENTS_FILE=requirements-backend.txt \
  .

echo ""
echo "🚀 Starting container..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p ${PORT}:${PORT} \
  -e PORT=${PORT} \
  -e DATABASE_URL="${DATABASE_URL:-}" \
  -e SUPABASE_URL="${SUPABASE_URL:-}" \
  -e SUPABASE_KEY="${SUPABASE_KEY:-}" \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
  -e TWITTER_BEARER_TOKEN="${TWITTER_BEARER_TOKEN:-}" \
  -e TWITTER_API_KEY="${TWITTER_API_KEY:-}" \
  -e TWITTER_API_SECRET="${TWITTER_API_SECRET:-}" \
  -e TWITTER_CLIENT_ID="${TWITTER_CLIENT_ID:-}" \
  -e TWITTER_CLIENT_SECRET="${TWITTER_CLIENT_SECRET:-}" \
  -v "$(pwd)/frontend:/app/frontend" \
  --restart unless-stopped \
  ${IMAGE_NAME}

# Wait for container to start
echo ""
echo "⏳ Waiting for container to start..."
sleep 3

# Check if container is running
if docker ps | grep -q ${CONTAINER_NAME}; then
    echo ""
    echo "✅ BRGY TAMAGO Quest Hub is running!"
    echo "======================================================================"
    echo ""
    echo "🌐 Access the application:"
    echo "   Frontend: http://localhost:${PORT}"
    echo "   API: http://localhost:${PORT}/api"
    echo "   Health: http://localhost:${PORT}/health"
    echo ""
    echo "📊 View logs:"
    echo "   docker logs -f ${CONTAINER_NAME}"
    echo ""
    echo "🛑 Stop the application:"
    echo "   docker stop ${CONTAINER_NAME}"
    echo ""
    echo "🗑️  Remove the container:"
    echo "   docker rm ${CONTAINER_NAME}"
    echo ""
    
    # Show initial logs
    echo "📋 Initial logs:"
    echo "----------------------------------------------------------------------"
    docker logs ${CONTAINER_NAME}
else
    echo ""
    echo "❌ Failed to start container. Check logs:"
    docker logs ${CONTAINER_NAME}
    exit 1
fi
