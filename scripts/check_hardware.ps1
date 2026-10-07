$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "VoiceBridge AI - N-ATLAS Local Hardware Check" -ForegroundColor Cyan
Write-Host "------------------------------------------------"

$os = Get-CimInstance Win32_OperatingSystem
$computer = Get-CimInstance Win32_ComputerSystem
$totalRamGB = [math]::Round($computer.TotalPhysicalMemory / 1GB, 1)

Write-Host "Windows:" $os.Caption
Write-Host "System RAM:" "$totalRamGB GB"

Write-Host ""
Write-Host "GPU information:"
try {
    Get-CimInstance Win32_VideoController |
        Select-Object Name, AdapterRAM, DriverVersion |
        ForEach-Object {
            $ram = if ($_.AdapterRAM) { [math]::Round($_.AdapterRAM / 1GB, 1) } else { "Unknown" }
            Write-Host (" - {0} | reported VRAM: {1} GB | driver: {2}" -f $_.Name, $ram, $_.DriverVersion)
        }
} catch {
    Write-Host "Could not query GPU via Windows CIM."
}

Write-Host ""
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host "NVIDIA CUDA details:" -ForegroundColor Green
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else {
    Write-Host "nvidia-smi not found. No NVIDIA CUDA runtime was detected from PATH." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Recommendation:"
Write-Host "N-ATLAS is an 8B BF16 model. Full local loading is demanding."
Write-Host "For the NAIC build, prefer an official/hosted N-ATLAS endpoint when available."
Write-Host "Use local mode only if the machine has adequate GPU/RAM and after accepting model access terms."
