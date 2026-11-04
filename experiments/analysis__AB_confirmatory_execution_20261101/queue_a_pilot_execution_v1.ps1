$ErrorActionPreference = 'Stop'
$labRoot = 'C:\Users\rafal\interpretability-lab'
$baseRelative = 'analysis/AB_confirmatory_execution_20261101'
$tailRoot = Join-Path $labRoot "$baseRelative/B_tail_qualification_v1"
$stageRelative = "$baseRelative/A_pilot_ready_v1"
$stageRoot = Join-Path $labRoot $stageRelative
$receiptPath = Join-Path $stageRoot 'launch_receipt_v1.json'
Set-Location -LiteralPath $labRoot
if (Test-Path -LiteralPath $receiptPath) { throw 'A PILOT already has launch receipt; never duplicate.' }
while (-not (Test-Path -LiteralPath (Join-Path $tailRoot 'run/stage_completed.json'))) {
    $tailReceiptPath = Join-Path $tailRoot 'launch_receipt_v1.json'
    if (Test-Path -LiteralPath $tailReceiptPath) {
        $tailReceipt = Get-Content -Raw -LiteralPath $tailReceiptPath | ConvertFrom-Json
        if (-not (Get-Process -Id $tailReceipt.launcher_pid -ErrorAction SilentlyContinue)) {
            throw 'Tail ended without completed stage. Preserve evidence; A queue stops.'
        }
    }
    Start-Sleep -Seconds 10
}
while (Test-Path -LiteralPath 'operations/research_worker.lock') {
    $lock = Get-Content -Raw -LiteralPath 'operations/research_worker.lock' | ConvertFrom-Json
    if ($lock.snapshot_sha256 -ne 'ba4c7f114686a6e5ab4517847228b81166d66797902e87bb13f7c1ce03adbe21') {
        throw 'Unexpected lock owner after completed tail; do not bypass.'
    }
    Start-Sleep -Seconds 10
}
$live = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'")
$unexpected = @($live | Where-Object { $_.ProcessId -notin @(4428,12416) })
if ($unexpected.Count -gt 0) { throw ('Unexpected Python process at slot boundary: ' + ($unexpected.ProcessId -join ',')) }
$launchArgs = @('-X','utf8','-m','research_checks','launch','--snapshot',"$stageRelative/pre_run_snapshot_v1.json",'--review',"$stageRelative/pre_run_review_astra_v1.json")
$launcher = Start-Process -FilePath 'C:\Users\rafal\miniconda3\python.exe' -ArgumentList $launchArgs -WorkingDirectory $labRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $stageRoot 'launch_v1.log') -RedirectStandardError (Join-Path $stageRoot 'launch_v1.err') -PassThru
$receipt = [ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');launcher_pid=$launcher.Id;snapshot='1c9b72044bd8317eac3f3924f01f49471ece0738dc352f0dbaaf46889c0f3931';arguments=$launchArgs;existing_python_pids=@($live.ProcessId);scope='Actual A PILOT32blocks;640full+3840local/0backward;frozenr0;noTEST';status='launcher_started'}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
$receipt | ConvertTo-Json -Depth 5
