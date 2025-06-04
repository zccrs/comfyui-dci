@echo off
REM ComfyUI DCI Extension Installation Script for Windows
REM This script installs the required dependencies for the DCI extension

echo Installing ComfyUI DCI Extension dependencies...

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
) else (
    echo Dependencies installed successfully!
)

REM Check if ComfyUI is available
if exist "..\..\..\ComfyUI" (
    echo ComfyUI installation detected
) else if exist "..\..\ComfyUI" (
    echo ComfyUI installation detected
) else (
    echo Warning: ComfyUI installation not found in expected locations
    echo Make sure this extension is installed in ComfyUI\custom_nodes\
)

echo.
echo Installation completed!
echo.
echo To use the DCI extension:
echo 1. Restart ComfyUI
echo 2. Look for DCI nodes in the node menu under 'DCI' category
echo 3. Check the examples\ directory for sample workflows
echo.
echo For more information, see README.md
echo.
pause
