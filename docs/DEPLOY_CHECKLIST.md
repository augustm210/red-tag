# Cloud Deployment Checklist

- [x] gcloud installed
- [x] Logged into Google account
- [x] Billing enabled
- [x] Project selected (`red-tag-agentic-2026-0815`)
- [x] APIs enabled
- [x] Firestore created
- [x] Pub/Sub topics created
- [x] Service accounts created
- [x] Cloud Run API deployed
- [x] Cloud Run Worker deployed
- [x] Pub/Sub push authentication tested
- [x] Duplicate action test passed in cloud
- [ ] DLQ test passed

## Local evidence

- [x] Python 3.12 virtual environment created
- [x] Google ADK 2.7 installed
- [x] Five-node ADK workflow imports successfully
- [x] API lifecycle test passed
- [x] SEV1 human approval gate test passed
- [x] High-risk action gate test passed
- [x] Duplicate delivery test passed
- [x] Duplicate action test passed
- [x] Vertex AI live call returned `RED_TAG_VERTEX_OK`
- [x] Five-node ADK live run returned all five agent authors
- [ ] Docker Desktop engine running (not required when Cloud Build builds the image)
