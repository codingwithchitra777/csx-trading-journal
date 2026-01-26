# Run these commands to grant permissions

# Grant Firebase Admin role
gcloud projects add-iam-policy-binding codingwithchitra-eacf9 \
  --member="serviceAccount:firebase-adminsdk-fbsvc@codingwithchitra-eacf9.iam.gserviceaccount.com" \
  --role="roles/firebase.admin"

# Grant Cloud Datastore User role
gcloud projects add-iam-policy-binding codingwithchitra-eacf9 \
  --member="serviceAccount:firebase-adminsdk-fbsvc@codingwithchitra-eacf9.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# If using Firestore in Native mode, also grant:
gcloud projects add-iam-policy-binding codingwithchitra-eacf9 \
  --member="serviceAccount:firebase-adminsdk-fbsvc@codingwithchitra-eacf9.iam.gserviceaccount.com" \
  --role="roles/datastore.owner"
