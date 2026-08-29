$ErrorActionPreference = 'Continue'
Write-Output '=== authenticated accounts ==='
gcloud auth list --format="value(account,status)" 2>&1
Write-Output '=== active config ==='
gcloud config list --format="value(core.project,core.account,run.region)" 2>&1
Write-Output '=== projects visible ==='
gcloud projects list --format="value(projectId,name)" 2>&1 | Select-Object -First 15
Write-Output '=== billing on highwater-473921 ==='
gcloud beta billing projects describe highwater-473921 --format="value(billingEnabled,billingAccountName)" 2>&1
Write-Output '=== enabled services (filtered) ==='
gcloud services list --enabled --project=highwater-473921 --format="value(config.name)" 2>&1 | Select-String -Pattern 'run|generativelanguage|aiplatform|artifactregistry|cloudbuild|secretmanager'
Write-Output '=== gemini models on the key ==='
$py = 'C:\Users\brian\Projects\highwater\.venv\Scripts\python.exe'
$env:GOOGLE_API_KEY = [Environment]::GetEnvironmentVariable('GOOGLE_API_KEY','User')
& $py -c "from google import genai; c=genai.Client(); ms=[m.name for m in c.models.list() if 'generateContent' in (m.supported_actions or [])]; print('total', len(ms)); print('\n'.join(sorted(x for x in ms if '3.5' in x or '3.6' in x or '3.7' in x)))" 2>&1
Write-Output '=== done ==='
