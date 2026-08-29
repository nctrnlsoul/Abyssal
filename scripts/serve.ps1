# Local console. KEYLESS on purpose: this process reads no GOOGLE_API_KEY.
# --reload because index.html and the CSP hash are both read at import, so
# without it an edited page is served stale and you review the old one.
param([int]$Port = 8081)
$env:PYTHONIOENCODING='utf-8'
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' -m uvicorn web.app:app --host 127.0.0.1 --port $Port --reload
