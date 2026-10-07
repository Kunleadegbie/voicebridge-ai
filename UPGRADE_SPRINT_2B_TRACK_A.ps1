$ErrorActionPreference = "Stop"

Write-Host "VoiceBridge AI Sprint 2B Track A - post-copy verification" -ForegroundColor Cyan

if (-not (Test-Path ".\backend")) {
    throw "Run this script from the voicebridge-ai project root."
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Existing .venv not found. Keep the Sprint 2A virtual environment in the project root."
}

& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

Push-Location .\backend
$env:PYTHONPATH = (Get-Location).Path
& ..\.venv\Scripts\python.exe -m pytest -q
Pop-Location

Write-Host ""
Write-Host "Upgrade verification complete." -ForegroundColor Green
Write-Host "Next: run scripts\check_hardware.ps1, then start Uvicorn."
