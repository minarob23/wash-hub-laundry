@echo off
echo ====================================
echo   Laundry Management System
echo   نظام إدارة المغسلة
echo ====================================
echo.

REM التحقق من تثبيت Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python غير مثبت!
    echo يرجى تثبيت Python من https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] التحقق من المكتبات المطلوبة...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo.
    echo [2/3] تثبيت المكتبات المطلوبة...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: فشل تثبيت المكتبات!
        pause
        exit /b 1
    )
) else (
    echo [2/3] المكتبات المطلوبة مثبتة بالفعل
)

echo [3/3] تشغيل البرنامج...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: حدث خطأ أثناء تشغيل البرنامج!
    pause
)
