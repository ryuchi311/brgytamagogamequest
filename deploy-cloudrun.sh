#!/bin/bash
# Cloud Run Deployment Script for BRGY TAMAGO Quest Hub

set -e

# Configuration
PROJECT_ID="${GCLOUD_PROJECT_ID}"
REGION="${GCLOUD_REGION:-us-central1}"
SERVICE_NAME="brgy-tamago-quest-hub"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying BRGY TAMAGO Quest Hub to Cloud Run"
echo "================================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
gcloud builds submit --tag "${IMAGE_NAME}:latest" \
  --project="${PROJECT_ID}" \
  --timeout=20m

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_NAME}:latest" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --port=8080 \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=10 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --cpu-boost \
  --no-cpu-throttling \
  --set-env-vars="PORT=8080" \
  --set-secrets="DATABASE_URL=database-url:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,SECRET_KEY=secret-key:latest,TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,TWITTER_BEARER_TOKEN=twitter-bearer-token:latest,TWITTER_API_KEY=twitter-api-key:latest,TWITTER_API_SECRET=twitter-api-secret:latest,TWITTER_CLIENT_ID=twitter-client-id:latest,TWITTER_CLIENT_SECRET=twitter-client-secret:latest"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URL:"
gcloud run services describe "${SERVICE_NAME}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.url)"
echo ""
echo "📊 View logs:"
echo "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}' --project=${PROJECT_ID} --limit=50 --format=json"
