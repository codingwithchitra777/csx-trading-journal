#!/bin/bash
# Setup secrets in Google Cloud Secret Manager

# 1. Create secret for Telegram bot token
echo -n "7805780868:AAESFXGhd4tGS9jEpFcSrifvLqTf30m3HcE" | \
  gcloud secrets create telegram-bot-token --data-file=-

# 2. Create secret for Firebase service account key
gcloud secrets create firebase-service-account --data-file=firebase/serviceAccountKey.json

# 3. Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding telegram-bot-token \
  --member="serviceAccount:codingwithchitra-eacf9@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding firebase-service-account \
  --member="serviceAccount:codingwithchitra-eacf9@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "✅ Secrets created successfully"
