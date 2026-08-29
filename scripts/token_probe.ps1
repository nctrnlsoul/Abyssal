$env:GOOGLE_API_KEY = [Environment]::GetEnvironmentVariable('GOOGLE_API_KEY','User')
$py = 'C:\Users\brian\Projects\highwater\.venv\Scripts\python.exe'
& $py 'C:\Users\brian\Projects\abyssal\scripts\token_probe.py'
