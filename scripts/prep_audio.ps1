$ErrorActionPreference = 'Continue'
$D = 'C:\Users\brian\Projects\abyssal\data'
$src = Join-Path $D 'sanctsound_fk04_raw.flac'

Write-Output '=== probe ==='
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,sample_rate,channels -of default=noprint_wrappers=1 $src 2>&1

Write-Output '=== cutting 60s clips at 16kHz mono ==='
# Gemini downsamples audio to 16 kHz mono, so encode to that directly: no
# quality is lost that the model would have seen, and the file stays inline-able.
ffmpeg -hide_banner -loglevel error -y -ss 00:02:00 -t 60 -i $src -ac 1 -ar 16000 (Join-Path $D 'reef_window_a.wav')
ffmpeg -hide_banner -loglevel error -y -ss 00:20:00 -t 60 -i $src -ac 1 -ar 16000 (Join-Path $D 'reef_window_b.wav')

Write-Output '=== result ==='
Get-ChildItem $D -Filter '*.wav' | Select-Object Name, Length | Format-Table -AutoSize

Write-Output '=== GOOGLE_API_KEY (User scope) ==='
$u = [Environment]::GetEnvironmentVariable('GOOGLE_API_KEY','User')
if ($u) { 'SET at User scope, length=' + $u.Length } else { 'NOT SET at User scope' }
$m = [Environment]::GetEnvironmentVariable('GOOGLE_API_KEY','Machine')
if ($m) { 'SET at Machine scope, length=' + $m.Length } else { 'NOT SET at Machine scope' }
