@echo off
echo === Frontend Fix Script ===
echo.

echo Step 1: Stopping any running processes...
taskkill /f /im node.exe 2>nul
echo.

echo Step 2: Cleaning Next.js cache...
cd frontend
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache
echo.

echo Step 3: Clearing npm cache...
npm cache clean --force
echo.

echo Step 4: Reinstalling dependencies...
npm install
echo.

echo Step 5: Starting development server...
npm run dev
