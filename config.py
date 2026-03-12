"""
ملف الإعدادات لنظام المغسلة
"""

import os

class Config:
    """إعدادات البرنامج"""
    
    # معلومات الشركة
    COMPANY_NAME = "AiFSoft Bt | WASH HUB LAUNDRY"
    COMPANY_NAME_AR = "نظام إدارة مغسلة"
    VERSION = "1.0"
    
    # قاعدة البيانات
    DATABASE_NAME = "laundry_system.db"
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    
    # الأسعار والضرائب
    VAT_RATE = 0.05  # 5% ضريبة القيمة المضافة
    DEFAULT_CURRENCY = "AED"
    
    # رقم الفاتورة
    INVOICE_START_NUMBER = 3147
    
    # تواريخ افتراضية
    DEFAULT_DELIVERY_DAYS = 1  # يوم واحد
    DEFAULT_DELIVERY_TIME = "3:31 AM"
    
    # أنواع الخدمات
    SERVICE_TYPES = {
        "Wash & Press": {
            "name_ar": "غسيل وكوي",
            "color": "#ADD8E6",
            "price_field": "price_wash_press"
        },
        "Pressing Only": {
            "name_ar": "كوي فقط",
            "color": "#90EE90",
            "price_field": "price_press_only"
        },
        "Wash & Press Ur": {
            "name_ar": "غسيل وكوي عاجل",
            "color": "#FFE4B5",
            "price_field": "price_wash_press_urgent"
        },
        "Pressing Urgent": {
            "name_ar": "كوي عاجل",
            "color": "#DDA0DD",
            "price_field": "price_press_urgent"
        },
        "Contract": {
            "name_ar": "عقد",
            "color": "#FFB6C1",
            "price_field": "price_contract"
        }
    }
    
    # أنواع العملاء
    CUSTOMER_TYPES = ["Cash Customer", "Credit Customer", "VIP"]
    
    # طرق التوصيل
    DELIVERY_METHODS = ["PICKUP", "Home Delivery"]
    
    # حالات الملابس
    CLOTH_STATUS = {
        "HANG": "علاقة",
        "FOLD": "مطوي",
        "URGENT": "عاجل"
    }
    
    # الألوان
    COLORS = {
        "primary": "#2b5797",
        "secondary": "#34495e",
        "success": "#27ae60",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "info": "#3498db",
        "light": "#ecf0f1",
        "dark": "#2c3e50",
        "white": "#ffffff"
    }
    
    # الخطوط
    FONTS = {
        "title": ("Segoe UI", 20, "bold"),
        "heading": ("Segoe UI", 16, "bold"),
        "normal": ("Segoe UI", 12),
        "small": ("Segoe UI", 10)
    }
    
    # حجم النافذة
    WINDOW_SIZE = {
        "width": 1400,
        "height": 800,
        "min_width": 1200,
        "min_height": 700
    }
    
    # الطباعة (قريباً)
    PRINT_SETTINGS = {
        "printer_type": "thermal",  # thermal, a4
        "paper_width": 80,  # مم
        "auto_print": False,
        "copies": 1
    }
    
    # النسخ الاحتياطي
    BACKUP_SETTINGS = {
        "auto_backup": True,
        "backup_folder": "backups",
        "backup_interval": "daily"  # daily, weekly, monthly
    }
    
    # اللغة
    DEFAULT_LANGUAGE = "ar"  # ar, en
    
    # التقارير
    REPORT_SETTINGS = {
        "export_format": "pdf",  # pdf, excel
        "include_logo": True,
        "page_size": "A4"
    }
    
    # الإشعارات
    NOTIFICATION_SETTINGS = {
        "whatsapp_enabled": False,
        "whatsapp_api": "",
        "sms_enabled": False,
        "sms_api": ""
    }


class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True
    DATABASE_NAME = "laundry_system_dev.db"


class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False


# الإعداد الحالي
current_config = Config  # غيّر إلى DevelopmentConfig للتطوير
