$ErrorActionPreference='Continue'
Set-Location -LiteralPath $PSScriptRoot\..
git add -A
git commit -F .commitmsg 2>&1 | Select-Object -First 3
git push 2>&1 | Select-Object -Last 1
Write-Output ''
Write-Output '=== redeploying ==='
& .\deploy.ps1
