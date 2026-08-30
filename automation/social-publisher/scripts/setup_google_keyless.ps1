$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ProjectId = 'project-19d57a26-9670-4cb4-a45'
$ServiceAccount = 'sklarz-social-publisher@project-19d57a26-9670-4cb4-a45.iam.gserviceaccount.com'
$Scopes = 'https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets'

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)][string]$Command,
        [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
    )
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host 'Google Cloud CLI is not installed or not on PATH.' -ForegroundColor Yellow
    Write-Host 'Install it with:'
    Write-Host '  winget install --id Google.CloudSDK --exact'
    Write-Host 'Then close and reopen PowerShell and rerun this script.'
    exit 2
}

Write-Host 'Sklarz Social Publisher - keyless Google authentication' -ForegroundColor Cyan
Write-Host 'No service-account private key will be created or stored.'
Write-Host ''

$Account = (& gcloud config get account 2>$null).Trim()
$WorkingLogin = $false
if ($Account -and $Account -ne '(unset)') {
    & gcloud auth print-access-token --account=$Account *> $null
    if ($LASTEXITCODE -eq 0) {
        $WorkingLogin = $true
    }
}

if ($WorkingLogin) {
    Write-Host "Using existing Google Cloud CLI login: $Account"
} else {
    Write-Host 'No working Google Cloud CLI login found. Opening browser sign-in...'
    Invoke-Checked gcloud auth login
    $Account = (& gcloud config get account 2>$null).Trim()
    if (-not $Account -or $Account -eq '(unset)') {
        throw 'Could not determine the signed-in Google account.'
    }
}

Write-Host "Setting project to $ProjectId..."
Invoke-Checked gcloud config set project $ProjectId
Write-Host "Signed in as: $Account"

Write-Host 'Enabling required APIs...'
Invoke-Checked gcloud services enable sheets.googleapis.com iamcredentials.googleapis.com --project=$ProjectId

Write-Host 'Granting this Google account permission to impersonate the publisher service account...'
Invoke-Checked gcloud iam service-accounts add-iam-policy-binding $ServiceAccount `
    --member="user:$Account" `
    --role='roles/iam.serviceAccountTokenCreator' `
    --project=$ProjectId

Write-Host 'Creating local Application Default Credentials using service-account impersonation...'
Invoke-Checked gcloud auth application-default login `
    --impersonate-service-account=$ServiceAccount `
    --scopes=$Scopes

Write-Host ''
Write-Host 'Keyless Google authentication is configured.' -ForegroundColor Green
Write-Host 'The publisher can now use Application Default Credentials.'
Write-Host 'Keep PUBLISHER_ENABLED=false and DRY_RUN=true until the Sheet dry run succeeds.'
