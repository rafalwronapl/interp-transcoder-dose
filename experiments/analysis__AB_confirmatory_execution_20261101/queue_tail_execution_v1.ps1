$ErrorActionPreference = 'Stop'
$labRoot = 'C:\Users\rafal\interpretability-lab'
$stageRelative = 'analysis/AB_confirmatory_execution_20261101/B_tail_qualification_v1'
$stageRoot = Join-Path $labRoot $stageRelative
$receiptPath = Join-Path $stageRoot 'launch_receipt_v1.json'
Set-Location -LiteralPath $labRoot
if (Test-Path -LiteralPath $receiptPath) { throw 'Tail already has a launch receipt; never start another copy.' }
while (Test-Path -LiteralPath 'operations/research_worker.lock') {
    $lock = Get-Content -Raw -LiteralPath 'operations/research_worker.lock' | ConvertFrom-Json
    if ($lock.snapshot_sha256 -ne 'c66e39c425fc9c6e202e72c385052f4790dfec84d3db1daa9a41c574bb041faf') {
        throw 'Unexpected lock owner. Preserve it and stop queue.'
    }
    if (-not (Get-Process -Id 4612 -ErrorAction SilentlyContinue)) {
        throw 'Precision launcher ended but lock remains. Do not remove or bypass it.'
    }
    Start-Sleep -Seconds 10
}
$live = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'")
$unexpected = @($live | Where-Object { $_.ProcessId -notin @(4428,12416) })
if ($unexpected.Count -gt 0) { throw ('Unexpected Python process at slot boundary: ' + ($unexpected.ProcessId -join ',')) }
$launchArgs = @('-X','utf8','-m','research_checks','launch','--snapshot',"$stageRelative/pre_run_snapshot_v1.json",'--review',"$stageRelative/pre_run_review_astra_v1.json")
$launcher = Start-Process -FilePath 'C:\Users\rafal\miniconda3\python.exe' -ArgumentList $launchArgs -WorkingDirectory $labRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $stageRoot 'launch_v1.log') -RedirectStandardError (Join-Path $stageRoot 'launch_v1.err') -PassThru
$receipt = [ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');launcher_pid=$launcher.Id;snapshot='ba4c7f114686a6e5ab4517847228b81166d66797902e87bb13f7c1ce03adbe21';arguments=$launchArgs;existing_python_pids=@($live.ProcessId);scope='Technical four unused FIT recipients;152forward/8backward;noPILOT/TEST';status='launcher_started'}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
$receipt | ConvertTo-Json -Depth 5
