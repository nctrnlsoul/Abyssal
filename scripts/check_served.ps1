$ProgressPreference='SilentlyContinue'
$r = Invoke-WebRequest -Uri 'http://127.0.0.1:8081/' -UseBasicParsing -TimeoutSec 20
$c = $r.Content
Write-Output ("served bytes: " + $c.Length)
foreach ($needle in @('minmax(0, 1fr)', '.cols > \* \{ min-width: 0', 'overflow-x: hidden', 'overflow-wrap: anywhere', 'top: -34px')) {
  $found = $c -match $needle
  Write-Output ("  [" + $(if($found){"PRESENT"}else{"MISSING"}) + "] " + $needle)
}
