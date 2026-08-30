$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "Sklarz Social Publisher - Windows bootstrap" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir"

$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = 'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = 'python'
} else {
    throw "Python 3.11+ was not found. Install Python, then rerun this script."
}

if (-not (Test-Path '.venv')) {
    Write-Host "Creating virtual environment..."
    & $PythonCmd -m venv .venv
}

$VenvPython = Join-Path $ProjectDir '.venv\Scripts\python.exe'
$VenvPip = Join-Path $ProjectDir '.venv\Scripts\pip.exe'

Write-Host "Installing/updating dependencies..."
& $VenvPython -m pip install --upgrade pip
& $VenvPip install -r requirements.txt

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host "Created .env from .env.example. Live publishing remains disabled." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists; leaving it unchanged."
}

Write-Host "Running test suite..."
$env:PYTHONPATH = $ProjectDir
& $VenvPython -m pytest -q

Write-Host ""
Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "Next: open .env and add credentials one route at a time."
Write-Host "Keep PUBLISHER_ENABLED=false and DRY_RUN=true until a controlled test is ready."
Write-Host "Then run:"
Write-Host "  .\.venv\Scripts\python.exe -m social_publisher.main --dry-run"
Write-Host ""
Write-Host "Canonical cutover checklist: GitHub issue #9"
