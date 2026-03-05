@echo off
setlocal

REM Profesor Abelton — Windows build (Gumroad)
REM Output: dist\ProfesorAbelton\  +  release\ProfesorAbelton_Windows_vX.Y.Z.zip

cd /d "%~dp0"

echo [i] Running Gumroad release build...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& '%~dp0release_windows.ps1' -Version '2.0.0'"

if errorlevel 1 (
  echo [X] Build/Release failed.
  exit /b 1
)

echo.
echo [OK] Done.
echo      dist\ProfesorAbelton\
echo      release\ProfesorAbelton_Windows_v2.0.0.zip
echo.
exit /b 0

