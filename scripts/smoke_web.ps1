$env:PYTHONIOENCODING='utf-8'
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' -m pip install httpx --quiet 2>&1 | Select-Object -Last 2
& '.\.venv\Scripts\python.exe' 'scripts\smoke_web.py'
