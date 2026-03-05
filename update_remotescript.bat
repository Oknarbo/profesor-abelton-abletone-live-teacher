@echo off
REM Quick RemoteScript Update
REM Copies updated RemoteScript to Ableton

echo ========================================
echo   UPDATE REMOTESCRIPT
echo ========================================
echo.

set "SCRIPT_SOURCE=RemoteScript\__init__.py"
set "ABLETON_DIR=%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\ProfesorAbelton"

echo Copying updated RemoteScript...
echo.
echo From: %SCRIPT_SOURCE%
echo To:   %ABLETON_DIR%
echo.

REM Create directory if it doesn't exist
if not exist "%ABLETON_DIR%" (
    mkdir "%ABLETON_DIR%"
    echo [OK] Created directory
)

REM Copy file
copy /Y "%SCRIPT_SOURCE%" "%ABLETON_DIR%\__init__.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] RemoteScript updated!
    echo.
    echo ========================================
    echo   NEXT STEPS:
    echo ========================================
    echo.
    echo 1. Close Ableton Live completely
    echo 2. Wait 3 seconds
    echo 3. Reopen Ableton Live
    echo 4. Test: "Add kick to track 1"
    echo.
    echo ========================================
) else (
    echo.
    echo [X] Update failed!
    echo Check that the paths are correct.
)

pause





























