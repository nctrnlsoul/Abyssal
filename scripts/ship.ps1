$ErrorActionPreference='Continue'
Set-Location -LiteralPath $PSScriptRoot\..
git add -A
git commit -F .commitmsg 2>&1 | Select-Object -First 2
git push 2>&1 | Select-Object -Last 1
Write-Output ''
& .\deploy.ps1
