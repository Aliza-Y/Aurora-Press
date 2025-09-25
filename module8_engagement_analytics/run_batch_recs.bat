@echo off
REM Change to project folder
cd /d "D:\Final Year Project\aurorapress"

REM Activate venv
call ".\venv\Scripts\activate.bat"

REM Run the batch recommender and tee output to a date-stamped run log as well
echo ==== %DATE% %TIME% starting batch_recommend.py ==== >> "module8_engagement_analytics\run_history.log"
python ".\module8_engagement_analytics\batch_recommend.py" >> "module8_engagement_analytics\run_history.log" 2>&1
echo ==== %DATE% %TIME% completed ==== >> "module8_engagement_analytics\run_history.log"
