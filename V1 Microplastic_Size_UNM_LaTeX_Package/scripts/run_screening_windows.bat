@echo off
REM Run this from the project folder, with the 10,833-row export next to this file's parent folder.
REM Example: scripts\run_screening_windows.bat "C:\Users\SIVI\Documents\Y3\Group Project\Case studies\Combined\Include_Candidates.csv"
if "%~1"=="" (
  echo Usage: %~nx0 "C:\path\to\Include_Candidates.csv"
  exit /b 1
)
py -m pip install -r "%~dp0requirements.txt"
py "%~dp001_screen_candidates.py" --input "%~1" --output "%~dp0..\data"
if errorlevel 1 exit /b 1
py "%~dp003_verify_outputs.py" "%~dp0..\data"
