$ErrorActionPreference = 'Stop'
$labRoot = 'C:\Users\rafal\interpretability-lab'
$base = 'analysis/AB_confirmatory_execution_20261101'
$stage = "$base/A_pilot_ready_v1"
Set-Location -LiteralPath $labRoot
if (Test-Path -LiteralPath "$stage/launch_receipt_v1.json") { throw 'A already has launch receipt; no duplicate.' }
$tailReceipt = Get-Content -Raw -LiteralPath "$base/B_tail_qualification_v1/launch_receipt_v1.json" | ConvertFrom-Json
while (Get-Process -Id $tailReceipt.launcher_pid -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
if (Test-Path -LiteralPath 'operations/concurrency_runtime_v1/model.lock') {
    throw 'Model lane lock remains after tail launcher ended; preserve it and stop queue.'
}
# A is independent of the tail verdict. The reviewed lane launcher rechecks all gates.
$memory = Get-CimInstance Win32_OperatingSystem
$launchArgs = @('-X','utf8','-m','concurrency_runtime_v1','--snapshot',"$stage/pre_run_snapshot_v1.json",'--review',"$stage/pre_run_review_astra_v1.json",'--policy',"$base/sol_parallel_acceptance/concurrency_migration_v1/migration_policy.json",'--policy-snapshot',"$base/sol_parallel_acceptance/concurrency_migration_v1/snapshot_v3.json",'--policy-review',"$base/astra_goals_concurrency_review/concurrency_review_v3.json")
$launcher = Start-Process -FilePath 'C:\Users\rafal\miniconda3\python.exe' -ArgumentList $launchArgs -WorkingDirectory $labRoot -WindowStyle Hidden -RedirectStandardOutput "$stage/launch_v1.log" -RedirectStandardError "$stage/launch_v1.err" -PassThru
$receipt = [ordered]@{started_utc=[DateTime]::UtcNow.ToString('o');launcher_pid=$launcher.Id;arguments=$launchArgs;snapshot='1c9b72044bd8317eac3f3924f01f49471ece0738dc352f0dbaaf46889c0f3931';migration_snapshot='c1089be1d7ee60a297dfc84d3211088c516dffa8592f98ee506348db8bbc85ea';scope='Actual A PILOT32blocks;640full+3840local/0backward;frozenr0;noTEST';status='launcher_started';free_RAM_KB=$memory.FreePhysicalMemory;tail_verdict_not_A_dependency=$true}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$stage/launch_receipt_v1.json" -Encoding UTF8
$receipt | ConvertTo-Json -Depth 5
