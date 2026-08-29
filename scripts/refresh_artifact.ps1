$env:PYTHONIOENCODING='utf-8'
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' 'scripts\refresh_artifact.py'
& '.\.venv\Scripts\python.exe' -m pytest tests -q
