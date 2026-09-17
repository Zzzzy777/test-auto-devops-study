@echo off
setlocal
set "ROOT=%~dp0"

if not exist "%ROOT%start-all.ps1" (
  echo ERROR: start-all.ps1 was not found in %ROOT%
  pause
  exit /b 1
)

if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
  echo Starting Docker Desktop...
  start "Docker Desktop" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
)

echo Waiting for Docker Desktop...
set /a COUNT=0
:waitdocker
docker info >nul 2>&1
if not errorlevel 1 goto dockerready
set /a COUNT+=1
if %COUNT% GEQ 60 (
  echo ERROR: Docker Desktop is not ready. Please start it manually and retry.
  pause
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto waitdocker

:dockerready
echo Docker is ready. Starting project 2...
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%ROOT%start-all.ps1"
if errorlevel 1 (
  echo ERROR: Project 2 failed to start.
  echo Check logs under %ROOT%runtime\logs
  pause
  exit /b 1
)

echo Project 2 started successfully.
echo Admin: http://localhost:8090
echo Mall:  http://localhost:8060
start "" "http://localhost:8090"
start "" "http://localhost:8060"
pause
