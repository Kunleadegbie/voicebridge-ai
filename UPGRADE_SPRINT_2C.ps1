$ErrorActionPreference = "Stop"
Write-Host "VoiceBridge AI Sprint 2C - Official N-ATLAS ASR upgrade verification" -ForegroundColor Cyan
if (-not (Test-Path ".\backend")) { throw "Run this script from the voicebridge-ai project root." }
if (-not (Test-Path ".\.venv\Scripts\python.exe")) { throw "Existing .venv not found." }
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Write-Host "Core upgrade verified. ASR packages are intentionally separate." -ForegroundColor Green
Write-Host "Next install: .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements-asr.txt"
