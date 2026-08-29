$ErrorActionPreference = 'Continue'
$D = 'C:\Users\brian\Projects\abyssal\data'
New-Item -ItemType Directory -Force -Path $D | Out-Null
$ProgressPreference = 'SilentlyContinue'

function Get-Asset($url, $out, $label) {
  $path = Join-Path $D $out
  if (Test-Path $path) { Write-Output "$label ALREADY PRESENT ($((Get-Item $path).Length) bytes)"; return }
  Write-Output "$label downloading..."
  try {
    Invoke-WebRequest -Uri $url -OutFile $path -UseBasicParsing -TimeoutSec 300
    Write-Output "$label OK $((Get-Item $path).Length) bytes"
  } catch {
    Write-Output "$label FAILED: $($_.Exception.Message)"
  }
}

Get-Asset 'https://www.fda.gov/media/181370/download' 'nssp_2023.pdf' 'NSSP_PDF'
Get-Asset 'https://nccospublicstor.blob.core.windows.net/hab-data/forecasts/GoMex_redtide/fl_current_image_cellcnts.png' 'hab_forecast_cellcounts.png' 'HAB_PNG'
Get-Asset 'https://assets.science.nasa.gov/content/dam/science/esd/eo/images/imagerecords/9000/9135/Fla_RedTide_122201_lrg.jpg' 'nasa_modis_redtide_2001.jpg' 'NASA_JPG'
Get-Asset 'https://storage.googleapis.com/noaa-passive-bioacoustic/sanctsound/audio/fk04/sanctsound_fk04_08/audio/SanctSound_FK04_08_470032451_210323151500.flac' 'sanctsound_fk04_raw.flac' 'AUDIO_FLAC'

Write-Output '=== contents ==='
Get-ChildItem $D | Select-Object Name, Length | Format-Table -AutoSize
