# Google Cloud Deployment Guide

## Prerequisites
1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project codingwithchitra-eacf9`

## Initial Setup

### Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Deploy Methods

### Method 1: Manual Deploy (Quick Test)
```bash
# Build and submit to Google Container Registry
gcloud builds submit --tag gcr.io/codingwithchitra-eacf9/csx-trading-journal

# Deploy to Cloud Run
gcloud run deploy csx-trading-journal \
  --image gcr.io/codingwithchitra-eacf9/csx-trading-journal \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 1 \
  --timeout 300s
```

### Method 2: Automated Deploy (Recommended)
```bash
# Deploy using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml
```

### Method 3: Continuous Deployment from GitHub
```bash
# Connect GitHub repository
gcloud builds triggers create github \
  --repo-name=csx-trading-journal \
  --repo-owner=codingwithchitra777 \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## View Logs
```bash
# View Cloud Run logs
gcloud run services logs read csx-trading-journal --region us-central1

# Follow logs in real-time
gcloud run services logs tail csx-trading-journal --region us-central1
```

## Update Service
```bash
# Redeploy after changes
gcloud builds submit --config cloudbuild.yaml
```

## Cost Optimization
- Free tier: 2M requests/month, 180K vCPU-seconds, 360K GiB-seconds
- Bot runs 24/7 within free tier with current settings
- Scales to zero when idle (min-instances=0)

## Environment Variables (if needed)
```bash
gcloud run services update csx-trading-journal \
  --region us-central1 \
  --set-env-vars "KEY=VALUE"
```
