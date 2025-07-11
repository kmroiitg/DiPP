@echo off
REM === Set your script and icon paths ===
set SCRIPT_NAME=DiPP_v7.0.py
set ICON_FILE=DiPP.ico

REM === Remove previous build ===
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

REM === Create executable ===
pyinstaller --noconfirm --onefile --windowed --icon=%ICON_FILE% %SCRIPT_NAME%

echo.
echo EXE successfully built and saved in the 'dist' folder.
pause
