[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z][a-z0-9-]{4,28}[a-z0-9]$')]
    [string]$ProjectId,

    [string]$Region = 'us-central1',
    [string]$Model = 'gemini-3.6-flash'
)

$ErrorActionPreference = 'Stop'
$Gcloud = (Get-Command gcloud.cmd -ErrorAction SilentlyContinue).Source
if (-not $Gcloud) {
    $Gcloud = (Get-Command gcloud -ErrorAction Stop).Source
}

function Invoke-Gcloud {
    & $Gcloud @args
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud failed: $($args -join ' ')"
    }
}

$Repository = 'red-tag'
$Image = "$Region-docker.pkg.dev/$ProjectId/$Repository/red-tag:latest"
$ApiService = 'red-tag-api'
$WorkerService = 'red-tag-worker'
$IncidentTopic = 'red-tag-incident-created'
$DeadLetterTopic = 'red-tag-dead-letter'
$Subscription = 'red-tag-worker-push'

Write-Host "Deploying Red Tag to project $ProjectId in $Region"
Invoke-Gcloud config set project $ProjectId

$BillingEnabled = & $Gcloud billing projects describe $ProjectId --format='value(billingEnabled)'
if ($LASTEXITCODE -ne 0 -or $BillingEnabled -ne 'True') {
    throw "Billing is not enabled for project $ProjectId."
}

Invoke-Gcloud services enable `
    run.googleapis.com `
    pubsub.googleapis.com `
    firestore.googleapis.com `
    aiplatform.googleapis.com `
    cloudbuild.googleapis.com `
    artifactregistry.googleapis.com

& $Gcloud artifacts repositories describe $Repository --location $Region *> $null
if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud artifacts repositories create $Repository `
        --repository-format docker `
        --location $Region `
        --description 'Red Tag container images'
}

& $Gcloud firestore databases describe --database='(default)' *> $null
if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud firestore databases create `
        --database='(default)' `
        --location $Region `
        --type firestore-native
}

foreach ($Account in @('red-tag-api', 'red-tag-worker', 'red-tag-pubsub')) {
    & $Gcloud iam service-accounts describe "$Account@$ProjectId.iam.gserviceaccount.com" *> $null
    if ($LASTEXITCODE -ne 0) {
        Invoke-Gcloud iam service-accounts create $Account --display-name $Account
    }
}

foreach ($Role in @('roles/datastore.user', 'roles/pubsub.publisher')) {
    Invoke-Gcloud projects add-iam-policy-binding $ProjectId `
        --member "serviceAccount:red-tag-api@$ProjectId.iam.gserviceaccount.com" `
        --role $Role `
        --condition=None
}
foreach ($Role in @('roles/datastore.user', 'roles/aiplatform.user')) {
    Invoke-Gcloud projects add-iam-policy-binding $ProjectId `
        --member "serviceAccount:red-tag-worker@$ProjectId.iam.gserviceaccount.com" `
        --role $Role `
        --condition=None
}

foreach ($Topic in @($IncidentTopic, $DeadLetterTopic)) {
    & $Gcloud pubsub topics describe $Topic *> $null
    if ($LASTEXITCODE -ne 0) {
        Invoke-Gcloud pubsub topics create $Topic
    }
}

Invoke-Gcloud builds submit --tag $Image .

$CommonEnv = "RED_TAG_ENVIRONMENT=cloud,RED_TAG_REPOSITORY_BACKEND=firestore,RED_TAG_GOOGLE_CLOUD_PROJECT=$ProjectId,GOOGLE_CLOUD_PROJECT=$ProjectId,GOOGLE_CLOUD_LOCATION=$Region,GOOGLE_GENAI_USE_VERTEXAI=true,RED_TAG_MODEL=$Model"

Invoke-Gcloud run deploy $WorkerService `
    --image $Image `
    --region $Region `
    --service-account "red-tag-worker@$ProjectId.iam.gserviceaccount.com" `
    --no-allow-unauthenticated `
    --set-env-vars "$CommonEnv,RED_TAG_SERVICE_ROLE=worker,RED_TAG_AGENT_MODE=adk,RED_TAG_DISPATCH_BACKEND=inline" `
    --memory 1Gi `
    --timeout 900 `
    --max-instances 10

Invoke-Gcloud run deploy $ApiService `
    --image $Image `
    --region $Region `
    --service-account "red-tag-api@$ProjectId.iam.gserviceaccount.com" `
    --allow-unauthenticated `
    --set-env-vars "$CommonEnv,RED_TAG_SERVICE_ROLE=api,RED_TAG_AGENT_MODE=local,RED_TAG_DISPATCH_BACKEND=pubsub,RED_TAG_INCIDENT_TOPIC=$IncidentTopic" `
    --memory 512Mi `
    --timeout 60 `
    --max-instances 10

$WorkerUrl = & $Gcloud run services describe $WorkerService --region $Region --format='value(status.url)'
if ($LASTEXITCODE -ne 0 -or -not $WorkerUrl) {
    throw 'Unable to resolve worker URL.'
}

Invoke-Gcloud run services add-iam-policy-binding $WorkerService `
    --region $Region `
    --member "serviceAccount:red-tag-pubsub@$ProjectId.iam.gserviceaccount.com" `
    --role roles/run.invoker

& $Gcloud pubsub subscriptions describe $Subscription *> $null
if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud pubsub subscriptions create $Subscription `
        --topic $IncidentTopic `
        --push-endpoint "$WorkerUrl/internal/pubsub/incidents" `
        --push-auth-service-account "red-tag-pubsub@$ProjectId.iam.gserviceaccount.com" `
        --ack-deadline 600 `
        --dead-letter-topic $DeadLetterTopic `
        --max-delivery-attempts 5
}

$ApiUrl = & $Gcloud run services describe $ApiService --region $Region --format='value(status.url)'
Write-Host "Red Tag API: $ApiUrl"
Write-Host "Red Tag Worker: $WorkerUrl"
Write-Host 'Deployment complete. Run the duplicate-delivery smoke test next.'
