$ErrorActionPreference='Continue'
Write-Output '=== gh cli ==='
if (Get-Command gh -ErrorAction SilentlyContinue) { gh --version 2>&1 | Select-Object -First 1 } else { 'GH CLI NOT INSTALLED' }
Write-Output '=== gh auth status ==='
gh auth status 2>&1
Write-Output '=== git identity ==='
git config --global user.name 2>&1
git config --global user.email 2>&1
Write-Output '=== existing remotes on highwater ==='
git -C 'C:\Users\brian\Projects\highwater' remote -v 2>&1
Write-Output '=== done ==='
