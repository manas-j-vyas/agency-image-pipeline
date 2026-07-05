@echo off
REM ============================================================
REM  build.bat
REM  Double-click this file to build AgencyImagePipeline.exe
REM  (This is for YOU, the developer, to run once. The people
REM  who actually USE the app will only ever touch the .exe
REM  produced in the "dist" folder - they never see this file
REM  or a terminal.)
REM ============================================================

echo.
echo === Agency Image Pipeline - Build Script ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on this machine.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo and make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building AgencyImagePipeline.exe ...
pyinstaller build.spec --noconfirm

echo.
if exist dist\AgencyImagePipeline.exe (
    echo SUCCESS! Your app is at: dist\AgencyImagePipeline.exe
    echo You can copy that single file anywhere and double-click to run it.
    explorer dist
) else (
    echo Build finished but the exe was not found - check the messages above for errors.
)

pause
