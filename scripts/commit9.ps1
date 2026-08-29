$ErrorActionPreference='Continue'
Set-Location -LiteralPath $PSScriptRoot\..
git add -A
# -F a file, never -m with a long message. PowerShell and git between them
# reinterpret arrows, apostrophes and backslashes in a multi-line -m string;
# the previous attempt died on "unknown switch `>`".
git commit -F .commitmsg 2>&1
Write-Output '=== log ==='
git log --oneline 2>&1 | Select-Object -First 3
git push 2>&1 | Select-Object -Last 2
