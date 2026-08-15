#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 PROJECT_ID [REGION]"
  exit 2
fi

PROJECT_ID="$1"
REGION="${2:-us-central1}"
REPOSITORY="red-tag"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/red-tag:latest"

gcloud config set project "${PROJECT_ID}"
gcloud services enable \
  run.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

if ! gcloud artifacts repositories describe "${REPOSITORY}" --location "${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format docker \
    --location "${REGION}"
fi

gcloud builds submit --tag "${IMAGE}" .

echo "Image built: ${IMAGE}"
echo "Use deploy_gcp.ps1 on Windows for the complete IAM, Firestore, Cloud Run, Pub/Sub, and DLQ deployment."
