@echo off
REM Complete Setup Script - Installs all project dependencies
REM This script ensures all system and project dependencies are installed

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo =========================================
echo   HealthMitra Scan - Complete Setup
echo =========================================
echo.

REM Check and install Tesseract
echo [1/3] Checking Tesseract OCR...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo Tesseract is not installed
    echo.
    call install_tesseract.bat
) else (
    echo Tesseract is already installed
)

REM Check and install Ollama
echo.
echo [2/3] Checking Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed
    echo.
    call install_ollama.bat
) else (
    echo Ollama is already installed
)

REM Run the main project runner
echo.
echo [3/3] All system dependencies installed!
echo.
echo =========================================
echo   Setup Complete
echo =========================================
echo.
echo You can now run the project with: run.bat
echo Or proceed with manual setup if needed.
echo.
pause
