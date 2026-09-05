@echo off
setlocal
cd /d "%~dp0UVR5-UI"

echo ==========================================
echo        UVR5-UI Start Script
echo ==========================================

echo.
echo [1/3] Kill residual app.py processes...
set "KILLED="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /C:":9999 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%p
    taskkill /F /PID %%p >nul 2>&1
    set "KILLED=1"
)
if defined KILLED (
    echo   Killed residual instances on port 9999
) else (
    echo   No residual instance
)

echo.
echo [2/3] Waiting for port 9999 to be released...
set "PORT_FREE="
for /l %%i in (1,1,15) do (
    netstat -ano | findstr /C:":9999 " | findstr "LISTENING" >nul 2>&1 || set "PORT_FREE=1"
    if defined PORT_FREE goto :port_free
    timeout /t 1 /nobreak >nul
)
:port_free
if defined PORT_FREE (
    echo   Port 9999 released
) else (
    echo   WARNING: Port 9999 still in use, may conflict
)

echo.
echo [3/3] Starting service...
echo   URL: http://127.0.0.1:9999
echo   (Press Ctrl+C to stop)
echo.
choice /C YN /N /M "Start service now (Y=yes / N=exit) ? "
if errorlevel 2 goto :eof

echo.
echo Starting, please wait...
".venv\Scripts\python.exe" app.py --listen-port 9999
if errorlevel 1 (
    echo.
    echo Failed to start. Check .venv\Scripts\python.exe and app.py.
    pause
)
endlocal
