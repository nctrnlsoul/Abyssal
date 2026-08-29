$env:PYTHONIOENCODING='utf-8'
Set-Location 'C:\Users\brian\Projects\abyssal'
& '.\.venv\Scripts\python.exe' -c "from core.waveform import envelope; e=envelope(r'C:\Users\brian\Projects\abyssal\data\reef_window_a.wav', 40); print('seconds',e['seconds'],'rate',e['rate'],'corner',e['low_band_corner_hz'],'Hz'); print('peak at',e['peak_at_seconds'],'s  low-band peak at',e['low_peak_at_seconds'],'s'); print('full', [round(p,2) for p in e['peaks']]); print('low ', [round(p,2) for p in e['low_band']])"
