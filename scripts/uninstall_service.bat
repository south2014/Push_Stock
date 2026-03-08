@echo off
chcp 65001 >nul
echo ==========================================
echo   Push Stock Service Uninstaller
echo ==========================================
echo.

set SERVICE_NAME=PushStockService
set PYTHON_PATH=%~dp0..\venv\Scripts\python.exe
set SERVICE_SCRIPT=%~dp0..\src\core\windows_service.py

echo [1/2] Stopping service if running...
sc stop %SERVICE_NAME% >nul 2>&1
timeout /t 2 /nobreak >nul
echo OK: Service stopped
echo.

echo [2/2] Removing Windows service...
"%PYTHON_PATH%" "%SERVICE_SCRIPT%" remove
if errorlevel 1 (
    echo ERROR: Service removal failed
    echo You may need to run as Administrator
    pause
    exit /b 1
)
echo OK: Service removed successfully
echo.

echo ==========================================
echo   Uninstallation Complete!
echo ==========================================
pause
