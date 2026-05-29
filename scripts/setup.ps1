# Bootstrap Python environment for the bearing design tool
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv

$py = Join-Path $Root ".venv\Scripts\python.exe"
& $py -m ensurepip --upgrade
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete. Run the web UI with:" -ForegroundColor Green
Write-Host "  .\scripts\run-web.ps1"
