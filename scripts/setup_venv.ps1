$ErrorActionPreference='Continue'
Set-Location 'C:\Users\brian\Projects\abyssal'
if (-not (Test-Path '.venv')) {
  Write-Output '=== creating venv ==='
  py -3 -m venv .venv
} else { Write-Output '=== venv exists ===' }

$py = '.\.venv\Scripts\python.exe'
Write-Output '=== upgrading pip ==='
& $py -m pip install --upgrade pip --quiet 2>&1 | Select-Object -Last 3
Write-Output '=== installing requirements (this takes a minute) ==='
& $py -m pip install -r requirements.txt --quiet 2>&1 | Select-Object -Last 10
Write-Output '=== verify ==='
& $py -c "import sys, google.adk, google.genai, fastapi, pytest; print('python', sys.version.split()[0]); print('adk', google.adk.__version__); print('fastapi', fastapi.__version__)"
