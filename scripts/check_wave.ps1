$env:PYTHONIOENCODING='utf-8'
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' -c "from core.waveform import envelope; e = envelope(r'C:\Users\brian\Projects\abyssal\data\reef_window_a.wav', 40); print('seconds', e['seconds'], 'rate', e['rate'], 'buckets', len(e['peaks'])); print('peaks', [round(p,2) for p in e['peaks']])"
