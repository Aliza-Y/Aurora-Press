Write-Host "=== Frontend Fix Script ===" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Stopping any running processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host ""

Write-Host "Step 2: Cleaning Next.js cache..." -ForegroundColor Yellow
Set-Location frontend
if (Test-Path ".next") { Remove-Item -Recurse -Force ".next" }
if (Test-Path "node_modules\.cache") { Remove-Item -Recurse -Force "node_modules\.cache" }
Write-Host ""

Write-Host "Step 3: Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force
Write-Host ""

Write-Host "Step 4: Reinstalling dependencies..." -ForegroundColor Yellow
npm install
Write-Host ""

Write-Host "Step 5: Starting development server..." -ForegroundColor Yellow
npm run dev
