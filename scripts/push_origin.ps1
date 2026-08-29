$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'

Write-Output '=== current branch ==='
git branch --show-current 2>&1

Write-Output '=== rename to main (GitHub default) ==='
git branch -M main 2>&1

Write-Output '=== add remote ==='
git remote remove origin 2>$null
git remote add origin https://github.com/nctrnlsoul/Abyssal.git 2>&1
git remote -v 2>&1

Write-Output '=== push ==='
git push -u origin main 2>&1

Write-Output '=== verify ==='
git log --oneline 2>&1
git status -sb 2>&1
