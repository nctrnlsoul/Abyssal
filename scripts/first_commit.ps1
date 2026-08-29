$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
git add -A
Write-Output '=== staged ==='
git status --short
Write-Output '=== committing ==='
git commit -m "Scaffold Project Abyssal: real data manifest, licence, hygiene

Four-agent marine biosecurity pipeline over real public data.
No model code yet. This commit establishes the repo and the honest
what-is-real table before any agent is written.

Data sources verified and downloaded (gitignored, reproducible via
scripts/fetch_data.ps1): NOAA SanctSound FK04 Florida Keys hydrophone,
NOAA NCCOS HAB forecast, NASA MODIS, FDA NSSP 2023 Guide.

Measured cost: the 520-page ordinance is 297,921 tokens, 98.6% of a
full pipeline pass. Everything else totals 4,111." 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1
Write-Output '=== what is tracked (confirm no big binaries) ==='
git ls-files | ForEach-Object { $s = (Get-Item $_).Length; "{0,10}  {1}" -f $s, $_ }
