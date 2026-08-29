$ErrorActionPreference = 'Continue'
Write-Output '=== billing accounts on this login ==='
gcloud billing accounts list --format="value(name,displayName,open,masterAccount)" 2>&1
Write-Output '=== is the project linked to billing? ==='
gcloud billing projects describe highwater-473921 --format="value(billingEnabled,billingAccountName)" 2>&1
Write-Output '=== project display name vs id ==='
gcloud projects describe highwater-473921 --format="value(projectId,name,projectNumber)" 2>&1
Write-Output '=== existing cloud run services ==='
gcloud run services list --project=highwater-473921 --format="value(metadata.name,status.url)" 2>&1
Write-Output '=== done ==='
