# Cloud Run Deployment Guide - BRGY TAMAGO Quest Hub

## Prerequisites

1. **Google Cloud Project**
   - Active GCP project with billing enabled
   - Cloud Run API enabled
   - Cloud Build API enabled
   - Secret Manager API enabled

2. **Local Setup**
   ```bash
   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   
   # Login to Google Cloud
   gcloud auth login
   
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   ```

## Environment Setup

### 1. Create Secrets in Google Cloud Secret Manager

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create secrets for sensitive data
echo -n "your-database-url" | gcloud secrets create database-url --data-file=-
echo -n "your-supabase-url" | gcloud secrets create supabase-url --data-file=-
echo -n "your-supabase-key" | gcloud secrets create supabase-key --data-file=-
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
echo -n "your-telegram-bot-token" | gcloud secrets create telegram-bot-token --data-file=-
echo -n "your-twitter-bearer-token" | gcloud secrets create twitter-bearer-token --data-file=-
echo -n "your-twitter-api-key" | gcloud secrets create twitter-api-key --data-file=-
echo -n "your-twitter-api-secret" | gcloud secrets create twitter-api-secret --data-file=-
echo -n "your-twitter-client-id" | gcloud secrets create twitter-client-id --data-file=-
echo -n "your-twitter-client-secret" | gcloud secrets create twitter-client-secret --data-file=-

# Grant Cloud Run service account access to secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Quick Deployment

### Option 1: Using Deployment Script (Recommended)

```bash
# Set environment variables
export GCLOUD_PROJECT_ID="your-project-id"
export GCLOUD_REGION="us-central1"  # or your preferred region

# Run deployment script
./deploy-cloudrun.sh
```

### Option 2: Manual Deployment

```bash
# Build and push Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/brgy-tamago-quest-hub:latest

# Deploy to Cloud Run
gcloud run deploy brgy-tamago-quest-hub \
  --image=gcr.io/YOUR_PROJECT_ID/brgy-tamago-quest-hub:latest \
  --platform=managed \
  --region=us-central1 \
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
  --set-secrets="DATABASE_URL=database-url:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,SECRET_KEY=secret-key:latest,TELEGRAM_BOT_TOKEN=telegram-bot-token:latest"
```

## Configuration Details

### Port Configuration
- **Cloud Run PORT**: 8080 (automatically set by Cloud Run)
- **Application**: Reads from `PORT` environment variable
- **Startup Script**: `start-server.sh` handles port binding

### Resource Limits
- **CPU**: 2 vCPUs (boosted during startup)
- **Memory**: 2 GiB
- **Timeout**: 300 seconds (5 minutes)
- **Concurrency**: 80 requests per container
- **Scaling**: 0-10 instances (auto-scaling)

### Health Checks
- **Endpoint**: `/health`
- **Startup Probe**: 240s timeout, 10s interval
- **Liveness Probe**: 10s interval

## Troubleshooting

### Issue: Container fails to start

**Solution 1: Check PORT variable**
```bash
# Verify PORT is set to 8080
gcloud run services describe brgy-tamago-quest-hub \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

**Solution 2: Check logs**
```bash
# View recent logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=brgy-tamago-quest-hub' \
  --limit=50 \
  --format=json
```

**Solution 3: Test locally with PORT=8080**
```bash
# Build locally
docker build -t brgy-tamago-test .

# Run with PORT=8080
docker run -p 8080:8080 -e PORT=8080 brgy-tamago-test
```

### Issue: Timeout during deployment

**Solution: Increase timeout**
```bash
gcloud run services update brgy-tamago-quest-hub \
  --region=us-central1 \
  --timeout=600
```

### Issue: Memory errors

**Solution: Increase memory**
```bash
gcloud run services update brgy-tamago-quest-hub \
  --region=us-central1 \
  --memory=4Gi
```

## Monitoring

### View Service Status
```bash
gcloud run services describe brgy-tamago-quest-hub \
  --region=us-central1
```

### Stream Logs
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=brgy-tamago-quest-hub"
```

### Check Metrics
```bash
# Open Cloud Console Metrics
gcloud run services describe brgy-tamago-quest-hub \
  --region=us-central1 \
  --format="value(status.url)"
```

## Post-Deployment

### Update Telegram Bot Webhook (if using webhooks)
```bash
# Get your Cloud Run URL
SERVICE_URL=$(gcloud run services describe brgy-tamago-quest-hub \
  --region=us-central1 \
  --format="value(status.url)")

# Update Telegram webhook
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${SERVICE_URL}/webhook"
```

### Test the Deployment
```bash
# Health check
curl https://your-service-url.run.app/health

# API test
curl https://your-service-url.run.app/api/quests
```

## CI/CD Integration

For automated deployments, create `.github/workflows/deploy-cloudrun.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy to Cloud Run
        run: ./deploy-cloudrun.sh
        env:
          GCLOUD_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          GCLOUD_REGION: us-central1
```

## Cost Optimization

### Reduce Idle Costs
```bash
# Set min instances to 0 (already configured)
gcloud run services update brgy-tamago-quest-hub \
  --region=us-central1 \
  --min-instances=0
```

### Adjust Resources Based on Usage
```bash
# Lower resources for testing/staging
gcloud run services update brgy-tamago-quest-hub \
  --region=us-central1 \
  --memory=512Mi \
  --cpu=1
```

## Support

For issues specific to Cloud Run deployment, check:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- Project Issues: https://github.com/ryuchi311/BT-GameHub/issues
