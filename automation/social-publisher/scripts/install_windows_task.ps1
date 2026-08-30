param(
    [string]$TaskName = "Sklarz Social Publisher"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$EnvFile = Join-Path $Root ".env"
$LoopScript = Join-Path $Root "scripts\run_loop.py"

if (-not (Test-Path $Python)) {
    throw "Virtual environment not found at $Venv. Run: py -m venv .venv; .\.venv\Scripts\pip.exe install -r requirements.txt"
}
if (-not (Test-Path $EnvFile)) {
    throw ".env not found. Copy .env.example to .env and configure credentials first."
}

$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument ('"{0}"' -f $LoopScript) `
    -WorkingDirectory $Root

$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 2) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Runs the Sklarz Creative direct social publisher loop at Windows startup." `
    -Force

Write-Host "Installed '$TaskName'."
Write-Host "Before enabling live publishing, run:"
Write-Host "  $Python -m social_publisher.main --dry-run"
Write-Host "Then set PUBLISHER_ENABLED=true and DRY_RUN=false in .env."
