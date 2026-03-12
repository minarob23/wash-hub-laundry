# 🧺 نظام إدارة المغسلة - دليل التطوير

## 📁 هيكل المشروع

```
سيستم مغسلة/
│
├── main.py                 # الملف الرئيسي للبرنامج
├── database.py             # مدير قاعدة البيانات
├── models.py               # نماذج البيانات (Models)
├── customer_manager.py     # نافذة إدارة العملاء
├── product_manager.py      # نافذة إدارة المنتجات
│
├── requirements.txt        # المكتبات المطلوبة
├── run.bat                 # ملف تشغيل سريع
├── README.md               # ملف تعريفي
├── USER_GUIDE.md           # دليل المستخدم
├── DEVELOPER_GUIDE.md      # دليل المطور (هذا الملف)
│
└── laundry_system.db       # قاعدة البيانات (يتم إنشاؤها تلقائياً)
```

---

## 🏗️ البنية المعمارية

### النمط المستخدم: MVC-like Pattern

1. **Model** (models.py):
   - تعريف نماذج البيانات
   - Customer, Product, Invoice, InvoiceItem

2. **View** (main.py, customer_manager.py, product_manager.py):
   - واجهة المستخدم الرسومية
   - CustomTkinter للواجهة الحديثة

3. **Controller** (database.py):
   - التعامل مع قاعدة البيانات
   - العمليات CRUD

---

## 🗄️ قاعدة البيانات

### SQLite Database Schema

#### جدول العملاء (customers)
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    address TEXT,
    trn_vat TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### جدول المنتجات (products)
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price_wash_press REAL DEFAULT 0,
    price_press_only REAL DEFAULT 0,
    price_wash_press_urgent REAL DEFAULT 0,
    price_press_urgent REAL DEFAULT 0,
    price_contract REAL DEFAULT 0,
    image_path TEXT
)
```

#### جدول الفواتير (invoices)
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER,
    date TEXT NOT NULL,
    delivery_date TEXT NOT NULL,
    delivery_time TEXT NOT NULL,
    service_type TEXT NOT NULL,
    customer_type TEXT DEFAULT 'Cash Customer',
    sales_man TEXT,
    depot TEXT,
    delivery_method TEXT DEFAULT 'PICKUP',
    status TEXT DEFAULT 'Hang',
    is_urgent INTEGER DEFAULT 0,
    is_fold INTEGER DEFAULT 0,
    is_tag INTEGER DEFAULT 0,
    remark TEXT,
    subtotal REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    vat REAL DEFAULT 0,
    total REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
)
```

#### جدول تفاصيل الفواتير (invoice_items)
```sql
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    product_id INTEGER,
    product_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price REAL NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
```

---

## 🎨 الواجهة الرسومية

### المكتبات المستخدمة:
- **CustomTkinter**: واجهة رسومية حديثة
- **Tkinter**: المكتبة الأساسية
- **ttk**: للجداول (Treeview)
- **Pillow**: لمعالجة الصور (مستقبلاً)

### الألوان المستخدمة:
```python
# الهيدر
header_bg = "#2b5797"

# التبويبات
wash_press = "#ADD8E6"      # أزرق فاتح
press_only = "#90EE90"      # أخضر فاتح
wash_press_ur = "#FFE4B5"   # بيج
press_urgent = "#DDA0DD"    # بنفسجي
contract = "#FFB6C1"        # وردي

# المنتجات
product_bg = "#E8F4F8"      # أزرق فاتح جداً
product_card_border = "#2b5797"
```

---

## 🔧 التطوير

### 1. إضافة منتج جديد برمجياً:

```python
from database import DatabaseManager
from models import Product

db = DatabaseManager()

product = Product(
    name="اسم المنتج",
    category="Wash & Press",
    price_wash_press=25.0,
    price_press_only=15.0,
    price_wash_press_urgent=35.0,
    price_press_urgent=25.0,
    price_contract=20.0
)

product_id = db.add_product(product)
```

### 2. البحث عن عميل:

```python
customer = db.get_customer_by_phone("0501234567")
if customer:
    print(f"العميل: {customer.name}")
```

### 3. حفظ فاتورة:

```python
from models import Invoice, InvoiceItem

# إنشاء الفاتورة
invoice = Invoice(
    invoice_number="3148",
    customer_id=1,
    date="12-03-2026",
    delivery_date="13-03-2026",
    delivery_time="3:31 AM",
    service_type="Wash & Press",
    subtotal=100.0,
    vat=5.0,
    total=105.0
)

# تفاصيل الفاتورة
items = [
    InvoiceItem(
        product_id=1,
        product_name="Jacket",
        quantity=2,
        price=25.0,
        total=50.0
    )
]

invoice_id = db.save_invoice(invoice, items)
```

---

## 🚀 إضافة ميزات جديدة

### إضافة تقرير جديد:

1. أنشئ ملف جديد: `reports.py`
```python
import customtkinter as ctk
from database import DatabaseManager

class ReportsWindow(ctk.CTkToplevel):
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.title("التقارير")
        # ... إضافة الكود
```

2. أضف الاستيراد في `main.py`:
```python
from reports import ReportsWindow
```

3. أضف الدالة في `LaundrySystem`:
```python
def show_daily_report(self):
    ReportsWindow(self, self)
```

### إضافة طباعة الفواتير:

1. أنشئ ملف: `printer.py`
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class InvoicePrinter:
    def print_invoice(self, invoice, items):
        # كود الطباعة
        pass
```

2. استخدمه في `main.py`:
```python
from printer import InvoicePrinter

def print_invoice(self):
    printer = InvoicePrinter()
    printer.print_invoice(self.current_invoice, self.cart_items)
```

---

## 🧪 الاختبار

### اختبار قاعدة البيانات:

```python
import unittest
from database import DatabaseManager
from models import Customer

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager("test.db")
    
    def test_add_customer(self):
        customer = Customer(
            phone="0501234567",
            name="Test Customer"
        )
        customer_id = self.db.add_customer(customer)
        self.assertIsNotNone(customer_id)
    
    def tearDown(self):
        import os
        os.remove("test.db")

if __name__ == '__main__':
    unittest.main()
```

---

## 📦 التعبئة والتوزيع

### إنشاء ملف تنفيذي (EXE):

#### باستخدام PyInstaller:

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --icon=icon.ico --name="LaundrySystem" main.py
```

#### سكريبت كامل:
```bash
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --name="LaundrySystem" ^
    --add-data="laundry_system.db;." ^
    main.py
```

---

## 🔒 الأمان

### نصائح الأمان:
1. لا تحفظ كلمات المرور في النص الصريح
2. استخدم تشفير للبيانات الحساسة
3. قم بعمل نسخ احتياطية منتظمة
4. تحقق من صلاحيات المستخدمين

### مثال على تشفير كلمة المرور:
```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed
```

---

## 📝 معايير الكود

### أسلوب الكتابة:
- اتبع PEP 8 لـ Python
- استخدم أسماء واضحة للمتغيرات والدوال
- أضف تعليقات للكود المعقد
- استخدم Docstrings للدوال والفئات

### مثال:
```python
def calculate_total(items: List[InvoiceItem], vat_rate: float = 0.05) -> float:
    """
    حساب الإجمالي النهائي مع الضريبة
    
    Args:
        items: قائمة عناصر الفاتورة
        vat_rate: نسبة الضريبة (افتراضي 5%)
    
    Returns:
        float: المبلغ الإجمالي شامل الضريبة
    """
    subtotal = sum(item.total for item in items)
    vat = subtotal * vat_rate
    return subtotal + vat
```

---

## 🐛 التصحيح (Debugging)

### تفعيل وضع التصحيح:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='laundry_system.log'
)

logger = logging.getLogger(__name__)
logger.debug('رسالة تصحيح')
```

---

## 🔄 Git والتحكم في الإصدارات

### .gitignore:
```
*.pyc
__pycache__/
*.db
*.log
build/
dist/
*.spec
```

### الأوامر الأساسية:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
```

---

## 📚 مصادر إضافية

### التوثيق:
- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [SQLite Docs](https://www.sqlite.org/docs.html)
- [Python Docs](https://docs.python.org/)

### دروس:
- GUI Development with CustomTkinter
- Database Design Best Practices
- Desktop App Development

---

## 🤝 المساهمة

لتحسين هذا المشروع:
1. Fork المشروع
2. أنشئ branch جديد
3. اعمل التعديلات
4. أرسل Pull Request

---

## 📞 الاتصال

للمزيد من المعلومات أو الدعم الفني، تواصل مع المطور.

---

**تم التحديث: مارس 2026**
