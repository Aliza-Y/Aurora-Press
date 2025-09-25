# Define absolute paths
$projectRoot = "D:\Final Year Project\aurorapress"
$moduleDir = Join-Path $projectRoot "module2_trend_analysis"
$venvDir = Join-Path $projectRoot "venv"
$logsDir = Join-Path $moduleDir "logs"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

# Verify Python executable exists
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python executable not found at: $pythonExe"
    exit 1
}

# Change to the module directory
Set-Location $moduleDir

# Create logs directory if it doesn't exist
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir
}

# Activate the virtual environment
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Error "Virtual environment not found at $venvDir"
    exit 1
}

# Start the scheduler
Write-Host "Starting AuroraPress Trend Scheduler..."
Write-Host "Using Python from: $pythonExe"
Write-Host "Logs will be written to: $logsDir\scheduler.log"

# Use the virtual environment's Python explicitly with full path
& $pythonExe scheduler.py

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 