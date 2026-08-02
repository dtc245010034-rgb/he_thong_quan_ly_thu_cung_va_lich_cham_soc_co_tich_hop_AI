@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Hệ thống Quản lý Thú cưng

echo ============================================================
echo   HE THONG QUAN LY THU CUNG ^& LICH CHAM SOC
echo ============================================================
echo.

REM --- Kiem tra moi truong ao ---
if not exist "venv\Scripts\python.exe" (
    echo [LOI] Chua co moi truong ao.
    echo.
    echo Mo terminal tai thu muc nay va chay:
    echo     python -m venv venv
    echo     venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

REM --- Tao file cau hinh neu chua co ---
if not exist "backend\.env" (
    echo [1/3] Tao file cau hinh backend\.env ...
    copy /y "backend\.env.example" "backend\.env" >nul
) else (
    echo [1/3] File cau hinh da co.
)

REM --- Khoi tao CSDL neu chua co ---
REM Flask dat CSDL SQLite duong dan tuong doi vao thu muc instance\
if not exist "instance\pet_care.db" (
    echo [2/3] Khoi tao co so du lieu va nap du lieu mau ...
    venv\Scripts\python.exe -m flask --app backend.app.main init-db
    venv\Scripts\python.exe -m flask --app backend.app.main seed-db
) else (
    echo [2/3] Co so du lieu da co, giu nguyen du lieu hien tai.
)

echo [3/3] Khoi dong ung dung ...
echo.
echo ------------------------------------------------------------
echo   Dia chi:   http://127.0.0.1:5000
echo.
echo   Tai khoan demo - mat khau deu la: demo1234
echo     admin      Quan ly     - so lieu tong quan, sua bang gia
echo     letan      Le tan      - dat lich, lap ho so, nhac tiem
echo     groomer1   Nhan vien   - chi thay lich cua minh
echo     chunuoi1   Chu nuoi    - chi thay thu cung nha minh
echo.
echo   Nhan Ctrl+C de dung server.
echo ------------------------------------------------------------
echo.

REM Doi 2 giay roi mo trinh duyet, de server kip khoi dong
start "" /b cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5000"

venv\Scripts\python.exe -m flask --app backend.app.main run

echo.
echo Server da dung.
pause
