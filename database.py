"""
مدير قاعدة البيانات لنظام المغسلة
"""

import sqlite3
from typing import List, Optional, Tuple
from models import Customer, Product, Invoice, InvoiceItem


class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_path: str = "laundry_system.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """الاتصال بقاعدة البيانات"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """قطع الاتصال بقاعدة البيانات"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """إنشاء الجداول"""
        # جدول العملاء
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                trn_vat TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنتجات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
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
        ''')
        
        # جدول الفواتير
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
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
        ''')
        
        # جدول تفاصيل الفواتير
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
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
        ''')
        
        self.conn.commit()
    
    # ========== عمليات العملاء ==========
    
    def add_customer(self, customer: Customer) -> int:
        """إضافة عميل جديد"""
        self.cursor.execute('''
            INSERT INTO customers (phone, name, address, trn_vat)
            VALUES (?, ?, ?, ?)
        ''', (customer.phone, customer.name, customer.address, customer.trn_vat))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """البحث عن عميل بالهاتف"""
        self.cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        row = self.cursor.fetchone()
        if row:
            return Customer(*row)
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """الحصول على جميع العملاء"""
        self.cursor.execute('SELECT * FROM customers ORDER BY id DESC')
        return [Customer(*row) for row in self.cursor.fetchall()]
    
    def update_customer(self, customer: Customer):
        """تحديث بيانات عميل"""
        self.cursor.execute('''
            UPDATE customers SET name = ?, address = ?, trn_vat = ?
            WHERE id = ?
        ''', (customer.name, customer.address, customer.trn_vat, customer.id))
        self.conn.commit()
    
    # ========== عمليات المنتجات ==========
    
    def add_product(self, product: Product) -> int:
        """إضافة منتج جديد"""
        self.cursor.execute('''
            INSERT INTO products (name, category, price_wash_press, price_press_only,
                                price_wash_press_urgent, price_press_urgent, price_contract,
                                image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product.name, product.category, product.price_wash_press,
              product.price_press_only, product.price_wash_press_urgent,
              product.price_press_urgent, product.price_contract, product.image_path))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_products(self) -> List[Tuple]:
        """الحصول على جميع المنتجات"""
        self.cursor.execute('SELECT * FROM products ORDER BY name')
        return self.cursor.fetchall()
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """الحصول على منتج بالمعرف"""
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = self.cursor.fetchone()
        if row:
            return Product(*row)
        return None
    
    # ========== عمليات الفواتير ==========
    
    def get_next_invoice_number(self) -> str:
        """الحصول على رقم الفاتورة التالي"""
        self.cursor.execute('SELECT MAX(id) FROM invoices')
        result = self.cursor.fetchone()
        next_num = (result[0] or 0) + 1
        return str(3147 + next_num)
    
    def save_invoice(self, invoice: Invoice, items: List[InvoiceItem]) -> int:
        """حفظ فاتورة جديدة"""
        # إدراج الفاتورة
        self.cursor.execute('''
            INSERT INTO invoices (invoice_number, customer_id, date, delivery_date,
                                delivery_time, service_type, customer_type, sales_man,
                                depot, delivery_method, status, is_urgent, is_fold,
                                is_tag, remark, subtotal, discount, vat, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice.invoice_number, invoice.customer_id, invoice.date,
              invoice.delivery_date, invoice.delivery_time, invoice.service_type,
              invoice.customer_type, invoice.sales_man, invoice.depot,
              invoice.delivery_method, invoice.status, invoice.is_urgent,
              invoice.is_fold, invoice.is_tag, invoice.remark, invoice.subtotal,
              invoice.discount, invoice.vat, invoice.total))
        
        invoice_id = self.cursor.lastrowid
        
        # إدراج تفاصيل الفاتورة
        for item in items:
            self.cursor.execute('''
                INSERT INTO invoice_items (invoice_id, product_id, product_name,
                                          quantity, price, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (invoice_id, item.product_id, item.product_name, item.quantity,
                  item.price, item.total))
        
        self.conn.commit()
        return invoice_id
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """الحصول على فاتورة بالرقم"""
        self.cursor.execute('SELECT * FROM invoices WHERE invoice_number = ?',
                          (invoice_number,))
        row = self.cursor.fetchone()
        if row:
            return Invoice(*row)
        return None
    
    def get_invoice_items(self, invoice_id: int) -> List[InvoiceItem]:
        """الحصول على تفاصيل فاتورة"""
        self.cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?',
                          (invoice_id,))
        return [InvoiceItem(*row) for row in self.cursor.fetchall()]
    
    def get_recent_invoices(self, limit: int = 50) -> List[Invoice]:
        """الحصول على الفواتير الأخيرة"""
        self.cursor.execute('SELECT * FROM invoices ORDER BY id DESC LIMIT ?',
                          (limit,))
        return [Invoice(*row) for row in self.cursor.fetchall()]
