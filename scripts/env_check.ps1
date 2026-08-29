Write-Output '=== python ==='
try { py -3 --version } catch { 'py launcher missing' }
Write-Output '=== gcloud ==='
if (Get-Command gcloud -ErrorAction SilentlyContinue) { gcloud --version | Select-Object -First 2 } else { 'GCLOUD NOT INSTALLED' }
Write-Output '=== ffmpeg ==='
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) { 'ffmpeg present' } else { 'ffmpeg NOT installed' }
Write-Output '=== git ==='
git --version
Write-Output '=== GOOGLE_API_KEY set? ==='
if ($env:GOOGLE_API_KEY) { 'YES length=' + $env:GOOGLE_API_KEY.Length } else { 'NOT SET in this shell' }
Write-Output '=== highwater venv ==='
$hw = 'C:\Users\brian\Projects\highwater\.venv\Scripts\python.exe'
if (Test-Path $hw) { & $hw -c "import google.adk, sys; print('adk', google.adk.__version__, '| py', sys.version.split()[0])" } else { 'no highwater venv' }
Write-Output '=== done ==='
