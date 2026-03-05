Param(
  [string]$Version = "2.0.0",
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "[i] Building ProfesorAbelton (Gumroad-ready)..." -ForegroundColor Cyan

# Build in an isolated venv to avoid accidentally bundling unrelated packages
# from some other workspace venv (which can massively bloat dist/).
$BuildVenv = Join-Path $Root ".venv-build"
$Py = Join-Path $BuildVenv "Scripts\python.exe"

if (-not $SkipBuild) {
  if (!(Test-Path $Py)) {
    Write-Host "[i] Creating build venv: .venv-build" -ForegroundColor Cyan
    python -m venv "$BuildVenv"
  }

  Write-Host "[i] Installing build dependencies..." -ForegroundColor Cyan
  & $Py -m pip install --upgrade pip setuptools wheel | Out-Null
  & $Py -m pip install -r "requirements.txt" | Out-Null

  Write-Host "[i] Running PyInstaller..." -ForegroundColor Cyan
  & $Py -m PyInstaller --noconfirm --clean "ProfesorAbelton.spec"
} else {
  Write-Host "[i] SkipBuild=ON - using existing dist/ output." -ForegroundColor Cyan
}

$distDir = Join-Path $Root "dist\ProfesorAbelton"
$exePath = Join-Path $distDir "ProfesorAbelton.exe"

if (!(Test-Path $exePath)) {
  throw "Build ok, ali EXE nije pronaden: $exePath"
}

# Make the Gumroad ZIP user-friendly:
# copy docs/config/RemoteScript next to the EXE (not only into _internal).
Write-Host "[i] Copying user-facing files next to the EXE..." -ForegroundColor Cyan
Copy-Item -Force (Join-Path $Root "LICENSE.txt") $distDir
Copy-Item -Force (Join-Path $Root "README.md") $distDir
Copy-Item -Force (Join-Path $Root "USER_MANUAL.md") $distDir
Copy-Item -Force (Join-Path $Root "FAQ.md") $distDir
Copy-Item -Force (Join-Path $Root "GUMROAD_README.txt") $distDir
Copy-Item -Recurse -Force (Join-Path $Root "Config") $distDir
Copy-Item -Recurse -Force (Join-Path $Root "RemoteScript") $distDir
Copy-Item -Recurse -Force (Join-Path $Root "Docs") $distDir

# Prepare release folder
$releaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

$zipName = "ProfesorAbelton_Windows_v$Version.zip"
$zipPath = Join-Path $releaseDir $zipName

if (Test-Path $zipPath) {
  try {
    Remove-Item $zipPath -Force
  } catch {
    # If the previous zip is locked (AV scan / explorer / previous run), write a new file instead.
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipName = "ProfesorAbelton_Windows_v$Version" + "_" + $stamp + ".zip"
    $zipPath = Join-Path $releaseDir $zipName
  }
}

Write-Host "[i] Zipping dist folder for Gumroad..." -ForegroundColor Cyan

# Zip the whole onedir folder so users can extract and run.
Compress-Archive -Path $distDir -DestinationPath $zipPath -Force

Write-Host "" 
Write-Host "[OK] Gumroad ZIP ready:" -ForegroundColor Green
Write-Host "     $zipPath"
Write-Host ""
Write-Host "Sadrzaj ZIP-a:" -ForegroundColor Gray
Write-Host " - ProfesorAbelton\ProfesorAbelton.exe"
Write-Host " - ProfesorAbelton\_internal\ (PyInstaller runtime)"
Write-Host " - ProfesorAbelton\Config\, RemoteScript\, Docs\, USER_MANUAL.md, FAQ.md, LICENSE.txt, GUMROAD_README.txt"
Write-Host ""

