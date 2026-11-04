param([int]$MaxHours=24)
$ErrorActionPreference='Stop'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class ResearchExecutionState {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$receiptRoot=Join-Path $PSScriptRoot 'keep_awake_v1'
New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
$deadline=[DateTime]::UtcNow.AddHours($MaxHours)
$flags=[uint32]2147483649
$set=[ResearchExecutionState]::SetThreadExecutionState($flags)
if($set -eq 0){throw 'SetThreadExecutionState failed'}
try {
    while([DateTime]::UtcNow -lt $deadline){
        $workers=@(Get-CimInstance Win32_Process | Where-Object {
            $_.Name -eq 'python.exe' -and
            $_.CommandLine -match 'analysis[\\/](AB_confirmatory_execution_20261101|A_estimation_v7|A_short_replication_(qwen|llama)_20261101)' -and (
                $_.CommandLine -match '\-m research_checks\._worker' -or
                $_.CommandLine -match '\-m concurrency_runtime_' -or
                $_.CommandLine -match 'B_descriptive_TEST_v8/completion_contract_v1.json' -or
                $_.CommandLine -match '\-m ab_confirmatory_20261101\.prepare_secondary_v5' -or
                $_.CommandLine -match '\-m prepare_short_fixed_v3'
            )
        } | Select-Object ProcessId,ParentProcessId,CommandLine)
        $stop=Test-Path (Join-Path $receiptRoot 'STOP')
        $leasePath=Join-Path $receiptRoot 'queue_lease.json'
        $queued=$false
        if(Test-Path $leasePath){
            $lease=Get-Content -LiteralPath $leasePath -Raw | ConvertFrom-Json
            $queued=$lease.active -eq $true -and [DateTime]::Parse($lease.expires_utc).ToUniversalTime() -gt [DateTime]::UtcNow
        }
        if($stop -or ($workers.Count -eq 0 -and -not $queued)){break}
        if([ResearchExecutionState]::SetThreadExecutionState($flags) -eq 0){throw 'Keep-awake heartbeat failed'}
        @{utc=[DateTime]::UtcNow.ToString('o');helper_pid=$PID;flags='ES_CONTINUOUS|ES_SYSTEM_REQUIRED';display_required=$false;workers=$workers;authorized_queue_active=$queued;deadline_utc=$deadline.ToString('o')} |
            ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $receiptRoot 'heartbeat.json')
        Start-Sleep -Seconds 20
    }
} finally {
    $cleared=[ResearchExecutionState]::SetThreadExecutionState([uint32]2147483648)
    @{utc=[DateTime]::UtcNow.ToString('o');helper_pid=$PID;continuous_clear_result=$cleared;reason='No matched experiment process, STOP marker, deadline, or exception'} |
        ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $receiptRoot 'exit.json')
}
