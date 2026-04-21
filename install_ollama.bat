@echo off
REM Install Ollama - Required for local LLM support
REM This script downloads and installs Ollama

echo.
echo =========================================
echo   Installing Ollama
echo =========================================
echo.

REM Check if Ollama is already installed
where ollama >nul 2>&1
if not errorlevel 1 (
    echo Ollama is already installed
    exit /b 0
)

echo Ollama is required for running language models locally.
echo.
echo Downloading Ollama installer...
echo.

REM Download the installer
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://ollama.ai/download/windows' -OutFile '%TEMP%\ollama-installer.exe'"

if not exist "%TEMP%\ollama-installer.exe" (
    echo ERROR: Failed to download Ollama
    echo Please download manually from: https://ollama.ai
    pause
    exit /b 1
)

echo Running installer...
"%TEMP%\ollama-installer.exe"

REM Clean up
del "%TEMP%\ollama-installer.exe"

echo.
echo Ollama installation complete
echo Please restart your terminal or computer for PATH changes to take effect
echo.
echo After installing, you may need to pull models with:
echo   ollama pull phi3
echo   ollama pull mistral
pause
