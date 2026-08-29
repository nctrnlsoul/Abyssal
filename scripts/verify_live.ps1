$ProgressPreference='SilentlyContinue'
$urls = @(
  'https://abyssal-7517955252.us-central1.run.app',
  'https://abyssal-yfahuqruia-uc.a.run.app'
)
foreach ($base in $urls) {
  Write-Output "=== $base ==="
  foreach ($p in @('/healthz','/','/api/run','/api/bands','/api/waveform','/api/source-image','/nope')) {
    try {
      $r = Invoke-WebRequest -Uri ($base + $p) -UseBasicParsing -TimeoutSec 40
      Write-Output ("  [{0}] {1,-20} {2} bytes" -f $r.StatusCode, $p, $r.RawContentLength)
    } catch {
      $code = $null
      if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
      Write-Output ("  [{0}] {1,-20} {2}" -f ($(if($code){$code}else{'ERR'})), $p, $_.Exception.Message)
    }
  }
  Write-Output ""
}
Write-Output "=== security headers on / (canonical url) ==="
try {
  $r = Invoke-WebRequest -Uri 'https://abyssal-7517955252.us-central1.run.app/' -UseBasicParsing -TimeoutSec 40
  foreach ($h in @('Content-Security-Policy','Strict-Transport-Security','X-Content-Type-Options','X-Frame-Options','Referrer-Policy')) {
    $v = $r.Headers[$h]
    Write-Output ("  {0,-28} {1}" -f $h, $(if($v){ $v.Substring(0,[Math]::Min(70,$v.Length)) } else { 'MISSING' }))
  }
} catch { Write-Output ("  header check failed: " + $_.Exception.Message) }
