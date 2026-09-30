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

function Assert-NativeSuccess([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

# Report the interpreter version before anything depends on it. This also makes
# $LASTEXITCODE defined for the checks below.
& $PythonCmd -c "import sys; print('Using Python ' + sys.version.split()[0])"
Assert-NativeSuccess "Reading the Python version"

$VenvPython = Join-Path $ProjectDir '.venv\Scripts\python.exe'

# Test for a usable interpreter, not merely a .venv directory. A venv whose
# creation failed part-way still leaves the folder behind, and testing only for
# the folder makes every later run skip creation and fail at pip instead.
if (-not (Test-Path $VenvPython)) {
    if (Test-Path '.venv') {
        Write-Host "Found a .venv with no interpreter. Recreating it." -ForegroundColor Yellow
        Remove-Item -Recurse -Force '.venv'
    }
    Write-Host "Creating virtual environment..."
    & $PythonCmd -m venv .venv
    Assert-NativeSuccess "Creating virtual environment"
}

if (-not (Test-Path $VenvPython)) {
    throw "The virtual environment is still missing $VenvPython after creation. Delete the .venv folder and rerun this script."
}

# venv can produce an interpreter with no pip, so verify rather than assume.
& $VenvPython -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "The virtual environment has no working pip. Repairing with ensurepip..." -ForegroundColor Yellow
    & $VenvPython -m ensurepip --upgrade --default-pip
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install pip into .venv. Delete the .venv folder and rerun. If it fails again, this Python install is missing its bundled pip (ensurepip)."
    }
    & $VenvPython -m pip --version *> $null
    Assert-NativeSuccess "Verifying pip after ensurepip"
    Write-Host "pip repaired." -ForegroundColor Green
}

Write-Host "Installing/updating dependencies..."
& $VenvPython -m pip install --upgrade pip
Assert-NativeSuccess "Upgrading pip"
# Use "python -m pip" rather than pip.exe: the shim can be absent even when the
# pip module is importable, which is exactly the state ensurepip repairs.
& $VenvPython -m pip install -r requirements.txt
Assert-NativeSuccess "Installing dependencies"

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host "Created .env from .env.example. Live publishing remains disabled." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists; leaving it unchanged."
}

Write-Host "Running test suite..."
$env:PYTHONPATH = $ProjectDir
& $VenvPython -m pytest -q
Assert-NativeSuccess "Test suite"

Write-Host ""
Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "Next: open .env and add credentials one route at a time."
Write-Host "Keep PUBLISHER_ENABLED=false and DRY_RUN=true until a controlled test is ready."
Write-Host "Then run:"
Write-Host "  .\.venv\Scripts\python.exe -m social_publisher.main --dry-run"
Write-Host ""
Write-Host "Canonical cutover checklist: GitHub issue #9"
