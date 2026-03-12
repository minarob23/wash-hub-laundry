@echo off
chcp 65001 >nul
:menu
cls
echo.
echo ════════════════════════════════════════════════════════
echo    🧺 نظام إدارة المغسلة
echo    AiFSoft Bt ^| WASH HUB LAUNDRY
echo ════════════════════════════════════════════════════════
echo.
echo    [1] تشغيل البرنامج
echo    [2] تثبيت المكتبات المطلوبة
echo    [3] عرض دليل الاستخدام
echo    [4] فحص المكتبات المثبتة
echo    [5] نسخة احتياطية من قاعدة البيانات
echo    [0] خروج
echo.
echo ════════════════════════════════════════════════════════
echo.

set /p choice="اختر رقماً (0-5): "

if "%choice%"=="1" goto run_app
if "%choice%"=="2" goto install
if "%choice%"=="3" goto show_guide
if "%choice%"=="4" goto check_libs
if "%choice%"=="5" goto backup
if "%choice%"=="0" goto exit
goto menu

:run_app
cls
echo ══════════════════════════════════════════════════════
echo 🚀 تشغيل البرنامج...
echo ══════════════════════════════════════════════════════
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ❌ حدث خطأ أثناء تشغيل البرنامج!
    echo.
    echo قد تحتاج إلى تثبيت المكتبات أولاً
    echo اختر الخيار [2] من القائمة
    echo.
    pause
)
goto menu

:install
cls
call install.bat
goto menu

:show_guide
cls
echo ══════════════════════════════════════════════════════
echo 📖 دليل الاستخدام السريع
echo ══════════════════════════════════════════════════════
echo.
echo 1. إصدار فاتورة جديدة:
echo    - أدخل بيانات العميل
echo    - اختر نوع الخدمة
echo    - اضغط على المنتجات
echo    - اضغط "Delivery & Save"
echo.
echo 2. البحث عن عميل:
echo    - أدخل رقم الهاتف
echo    - أو اضغط زر البحث 🔍
echo.
echo 3. استرجاع فاتورة:
echo    - اضغط "Retrieve"
echo    - أدخل رقم الفاتورة
echo.
echo للمزيد من التفاصيل، افتح ملف USER_GUIDE.md
echo.
pause
goto menu

:check_libs
cls
echo ══════════════════════════════════════════════════════
echo 🔍 فحص المكتبات المثبتة...
echo ══════════════════════════════════════════════════════
echo.
python --version
echo.
pip show customtkinter
echo ──────────────────────────────────────────────────────
pip show Pillow
echo.
pause
goto menu

:backup
cls
echo ══════════════════════════════════════════════════════
echo 💾 نسخة احتياطية من قاعدة البيانات
echo ══════════════════════════════════════════════════════
echo.
if not exist laundry_system.db (
    echo ❌ لا توجد قاعدة بيانات للنسخ الاحتياطي
    echo قم بتشغيل البرنامج مرة واحدة على الأقل
    echo.
    pause
    goto menu
)

if not exist backups mkdir backups
set timestamp=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
copy laundry_system.db backups\laundry_system_%timestamp%.db >nul

if errorlevel 1 (
    echo ❌ فشل إنشاء النسخة الاحتياطية
) else (
    echo ✅ تم إنشاء النسخة الاحتياطية بنجاح!
    echo الملف: backups\laundry_system_%timestamp%.db
)
echo.
pause
goto menu

:exit
cls
echo.
echo ════════════════════════════════════════════════════════
echo    شكراً لاستخدام نظام إدارة المغسلة
echo    AiFSoft Bt ^| WASH HUB LAUNDRY
echo ════════════════════════════════════════════════════════
echo.
timeout /t 2 >nul
exit
