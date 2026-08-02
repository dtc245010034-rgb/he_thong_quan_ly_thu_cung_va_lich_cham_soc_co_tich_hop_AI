@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Kiem thu he thong

echo ============================================================
echo   CHAY BO KIEM THU
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [LOI] Chua co moi truong ao. Xem huong dan trong README.md
    pause
    exit /b 1
)

echo Dang chay... mat khoang 2 phut.
echo.

venv\Scripts\python.exe -m pytest

echo.
echo ============================================================
pause
