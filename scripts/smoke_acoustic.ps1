$env:GOOGLE_API_KEY = [Environment]::GetEnvironmentVariable('GOOGLE_API_KEY','User')
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' 'scripts\smoke_acoustic.py'
