Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' -m pip install pymupdf --quiet 2>&1 | Select-Object -Last 3
& '.\.venv\Scripts\python.exe' 'scripts\find_biotoxin.py'
