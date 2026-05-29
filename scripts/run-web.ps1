# Start FastAPI web UI (backend + frontend)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "No .venv found. Run .\scripts\setup.ps1 first." -ForegroundColor Yellow
    $py = "python"
}

$port = if ($args.Count -gt 0) { $args[0] } else { 8000 }
& $py main.py --web --port $port
