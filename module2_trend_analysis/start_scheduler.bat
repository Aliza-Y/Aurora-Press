@echo off
cd /d "%~dp0"
echo Starting AuroraPress Trend Scheduler...
"D:\Final Year Project\aurorapress\venv\Scripts\python.exe" scheduler.py
pause 