# Cloud Deployment Checklist

- [x] gcloud installed
- [x] Logged into Google account
- [ ] Billing enabled
- [x] Project selected (`red-tag-agentic-2026-0815`)
- [ ] APIs enabled
- [ ] Firestore created
- [ ] Pub/Sub topics created
- [ ] Service accounts created
- [ ] Cloud Run API deployed
- [ ] Cloud Run Worker deployed
- [ ] Pub/Sub push authentication tested
- [ ] Duplicate action test passed
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
- [ ] Docker Desktop engine running (not required when Cloud Build builds the image)
