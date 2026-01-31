@echo off
cd /d "%~dp0"
REM اگر virtual environment داری:
call venv\Scripts\activate
start "" "http://localhost:5000"
python app.py
pause
