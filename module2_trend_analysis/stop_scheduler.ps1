# Get all Python processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

# Filter for our scheduler process
$schedulerProcess = $pythonProcesses | Where-Object { $_.CommandLine -like "*scheduler.py*" }

if ($schedulerProcess) {
    Write-Host "Stopping AuroraPress Trend Scheduler..."
    $schedulerProcess | Stop-Process -Force
    Write-Host "Scheduler stopped successfully!"
} else {
    Write-Host "No running scheduler process found."
}

# Keep the window open briefly
Start-Sleep -Seconds 2 