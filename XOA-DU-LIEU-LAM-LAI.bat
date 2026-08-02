@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Xoa du lieu va nap lai tu dau

echo ============================================================
echo   XOA TOAN BO DU LIEU VA NAP LAI DU LIEU MAU
echo ============================================================
echo.
echo Thao tac nay se XOA co so du lieu hien tai va nap lai du
echo lieu mau ban dau. Moi thay doi ban da nhap se mat.
echo.

set /p XACNHAN="Go 'xoa' de xac nhan: "
if /i not "%XACNHAN%"=="xoa" (
    echo.
    echo Da huy. Khong co gi bi xoa.
    pause
    exit /b 0
)

echo.
if exist "instance" (
    rmdir /s /q "instance"
    echo Da xoa co so du lieu cu.
)

venv\Scripts\python.exe -m flask --app backend.app.main init-db
venv\Scripts\python.exe -m flask --app backend.app.main seed-db

echo.
echo Xong. Chay CHAY-HE-THONG.bat de mo ung dung.
pause
