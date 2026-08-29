# Deploy the KEYLESS console to Cloud Run.
#
# Two omissions in a suggested deploy command that this script exists to close,
# both flagged by adversarial review on the previous project:
#
#   1. NO --service-account means the revision runs as the Compute Engine
#      default service account, which carries project EDITOR. Anything that can
#      reach the metadata server on that container can mint a token with broad
#      project rights, from a PUBLIC unauthenticated URL. This creates a
#      dedicated account with NO roles at all.
#
#   2. NO --max-instances means no bound on concurrent containers, so a traffic
#      spike is an unbounded bill. --max-instances IS the spend cap.
#
# No GOOGLE_API_KEY is set on the service, deliberately. The console serves a
# recorded run and cannot call a model, so a visitor cannot spend money.

$ErrorActionPreference = 'Stop'

# ANCHOR THE WORKING DIRECTORY FIRST.
#
# The first run of this script omitted it. PowerShell launched with its default
# cwd, `--source .` therefore resolved to C:\Windows\System32, and gcloud spent
# two minutes uploading the Windows system directory before crashing on
# catroot2\edb.log. It also silently fell back to Buildpacks, because there was
# no Dockerfile where it was looking.
#
# A relative --source in a script that does not pin its own location is a trap,
# and the failure mode is "uploads your operating system", not "file not found".
Set-Location -LiteralPath $PSScriptRoot

$PROJECT  = 'highwater-473921'
$REGION   = 'us-central1'
$SERVICE  = 'abyssal'
$SA_NAME  = 'abyssal-run'
$SA_EMAIL = "$SA_NAME@$PROJECT.iam.gserviceaccount.com"

function Assert-LastExit($what) {
  # $ErrorActionPreference does NOT stop a failed native command. Checking
  # $LASTEXITCODE is the only thing that does, and skipping it is how a broken
  # build gets reported as a successful deploy.
  if ($LASTEXITCODE -ne 0) { throw "$what failed with exit code $LASTEXITCODE" }
}

Write-Output "=== project ==="
gcloud config set project $PROJECT | Out-Null
Assert-LastExit 'gcloud config set project'

Write-Output "=== service account with NO roles ==="
$existing = gcloud iam service-accounts list --filter="email:$SA_EMAIL" --format='value(email)' 2>$null
if (-not $existing) {
  gcloud iam service-accounts create $SA_NAME `
    --display-name='Abyssal Cloud Run (no roles)' `
    --description='Runs the keyless public console. Intentionally holds no IAM roles.'
  Assert-LastExit 'service account create'
} else {
  Write-Output "  exists: $SA_EMAIL"
}

Write-Output "=== preflight ==="
# Fail loudly rather than let gcloud fall back to Buildpacks, which would ignore
# the Dockerfile, install the FULL requirements.txt including the agent
# framework, and guess an entrypoint.
foreach ($required in @('Dockerfile', '.dockerignore', 'requirements-web.txt',
                        'web/app.py', 'docs/recorded-run.json',
                        'data/reef_window_a.wav', 'data/hab_forecast_cellcounts.png')) {
  if (-not (Test-Path -LiteralPath $required)) {
    throw "missing $required in $PWD. Refusing to deploy from the wrong directory."
  }
}
Write-Output ("  cwd: " + $PWD)
Write-Output "  all required files present"

Write-Output "=== deploy from source ==="
# --source builds with Cloud Build and pushes to Artifact Registry in one step.
# gcr.io is the legacy Container Registry path; this uses the current one.
gcloud run deploy $SERVICE `
  --source . `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --service-account $SA_EMAIL `
  --max-instances 3 `
  --memory 512Mi `
  --cpu 1 `
  --concurrency 40 `
  --timeout 60 `
  --set-env-vars 'ABYSSAL_TRUSTED_PROXY_HOPS=0' `
  --quiet
Assert-LastExit 'gcloud run deploy'

$url = gcloud run services describe $SERVICE --region $REGION --format='value(status.url)'
Assert-LastExit 'describe service'
Write-Output ""
Write-Output "LIVE URL: $url"
Write-Output ""
Write-Output "=== verifying the deployed surface ==="
$ProgressPreference = 'SilentlyContinue'
foreach ($p in @('/health', '/', '/api/run', '/api/bands', '/api/waveform', '/api/source-image')) {
  try {
    $r = Invoke-WebRequest -Uri ($url + $p) -UseBasicParsing -TimeoutSec 45
    Write-Output ("  [{0}] {1}  {2} bytes" -f $r.StatusCode, $p, $r.RawContentLength)
  } catch {
    Write-Output ("  [FAIL] {0}  {1}" -f $p, $_.Exception.Message)
  }
}
Write-Output ""
Write-Output "Set a Cloud Billing budget on $PROJECT if you have not already."
