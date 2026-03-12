@echo off
chcp 65001 >nul
cls
echo.
echo ════════════════════════════════════════════════════════
echo    🧺 نظام إدارة المغسلة - تثبيت المكتبات
echo    AiFSoft Bt ^| WASH HUB LAUNDRY
echo ════════════════════════════════════════════════════════
echo.

REM التحقق من تثبيت Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python غير مثبت!
    echo.
    echo يرجى تثبيت Python 3.8 أو أحدث من:
    echo https://www.python.org/downloads/
    echo.
    echo تأكد من تفعيل خيار "Add Python to PATH" أثناء التثبيت
    echo.
    pause
    exit /b 1
)

echo ✅ Python مثبت بنجاح
python --version
echo.

echo ──────────────────────────────────────────────────────
echo 📦 تثبيت المكتبات المطلوبة...
echo ──────────────────────────────────────────────────────
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ ERROR: فشل تثبيت المكتبات!
    echo.
    echo جرب تشغيل الأمر التالي يدوياً:
    echo pip install customtkinter Pillow
    echo.
    pause
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════════════
echo ✅ تم تثبيت جميع المكتبات بنجاح!
echo ══════════════════════════════════════════════════════
echo.
echo الآن يمكنك تشغيل البرنامج باستخدام:
echo - run.bat
echo أو:
echo - python main.py
echo.
pause
