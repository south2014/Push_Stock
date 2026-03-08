@echo off
chcp 65001 >nul
echo ==========================================
echo   Push Stock Service Installer
echo ==========================================
echo.

set SERVICE_NAME=PushStockService
set PYTHON_PATH=%~dp0..\venv\Scripts\python.exe
set SERVICE_SCRIPT=%~dp0..\src\core\windows_service.py

echo [1/3] Checking Python environment...
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
echo OK: Python found
echo.

echo [2/3] Installing Windows service...
"%PYTHON_PATH%" "%SERVICE_SCRIPT%" install
if errorlevel 1 (
    echo ERROR: Service installation failed
    pause
    exit /b 1
)
echo OK: Service installed successfully
echo.

echo [3/3] Setting service to auto-start...
sc config %SERVICE_NAME% start= auto
if errorlevel 1 (
    echo WARNING: Could not set auto-start
) else (
    echo OK: Auto-start configured
)
echo.

echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo Service Name: %SERVICE_NAME%
echo.
echo Commands:
echo   Start:   sc start %SERVICE_NAME%
echo   Stop:    sc stop %SERVICE_NAME%
echo   Status:  sc query %SERVICE_NAME%
echo   Remove:  run uninstall_service.bat
echo.
pause
