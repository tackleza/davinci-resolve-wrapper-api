@echo off
echo ===== Restarting DaVinci Wrapper =====
echo.

REM Kill process on port 8080
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start wrapper
echo Starting wrapper...
start "" /min "C:\Users\Tackle\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\Tackle\davinci_wrapper\main.py"

echo Done! Wrapper starting at http://127.0.0.1:8080
