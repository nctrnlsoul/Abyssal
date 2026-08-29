$ErrorActionPreference='Continue'
$ProgressPreference='SilentlyContinue'
foreach ($u in @('https://highwater-yfahuqruia-uc.a.run.app/healthz','https://highwater-yfahuqruia-uc.a.run.app/')) {
  try {
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 30
    Write-Output "$u -> $($r.StatusCode), $($r.RawContentLength) bytes"
  } catch {
    Write-Output "$u -> FAILED: $($_.Exception.Message)"
  }
}
