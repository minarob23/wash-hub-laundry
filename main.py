"""
نظام إدارة مغسلة - AiFSoft Bt | WASH HUB LAUNDRY
 برنامج كاشير احترافي لإدارة المغاسل
"""

import customtkinter as ctk
from tkinter import messagebox, ttk, Menu
import tkinter as tk
from datetime import datetime, timedelta
import sqlite3
from PIL import Image, ImageTk
import os
import sys

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد المكونات
from customer_manager import CustomerManagementWindow
from product_manager import ProductManagementWindow

# إعدادات المظهر
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LaundrySystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # إعدادات النافذة الرئيسية
        self.title("AP SOFT | WASH HUB LAUNDRY")
        self.geometry("1400x800")
        self.state('zoomed')  # ملء الشاشة
        
        # قاعدة البيانات
        self.init_database()
        
        # المتغيرات
        self.current_invoice = None
        self.cart_items = []
        self.customer_search_var = ctk.StringVar()
        self.product_search_var = ctk.StringVar()
        self.current_product_dialog = None  # تتبع نافذة المنتج الحالية
        self.modify_price_enabled = tk.BooleanVar(value=False)  # متغير MODIFY PRICE
        self.admin_menu_open = None  # تتبع نافذة قائمة الأدمن
        self._cached_position = None  # تخزين مؤقت للموضع
        
        # بناء الواجهة
        self.create_header()
        self.create_invoice_section()
        self.create_service_tabs()
        
        # تحميل البيانات
        self.load_next_invoice_number()
        
        # ربط أحداث تحديث الموضع
        self.bind('<Configure>', self._on_window_configure)
        
        # تحسين الأداء: حساب الموضع الأولي بعد إنشاء النافذة
        self.after(100, self._initialize_cached_position)
        
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        self.conn = sqlite3.connect('laundry_system.db')
        self.cursor = self.conn.cursor()
        
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
        
        # جدول المنتجات/الخدمات
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
        
        # جدول الملف الشخصي للأدمن
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT DEFAULT 'Admin',
                city TEXT DEFAULT '',
                location TEXT DEFAULT '',
                email TEXT DEFAULT '',
                telephone TEXT DEFAULT '',
                fax TEXT DEFAULT '',
                mobile TEXT DEFAULT '',
                address TEXT DEFAULT '',
                display_name TEXT DEFAULT '',
                ext_email TEXT DEFAULT '',
                password TEXT DEFAULT ''
            )
        ''')
        
        self.conn.commit()
        
        # إضافة سجل افتراضي للملف الشخصي إذا لم يكن موجوداً
        self.cursor.execute('SELECT COUNT(*) FROM admin_profile')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO admin_profile (name) VALUES ('Admin')")
            self.conn.commit()
        
        # إضافة بيانات تجريبية إذا كانت الجداول فارغة
        self.cursor.execute('SELECT COUNT(*) FROM products')
        if self.cursor.fetchone()[0] == 0:
            self.add_sample_products()
    
    def add_sample_products(self):
        """إضافة منتجات تجريبية"""
        products = [
            ('Jacket', 'Wash & Press', 25, 15, 35, 25, 20),
            ('Trouser', 'Wash & Press', 15, 10, 25, 15, 12),
            ('Pullovers', 'Wash & Press', 20, 12, 30, 20, 15),
            ('Shirt', 'Wash & Press', 12, 8, 20, 12, 10),
            ('White Dishdasha', 'Wash & Press', 18, 12, 28, 18, 15),
            ('Ghutra Wool', 'Wash & Press', 15, 10, 25, 15, 12),
            ('Ghutra White', 'Wash & Press', 12, 8, 20, 12, 10),
            ('Vest', 'Wash & Press', 15, 10, 25, 15, 12),
            ('Socks', 'Wash & Press', 5, 3, 8, 5, 4),
            ('Lungi', 'Wash & Press', 10, 6, 15, 10, 8),
            ('Skirt', 'Wash & Press', 15, 10, 25, 15, 12),
            ('Frock', 'Wash & Press', 20, 15, 30, 20, 18),
            ('Dressing Gown', 'Wash & Press', 30, 20, 45, 30, 25),
            ('Lady Suit', 'Wash & Press', 35, 25, 50, 35, 30),
            ('Dress Cotton', 'Wash & Press', 25, 18, 38, 25, 22),
            ('Night Dress', 'Wash & Press', 20, 15, 30, 20, 18),
            ('Abaya', 'Wash & Press', 22, 15, 32, 22, 18),
            ('Sheila', 'Wash & Press', 8, 5, 12, 8, 6),
        ]
        
        for product in products:
            self.cursor.execute('''
                INSERT INTO products (name, category, price_wash_press, price_press_only, 
                                    price_wash_press_urgent, price_press_urgent, price_contract)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', product)
        
        self.conn.commit()
    
    def create_header(self):
        """إنشاء شريط العنوان"""
        header = ctk.CTkFrame(self, fg_color="#2b5797", height=50)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # العنوان
        title_label = ctk.CTkLabel(
            header,
            text="🧺 AP SOFT | WASH HUB LAUNDRY",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20)
        
        # الوقت والتاريخ
        current_time = datetime.now().strftime("%I:%M:%S %p Thurs, %d %b %Y")
        time_label = ctk.CTkLabel(
            header,
            text=current_time,
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        time_label.pack(side="right", padx=20)
        
        # اسم المستخدم - زر بقائمة منسدلة
        user_btn = ctk.CTkButton(
            header,
            text="👤 Admin ▼",
            font=ctk.CTkFont(size=14),
            text_color="white",
            fg_color="#2b5797",
            hover_color="#1e3d6b",
            corner_radius=5,
            command=self.show_admin_menu
        )
        user_btn.pack(side="right", padx=10)
    
    def create_invoice_section(self):
        """قسم معلومات الفاتورة"""
        invoice_frame = ctk.CTkFrame(self, fg_color="#34495e")
        invoice_frame.pack(fill="x", padx=10, pady=5)
        
        # الصف الأول
        row1 = ctk.CTkFrame(invoice_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)
        
        # رقم الفاتورة
        ctk.CTkLabel(row1, text="Next Inv. No", text_color="white").grid(row=0, column=0, padx=5, sticky="w")
        
        # إنشاء frame لرقم الفاتورة مع أزرار التنقل
        invoice_frame = ctk.CTkFrame(row1, fg_color="transparent")
        invoice_frame.grid(row=0, column=1, padx=5)
        
        # زر السابق
        prev_btn = ctk.CTkButton(
            invoice_frame,
            text="◀",
            width=30,
            height=28,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.previous_invoice
        )
        prev_btn.pack(side="left", padx=(0, 2))
        
        # حقل رقم الفاتورة
        self.invoice_number_entry = ctk.CTkEntry(invoice_frame, width=90)
        self.invoice_number_entry.pack(side="left")
        
        # زر التالي
        next_btn = ctk.CTkButton(
            invoice_frame,
            text="▶",
            width=30,
            height=28,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.next_invoice
        )
        next_btn.pack(side="left", padx=(2, 0))
        
        # الصف الثاني من row1 - التواريخ والملاحظات
        dates_row = ctk.CTkFrame(invoice_frame, fg_color="transparent")
        dates_row.pack(fill="x", padx=10, pady=5)
        
        # التاريخ
        ctk.CTkLabel(dates_row, text="Date", text_color="white").grid(row=0, column=0, padx=5, sticky="w")
        self.date_entry = ctk.CTkEntry(dates_row, width=120)
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.date_entry.grid(row=0, column=1, padx=5)
        
        # تاريخ التسليم
        ctk.CTkLabel(dates_row, text="Delivery Date", text_color="white").grid(row=0, column=2, padx=5, sticky="w")
        self.delivery_date_entry = ctk.CTkEntry(dates_row, width=120)
        self.delivery_date_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y"))
        self.delivery_date_entry.grid(row=0, column=3, padx=5)
        
        # وقت التسليم
        ctk.CTkLabel(dates_row, text="Delivery Time", text_color="white").grid(row=0, column=4, padx=5, sticky="w")
        self.delivery_time_entry = ctk.CTkEntry(dates_row, width=100)
        self.delivery_time_entry.insert(0, "3:31 AM")
        self.delivery_time_entry.grid(row=0, column=5, padx=5)
        
        # ملاحظات
        ctk.CTkLabel(dates_row, text="Remark", text_color="white").grid(row=0, column=6, padx=5, sticky="w")
        self.remark_entry = ctk.CTkEntry(dates_row, width=300)
        self.remark_entry.grid(row=0, column=7, padx=5)
        
        # الصف الثاني
        row2 = ctk.CTkFrame(invoice_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)
        
        # العميل
        ctk.CTkLabel(row2, text="Customer", text_color="white").grid(row=0, column=0, padx=5, sticky="w")
        self.customer_entry = ctk.CTkEntry(row2, width=150)
        self.customer_entry.insert(0, "0000000000")
        self.customer_entry.grid(row=0, column=1, padx=5)
        self.customer_entry.bind('<KeyRelease>', self.search_customer)
        
        # بحث العميل
        search_btn = ctk.CTkButton(row2, text="🔍", width=30, command=self.show_customer_search)
        search_btn.grid(row=0, column=2, padx=2)
        
        # اسم العميل
        self.customer_name_entry = ctk.CTkEntry(row2, width=200)
        self.customer_name_entry.insert(0, "Cash Customer")
        self.customer_name_entry.grid(row=0, column=3, padx=5)
        
        # عنوان العميل
        self.customer_address_entry = ctk.CTkEntry(row2, width=200)
        self.customer_address_entry.insert(0, "Cash Customer address1")
        self.customer_address_entry.grid(row=0, column=4, padx=5)
        
        # TRN/VAT
        self.trn_entry = ctk.CTkEntry(row2, width=150)
        self.trn_entry.insert(0, "TRN(VAT-TIN)")
        self.trn_entry.grid(row=0, column=5, padx=5)
        
        # WhatsApp
        whatsapp_btn = ctk.CTkButton(row2, text="💬", width=30, fg_color="green")
        whatsapp_btn.grid(row=0, column=6, padx=2)
        
        # نوع التوصيل
        delivery_frame = ctk.CTkFrame(row2, fg_color="transparent")
        delivery_frame.grid(row=0, column=7, padx=20)
        
        self.delivery_var = ctk.StringVar(value="PICKUP")
        
        self.pickup_radio = ctk.CTkRadioButton(
            delivery_frame, 
            text="● PICKUP", 
            variable=self.delivery_var,
            value="PICKUP",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.pickup_radio.pack(side="left", padx=5)
        
        self.home_delivery_radio = ctk.CTkRadioButton(
            delivery_frame, 
            text="○ Home Delivery",
            variable=self.delivery_var,
            value="Home Delivery",
            font=ctk.CTkFont(size=13),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.home_delivery_radio.pack(side="left", padx=5)
        
        # الصف الثالث
        row3 = ctk.CTkFrame(invoice_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=5)
        
        # نوع العميل
        ctk.CTkLabel(row3, text="C Type", text_color="white").grid(row=0, column=0, padx=5, sticky="w")
        self.customer_type = ctk.CTkComboBox(row3, values=["Cash Customer", "Credit Customer", "VIP"], width=150)
        self.customer_type.set("Cash Customer")
        self.customer_type.grid(row=0, column=1, padx=5)
        
        # المندوب
        ctk.CTkLabel(row3, text="Sales Man", text_color="white").grid(row=0, column=2, padx=5, sticky="w")
        self.sales_man = ctk.CTkComboBox(row3, values=["None", "Ahmed", "Mohamed", "Ali"], width=150)
        self.sales_man.grid(row=0, column=3, padx=5)
        
        # المستودع
        ctk.CTkLabel(row3, text="Depot", text_color="white").grid(row=0, column=4, padx=5, sticky="w")
        self.depot = ctk.CTkComboBox(row3, values=["NIL", "Depot 1", "Depot 2"], width=150)
        self.depot.set("NIL")
        self.depot.grid(row=0, column=5, padx=5)
        
        # عرض التاريخ الحالي
        date_display_frame = ctk.CTkFrame(row3, fg_color="#34495e", corner_radius=8)
        date_display_frame.grid(row=0, column=6, padx=20, sticky="e")
        
        ctk.CTkLabel(
            date_display_frame,
            text="Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=(10, 5), pady=5)
        
        current_date_str = datetime.now().strftime("%d-%m-%Y")
        ctk.CTkLabel(
            date_display_frame,
            text=current_date_str,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3498db"
        ).pack(side="left", padx=(0, 10), pady=5)
    
    def create_service_tabs(self):
        """إنشاء تبويبات الخدمات"""
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # الجزء الأيسر - المنتجات
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # التبويبات
        tabs_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=5, pady=5)
        
        self.service_type = ctk.StringVar(value="Wash & Press")
        
        services = [
            ("Wash & Press", "#ADD8E6"),
            ("Pressing Only", "#90EE90"),
            ("Wash & Press Ur", "#FFE4B5"),
            ("Pressing Urgent", "#DDA0DD"),
            ("Contract", "#FFB6C1")
        ]
        
        # تخزين أزرار الخدمات والألوان الأصلية
        self.service_buttons = {}
        self.service_colors = {}
        
        hover_colors = {
            "#ADD8E6": "#87CEEB",
            "#90EE90": "#7FDD7F",
            "#FFE4B5": "#FFD094",
            "#DDA0DD": "#CC90CC",
            "#FFB6C1": "#FFA0A0"
        }
        
        for i, (service, color) in enumerate(services):
            hover_col = hover_colors.get(color, color)
            btn = ctk.CTkButton(
                tabs_frame,
                text=service,
                command=lambda s=service: self.change_service_type(s),
                fg_color=color,
                text_color="black",
                hover_color=hover_col,
                width=140,
                height=40,
                border_width=0,
                border_color=color
            )
            btn.pack(side="left", padx=2)
            self.service_buttons[service] = btn
            self.service_colors[service] = color
        
        self.service_hover_colors = hover_colors
        
        # تعيين الزر الأول كمحدد
        self.update_service_button_colors("Wash & Press")
        
        # بحث المنتج
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=5, pady=5)
        
        self.scan_cloth_entry = ctk.CTkEntry(search_frame, placeholder_text="Scan Cloth", width=200)
        self.scan_cloth_entry.pack(side="left", padx=5)
        self.scan_cloth_entry.bind('<Return>', self.scan_cloth)
        
        self.search_product_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Product", width=200)
        self.search_product_entry.pack(side="left", padx=5)
        self.search_product_entry.bind('<KeyRelease>', self.search_product_live)
        
        # Checkbox لتفعيل تعديل السعر
        self.modify_price_checkbox = ctk.CTkCheckBox(
            search_frame, 
            text="MODIFY PRICE",
            variable=self.modify_price_enabled,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.modify_price_checkbox.pack(side="right", padx=5)
        
        # عرض المنتجات
        self.products_frame = ctk.CTkScrollableFrame(left_panel, fg_color="#E8F4F8")
        self.products_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.load_products()
        
        # الجزء الأيمن - السلة والإعدادات
        right_panel = ctk.CTkFrame(main_container, width=450)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        right_panel.pack_propagate(False)
        
        self.create_cart_section(right_panel)
    
    def create_cart_section(self, parent):
        """قسم سلة المشتريات والإجماليات"""
        # أزرار الحالة - نظام اختيار واحد فقط
        status_frame = ctk.CTkFrame(parent, fg_color="white")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        buttons_row1 = ctk.CTkFrame(status_frame, fg_color="transparent")
        buttons_row1.pack(fill="x", pady=5)
        
        # متغير واحد لتتبع الاختيار: 0=Urgent, 1=Hang, 2=Fold
        self.status_option = ctk.IntVar(value=1)  # الافتراضي Hang
        
        # زر Urgent
        self.urgent_btn = ctk.CTkButton(
            buttons_row1, 
            text="Urgent", 
            width=120, 
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            text_color="white",
            corner_radius=8,
            command=lambda: self.select_status(0)
        )
        self.urgent_btn.pack(side="left", padx=5)
        
        # زر Hang
        self.hang_btn = ctk.CTkButton(
            buttons_row1, 
            text="● Hang", 
            width=120, 
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            text_color="white",
            corner_radius=8,
            command=lambda: self.select_status(1)
        )
        self.hang_btn.pack(side="left", padx=5)
        
        # زر Fold
        self.fold_btn = ctk.CTkButton(
            buttons_row1, 
            text="Fold", 
            width=120, 
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            text_color="white",
            corner_radius=8,
            command=lambda: self.select_status(2)
        )
        self.fold_btn.pack(side="left", padx=5)
        
        # TAG
        tag_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        tag_frame.pack(fill="x", pady=5)
        
        self.tag_var = ctk.IntVar(value=1)
        tag_switch = ctk.CTkSwitch(
            tag_frame, 
            text="TAG",
            variable=self.tag_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            progress_color="#2ecc71",
            button_color="#e0e0e0",
            button_hover_color="#bdc3c7"
        )
        tag_switch.pack(pady=3)
        
        # أزرار Menu و Search
        menu_search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        menu_search_frame.pack(fill="x", padx=10, pady=(5, 3))
        
        # Search button
        search_btn = ctk.CTkButton(
            menu_search_frame,
            text="Search",
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27ae60",
            hover_color="#229954",
            text_color="white",
            corner_radius=20,
            border_width=0,
            command=self.show_search_dialog
        )
        search_btn.pack(side="right", padx=2)
        
        # Menu button
        menu_btn = ctk.CTkButton(
            menu_search_frame,
            text="☰ Menu",
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            text_color="white",
            corner_radius=20,
            border_width=0,
            command=self.show_menu_dialog
        )
        menu_btn.pack(side="right", padx=2)
        
        # الأزرار الستة الرئيسية - تصميم محسّن
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=3)
        
        # الصف الأول من الأزرار
        row1 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        row1.pack(pady=2)
        
        # Split button
        ctk.CTkButton(
            row1,
            text="Split ⇄",
            width=105,
            height=42,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#AED6F1",
            hover_color="#85C1E2",
            text_color="#1C2833",
            corner_radius=10,
            border_width=0,
            command=self.split_invoice
        ).pack(side="left", padx=2)
        
        # New Order button
        new_order_btn = ctk.CTkButton(
            row1,
            text="New Order",
            width=105,
            height=42,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#F9E79F",
            hover_color="#F4D03F",
            text_color="#1C2833",
            corner_radius=10,
            border_width=0,
            command=self.new_order
        )
        new_order_btn.pack(side="left", padx=2)
        
        # Retrieve button
        retrieve_btn = ctk.CTkButton(
            row1,
            text="Retrieve",
            width=105,
            height=42,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#EB984E",
            hover_color="#DC7633",
            text_color="white",
            corner_radius=10,
            border_width=0,
            command=self.retrieve_invoice
        )
        retrieve_btn.pack(side="left", padx=2)
        
        # الصف الثاني من الأزرار
        row2 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        row2.pack(pady=2)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            row2,
            text="Clear 🗑\nClear All",
            width=105,
            height=42,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#EC7063",
            hover_color="#CB4335",
            text_color="white",
            corner_radius=10,
            border_width=0,
            command=self.clear_cart
        )
        clear_btn.pack(side="left", padx=2)
        
        # Quick Delivery button
        quick_delivery_btn = ctk.CTkButton(
            row2,
            text="Quick Delivery ➕",
            width=105,
            height=42,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#ABEBC6",
            hover_color="#82E0AA",
            text_color="#1C2833",
            corner_radius=10,
            border_width=0,
            command=self.quick_delivery
        )
        quick_delivery_btn.pack(side="left", padx=2)
        
        # Delivery & Save button
        save_btn = ctk.CTkButton(
            row2,
            text="Delivery & Save 📋",
            width=105,
            height=42,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#48C9B0",
            hover_color="#17A589",
            text_color="white",
            corner_radius=10,
            border_width=0,
            command=self.save_invoice
        )
        save_btn.pack(side="left", padx=2)
        
        # Notifications
        notif_btn = ctk.CTkButton(parent, text="Notifications", fg_color="#E8E8E8", 
                                 text_color="black", height=30)
        notif_btn.pack(fill="x", padx=10, pady=3)
        
        # عرض عناصر السلة - بطاقات بدلاً من جدول
        self.cart_items_frame = ctk.CTkScrollableFrame(parent, fg_color="#f0f0f0", height=180)
        self.cart_items_frame.pack(fill="both", padx=10, pady=(3, 3))
        
        # الإجماليات - ثابتة في الأسفل
        totals_frame = ctk.CTkFrame(parent, fg_color="white", height=85)
        totals_frame.pack(fill="x", padx=10, pady=(3, 5))
        totals_frame.pack_propagate(False)
        
        # الصف الأول من الإجماليات (العناوين)
        totals_row = ctk.CTkFrame(totals_frame, fg_color="transparent")
        totals_row.pack(fill="x", pady=3)
        
        # تحديد عرض موحد للأعمدة
        col_width = 70
        
        ctk.CTkLabel(totals_row, text="Sub Total", font=ctk.CTkFont(size=11), width=col_width).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(totals_row, text="Discount", font=ctk.CTkFont(size=11), width=col_width).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(totals_row, text="Quantity", font=ctk.CTkFont(size=11), width=col_width).grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkLabel(totals_row, text="Vat", font=ctk.CTkFont(size=11), width=col_width).grid(row=0, column=3, padx=5, sticky="ew")
        ctk.CTkLabel(totals_row, text="Total", font=ctk.CTkFont(size=13, weight="bold"), width=col_width).grid(row=0, column=4, padx=5, sticky="ew")
        
        # ضبط أوزان الأعمدة
        for i in range(5):
            totals_row.grid_columnconfigure(i, weight=1, minsize=col_width)
        
        # القيم
        values_row = ctk.CTkFrame(totals_frame, fg_color="transparent")
        values_row.pack(fill="x", pady=3)
        
        self.subtotal_label = ctk.CTkLabel(values_row, text="0", font=ctk.CTkFont(size=12), width=col_width)
        self.subtotal_label.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.discount_label = ctk.CTkLabel(values_row, text="0", font=ctk.CTkFont(size=12), width=col_width)
        self.discount_label.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.quantity_label = ctk.CTkLabel(values_row, text="0", font=ctk.CTkFont(size=12), width=col_width)
        self.quantity_label.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.vat_label = ctk.CTkLabel(values_row, text="0", font=ctk.CTkFont(size=12), width=col_width)
        self.vat_label.grid(row=0, column=3, padx=5, sticky="ew")
        
        self.total_label = ctk.CTkLabel(values_row, text="0", font=ctk.CTkFont(size=16, weight="bold"), width=col_width)
        self.total_label.grid(row=0, column=4, padx=5, sticky="ew")
        
        # ضبط أوزان الأعمدة
        for i in range(5):
            values_row.grid_columnconfigure(i, weight=1, minsize=col_width)
    
    
    def create_footer(self):
        """إنشاء الأزرار السفلية - تم نقل جميع الأزرار إلى الجانب الأيمن"""
        pass
    
    def select_status(self, option):
        """اختيار حالة واحدة فقط (Urgent, Hang, أو Fold)"""
        self.status_option.set(option)
        
        # إعادة تعيين جميع الأزرار للون الرمادي
        self.urgent_btn.configure(fg_color="#95a5a6", text="Urgent")
        self.hang_btn.configure(fg_color="#95a5a6", text="Hang")
        self.fold_btn.configure(fg_color="#95a5a6", text="Fold")
        
        # تفعيل الزر المختار
        if option == 0:  # Urgent
            self.urgent_btn.configure(fg_color="#e74c3c", text="● Urgent")
        elif option == 1:  # Hang
            self.hang_btn.configure(fg_color="#34495e", text="● Hang")
        elif option == 2:  # Fold
            self.fold_btn.configure(fg_color="#34495e", text="● Fold")
    
    def toggle_urgent(self):
        """Deprecated - استبدل بـ select_status"""
        self.select_status(0)
    
    def toggle_hang(self):
        """Deprecated - استبدل بـ select_status"""
        self.select_status(1)
    
    def toggle_fold(self):
        """Deprecated - استبدل بـ select_status"""
        self.select_status(2)
    
    def new_order(self):
        """بدء فاتورة جديدة"""
        self.cart_items = []
        self.update_cart_display()
        self.load_next_invoice_number()
        self.customer_entry.delete(0, 'end')
        self.customer_entry.insert(0, "0000000000")
        self.customer_name_entry.delete(0, 'end')
        self.customer_name_entry.insert(0, "Cash Customer")
        self.customer_address_entry.delete(0, 'end')
        self.customer_address_entry.insert(0, "Cash Customer address1")
        self.trn_entry.delete(0, 'end')
        self.trn_entry.insert(0, "TRN(VAT-TIN)")
        self.remark_entry.delete(0, 'end')
        self.select_status(1)  # إعادة تعيين الحالة إلى Hang
    
    def clear_cart(self):
        """مسح السلة"""
        if messagebox.askyesno("مسح السلة", "هل أنت متأكد من مسح جميع المنتجات؟"):
            self.cart_items = []
            self.update_cart_display()
    
    def retrieve_invoice(self):
        """استرجاع فاتورة"""
        messagebox.showinfo("استرجاع فاتورة", "سيتم إضافة هذه الميزة قريباً")
    
    def save_invoice(self):
        """حفظ الفاتورة"""
        if not self.cart_items:
            messagebox.showwarning("تحذير", "السلة فارغة!")
            return
        
        try:
            # حفظ الفاتورة
            invoice_number = self.invoice_number_entry.get()
            customer_phone = self.customer_entry.get()
            
            # البحث عن العميل أو إنشاء عميل جديد
            self.cursor.execute('SELECT id FROM customers WHERE phone = ?', (customer_phone,))
            customer = self.cursor.fetchone()
            
            if not customer:
                # إنشاء عميل جديد
                self.cursor.execute('''
                    INSERT INTO customers (phone, name, address, trn_vat)
                    VALUES (?, ?, ?, ?)
                ''', (customer_phone, self.customer_name_entry.get(),
                     self.customer_address_entry.get(), self.trn_entry.get()))
                customer_id = self.cursor.lastrowid
            else:
                customer_id = customer[0]
            
            # حساب الإجماليات
            subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
            discount = 0
            vat = subtotal * 0.05  # 5% VAT
            total = subtotal - discount + vat
            
            # تحديد الحالة من status_option (0=Urgent, 1=Hang, 2=Fold)
            status_val = self.status_option.get()
            status_text = "Urgent" if status_val == 0 else "Hang" if status_val == 1 else "Fold"
            is_urgent = 1 if status_val == 0 else 0
            is_fold = 1 if status_val == 2 else 0
            
            # إدراج الفاتورة
            self.cursor.execute('''
                INSERT INTO invoices (invoice_number, customer_id, date, delivery_date,
                                    delivery_time, service_type, customer_type, sales_man,
                                    depot, delivery_method, status, is_urgent, is_fold,
                                    is_tag, remark, subtotal, discount, vat, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (invoice_number, customer_id, self.date_entry.get(),
                 self.delivery_date_entry.get(), self.delivery_time_entry.get(),
                 self.service_type.get(), self.customer_type.get(),
                 self.sales_man.get(), self.depot.get(), self.delivery_var.get(),
                 status_text, is_urgent, is_fold, self.tag_var.get(),
                 self.remark_entry.get(), subtotal, discount, vat, total))
            
            invoice_id = self.cursor.lastrowid
            
            # إدراج تفاصيل الفاتورة
            for item in self.cart_items:
                self.cursor.execute('''
                    INSERT INTO invoice_items (invoice_id, product_id, product_name,
                                              quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (invoice_id, item['id'], item['name'], item['quantity'],
                     item['price'], item['price'] * item['quantity']))
            
            self.conn.commit()
            
            # سؤال المستخدم عن الطباعة
            if messagebox.askyesno("نجاح", f"تم حفظ الفاتورة رقم {invoice_number} بنجاح!\n\nهل تريد طباعة الفاتورة؟"):
                self.print_invoice_by_id(invoice_id)
            
            # بدء فاتورة جديدة
            self.new_order()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ الفاتورة: {str(e)}")

    def print_invoice_by_id(self, invoice_id):
        """طباعة فاتورة موجودة بالـ ID"""
        try:
            # جلب بيانات الفاتورة
            self.cursor.execute('''
                SELECT i.*, c.name, c.phone, c.address, c.trn_vat
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                WHERE i.id = ?
            ''', (invoice_id,))
            inv = self.cursor.fetchone()
            if not inv:
                return
            
            # جلب تفاصيل الفاتورة
            self.cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
            items = self.cursor.fetchall()
            
            self._generate_and_print_receipt(inv, items)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء طباعة الفاتورة: {str(e)}")

    def print_current_invoice(self):
        """طباعة الفاتورة الحالية في السلة (قبل الحفظ)"""
        if not self.cart_items:
            messagebox.showwarning("تحذير", "السلة فارغة! أضف منتجات أولاً.")
            return
        
        # بناء بيانات مؤقتة للطباعة
        invoice_number = self.invoice_number_entry.get()
        customer_name = self.customer_name_entry.get()
        customer_phone = self.customer_entry.get()
        customer_address = self.customer_address_entry.get()
        trn_vat = self.trn_entry.get()
        date_val = self.date_entry.get()
        delivery_date = self.delivery_date_entry.get()
        delivery_time = self.delivery_time_entry.get()
        service_type = self.service_type.get()
        remark = self.remark_entry.get()
        
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
        discount = 0
        vat = subtotal * 0.05
        total = subtotal - discount + vat
        
        # توليد HTML للفاتورة وطباعتها
        items_rows = ""
        for idx, item in enumerate(self.cart_items, 1):
            item_total = item['price'] * item['quantity']
            items_rows += f"""
            <tr>
                <td>{idx}</td>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
                <td>{item['price']:.2f}</td>
                <td>{item_total:.2f}</td>
            </tr>"""
        
        html = self._build_receipt_html(
            invoice_number, customer_name, customer_phone, customer_address,
            trn_vat, date_val, delivery_date, delivery_time, service_type,
            remark, items_rows, subtotal, discount, vat, total
        )
        self._open_print_window(html)

    def _generate_and_print_receipt(self, inv, items):
        """توليد وطباعة إيصال الدفع"""
        # inv columns: id, invoice_number, customer_id, date, delivery_date, delivery_time,
        #              service_type, customer_type, sales_man, depot, delivery_method,
        #              status, is_urgent, is_fold, is_tag, remark, subtotal, discount,
        #              vat, total, created_at, name, phone, address, trn_vat
        invoice_number = inv[1]
        date_val       = inv[3]
        delivery_date  = inv[4]
        delivery_time  = inv[5]
        service_type   = inv[6]
        remark         = inv[15] or ""
        subtotal       = inv[16]
        discount       = inv[17]
        vat            = inv[18]
        total          = inv[19]
        customer_name  = inv[21] or "Cash Customer"
        customer_phone = inv[22] or ""
        customer_address = inv[23] or ""
        trn_vat        = inv[24] or ""
        
        items_rows = ""
        for idx, item in enumerate(items, 1):
            # item: id, invoice_id, product_id, product_name, quantity, price, total
            items_rows += f"""
            <tr>
                <td>{idx}</td>
                <td>{item[3]}</td>
                <td>{item[4]}</td>
                <td>{item[5]:.2f}</td>
                <td>{item[6]:.2f}</td>
            </tr>"""
        
        html = self._build_receipt_html(
            invoice_number, customer_name, customer_phone, customer_address,
            trn_vat, date_val, delivery_date, delivery_time, service_type,
            remark, items_rows, subtotal, discount, vat, total
        )
        self._open_print_window(html)

    def _build_receipt_html(self, invoice_number, customer_name, customer_phone,
                             customer_address, trn_vat, date_val, delivery_date,
                             delivery_time, service_type, remark, items_rows,
                             subtotal, discount, vat, total):
        """بناء HTML الفاتورة"""
        return f"""<!DOCTYPE html>
<html dir="ltr">
<head>
<meta charset="UTF-8">
<title>Invoice #{invoice_number}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: Arial, sans-serif; font-size: 13px; color: #222; padding: 20px; }}
  .header {{ text-align: center; border-bottom: 2px solid #2b5797; padding-bottom: 10px; margin-bottom: 15px; }}
  .header h1 {{ color: #2b5797; font-size: 22px; }}
  .header p {{ color: #555; font-size: 12px; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
  .info-block {{ background: #f5f8ff; border: 1px solid #d0daf0; border-radius: 6px; padding: 8px 12px; }}
  .info-block label {{ font-size: 11px; color: #777; display: block; }}
  .info-block span {{ font-weight: bold; color: #222; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
  th {{ background: #2b5797; color: white; padding: 8px; text-align: left; font-size: 12px; }}
  td {{ padding: 7px 8px; border-bottom: 1px solid #eee; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  .totals {{ width: 300px; margin-left: auto; border: 1px solid #d0daf0; border-radius: 6px; overflow: hidden; }}
  .totals tr td:first-child {{ color: #555; padding: 6px 12px; }}
  .totals tr td:last-child {{ text-align: right; font-weight: bold; padding: 6px 12px; }}
  .totals .grand-total td {{ background: #2b5797; color: white; font-size: 15px; }}
  .footer {{ text-align: center; margin-top: 20px; color: #777; font-size: 11px; border-top: 1px solid #ddd; padding-top: 10px; }}
  @media print {{
    body {{ padding: 5px; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>🧺 WASH HUB LAUNDRY</h1>
  <p>AP SOFT System | Professional Laundry Management</p>
</div>

<div class="info-grid">
  <div class="info-block">
    <label>Invoice No.</label>
    <span>#{invoice_number}</span>
  </div>
  <div class="info-block">
    <label>Date</label>
    <span>{date_val}</span>
  </div>
  <div class="info-block">
    <label>Customer Name</label>
    <span>{customer_name}</span>
  </div>
  <div class="info-block">
    <label>Phone</label>
    <span>{customer_phone}</span>
  </div>
  <div class="info-block">
    <label>Address</label>
    <span>{customer_address}</span>
  </div>
  <div class="info-block">
    <label>TRN / VAT</label>
    <span>{trn_vat if trn_vat and trn_vat != "TRN(VAT-TIN)" else "-"}</span>
  </div>
  <div class="info-block">
    <label>Service Type</label>
    <span>{service_type}</span>
  </div>
  <div class="info-block">
    <label>Delivery Date</label>
    <span>{delivery_date} {delivery_time}</span>
  </div>
</div>

{"<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:8px 12px;margin-bottom:12px;'><b>Remark:</b> " + remark + "</div>" if remark else ""}

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Item</th>
      <th>Qty</th>
      <th>Price (AED)</th>
      <th>Total (AED)</th>
    </tr>
  </thead>
  <tbody>
    {items_rows}
  </tbody>
</table>

<table class="totals">
  <tr><td>Sub Total</td><td>{subtotal:.2f} AED</td></tr>
  <tr><td>Discount</td><td>{discount:.2f} AED</td></tr>
  <tr><td>VAT (5%)</td><td>{vat:.2f} AED</td></tr>
  <tr class="grand-total"><td><b>TOTAL</b></td><td><b>{total:.2f} AED</b></td></tr>
</table>

<div class="footer">
  <p>Thank you for choosing Wash Hub Laundry!</p>
  <p>Generated by AP SOFT System</p>
</div>

<div class="no-print" style="text-align:center;margin-top:20px;">
  <button onclick="window.print()" style="padding:10px 30px;background:#2b5797;color:white;border:none;border-radius:6px;font-size:14px;cursor:pointer;">🖨 Print</button>
</div>
</body>
</html>"""

    def _open_print_window(self, html):
        """حفظ HTML وفتحه في المتصفح للطباعة"""
        import tempfile
        import webbrowser
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.html', delete=False,
            encoding='utf-8', prefix='laundry_invoice_'
        ) as f:
            f.write(html)
            temp_path = f.name
        
        webbrowser.open(f'file:///{temp_path.replace(chr(92), "/")}')
        messagebox.showinfo("طباعة", "تم فتح الفاتورة في المتصفح.\nاضغط Ctrl+P أو زر Print لطباعتها.")
    
    def update_cart_display(self):
        """تحديث عرض السلة"""
        # مسح البطاقات الموجودة
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        # إضافة المنتجات
        subtotal = 0
        total_qty = 0
        
        for idx, item in enumerate(self.cart_items):
            item_total = item['price'] * item['quantity']
            self.create_cart_item_card(idx, item)
            subtotal += item_total
            total_qty += item['quantity']
        
        # تحديث الإجماليات
        discount = 0
        vat = subtotal * 0.05
        total = subtotal - discount + vat
        
        self.subtotal_label.configure(text=f"{subtotal:.2f}")
        self.discount_label.configure(text=f"{discount:.2f}")
        self.quantity_label.configure(text=str(total_qty))
        self.vat_label.configure(text=f"{vat:.2f}")
        self.total_label.configure(text=f"{total:.2f}")
    
    def load_products(self):
        """تحميل المنتجات"""
        # مسح المنتجات الحالية
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # الحصول على المنتجات من قاعدة البيانات
        self.cursor.execute('SELECT * FROM products')
        products = self.cursor.fetchall()
        
        # عرض المنتجات في شبكة
        row, col = 0, 0
        for product in products:
            product_card = self.create_product_card(product)
            product_card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            col += 1
            if col > 5:  # 6 منتجات في كل صف
                col = 0
                row += 1
    
    def create_product_card(self, product):
        """إنشاء بطاقة منتج"""
        card = ctk.CTkFrame(self.products_frame, width=120, height=140, fg_color="white",
                           border_width=2, border_color="#2b5797")
        
        # علامة حمراء
        flag = ctk.CTkLabel(card, text="🚩", font=ctk.CTkFont(size=16))
        flag.pack(anchor="nw", padx=2, pady=2)
        
        # اسم المنتج
        name_label = ctk.CTkLabel(card, text=product[1], font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color="black")
        name_label.pack(pady=(30, 5))
        
        # السعر حسب نوع الخدمة
        price = self.get_product_price(product)
        price_label = ctk.CTkLabel(card, text=f"{price} AED", font=ctk.CTkFont(size=10),
                                  text_color="green")
        price_label.pack()
        
        # حدث النقر
        card.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
        name_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
        price_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
        
        return card
    
    def get_product_price(self, product):
        """الحصول على سعر المنتج حسب نوع الخدمة"""
        service = self.service_type.get()
        if service == "Wash & Press":
            return product[3]
        elif service == "Pressing Only":
            return product[4]
        elif service == "Wash & Press Ur":
            return product[5]
        elif service == "Pressing Urgent":
            return product[6]
        else:  # Contract
            return product[7]
    
    def add_to_cart(self, product):
        """إضافة منتج إلى السلة - مباشرة أو عبر نافذة حسب MODIFY PRICE"""
        # إذا كان MODIFY PRICE غير مفعل → إضافة مباشرة
        if not self.modify_price_enabled.get():
            price = self.get_product_price(product)
            self.add_item_to_cart(
                product[0],
                product[1],
                price,
                1,  # الكمية الافتراضية
                self.status_option.get()
            )
            return
        
        # إذا كان MODIFY PRICE مفعل → فتح النافذة
        # التحقق من وجود نافذة منتج مفتوحة مع سعر معدل
        if self.current_product_dialog and self.current_product_dialog.winfo_exists():
            if self.current_product_dialog.price_modified:
                result = messagebox.askyesno(
                    "تحذير",
                    "تم تعديل السعر في النافذة الحالية.\nهل تريد إغلاق النافذة الحالية وفتح منتج جديد؟",
                    parent=self
                )
                if not result:
                    return
                else:
                    self.current_product_dialog.destroy()
            else:
                self.current_product_dialog.destroy()
        
        # فتح نافذة جديدة
        self.current_product_dialog = ProductAddDialog(
            self, product, self.service_type.get(), self.status_option.get()
        )
    
    def create_cart_item_card(self, idx, item):
        """إنشاء بطاقة عنصر في السلة"""
        card = ctk.CTkFrame(self.cart_items_frame, fg_color="white", corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)
        
        # الصف العلوي - اسم المنتج وزر الحذف
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(10, 5))
        
        product_label = ctk.CTkLabel(
            top_row, 
            text=f"{idx + 1} - {item['name']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        product_label.pack(side="left", fill="x", expand=True)
        
        remove_btn = ctk.CTkButton(
            top_row,
            text="⊗",
            width=30,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            text_color="#e74c3c",
            hover_color="#f5f5f5",
            command=lambda: self.remove_cart_item(idx)
        )
        remove_btn.pack(side="right")
        
        # الصف الثاني - الوصف والتحكم
        middle_row = ctk.CTkFrame(card, fg_color="transparent")
        middle_row.pack(fill="x", padx=10, pady=5)
        
        # حقل الوصف
        desc_entry = ctk.CTkEntry(
            middle_row,
            placeholder_text="Other Description",
            width=150
        )
        desc_entry.pack(side="left", padx=(0, 10))
        
        # التحكم في الكمية
        qty_frame = ctk.CTkFrame(middle_row, fg_color="transparent")
        qty_frame.pack(side="left", padx=5)
        
        minus_btn = ctk.CTkButton(
            qty_frame,
            text="−",
            width=30,
            height=30,
            fg_color="#2c3e50",
            hover_color="#34495e",
            command=lambda: self.decrease_quantity(idx)
        )
        minus_btn.pack(side="left", padx=2)
        
        qty_label = ctk.CTkLabel(
            qty_frame,
            text=str(item['quantity']),
            width=40,
            font=ctk.CTkFont(size=12)
        )
        qty_label.pack(side="left", padx=2)
        
        plus_btn = ctk.CTkButton(
            qty_frame,
            text="+",
            width=30,
            height=30,
            fg_color="#2c3e50",
            hover_color="#34495e",
            command=lambda: self.increase_quantity(idx)
        )
        plus_btn.pack(side="left", padx=2)
        
        # أزرار الحالة (Hang, Fold)
        status_var = tk.IntVar(value=item['status'])
        
        hang_radio = ctk.CTkRadioButton(
            middle_row,
            text="Hang",
            variable=status_var,
            value=1,
            command=lambda: self.update_item_status(idx, 1)
        )
        hang_radio.pack(side="left", padx=5)
        
        fold_radio = ctk.CTkRadioButton(
            middle_row,
            text="Fold",
            variable=status_var,
            value=2,
            command=lambda: self.update_item_status(idx, 2)
        )
        fold_radio.pack(side="left", padx=5)
        
        # السعر
        price_label = ctk.CTkLabel(
            middle_row,
            text=f"{item['price'] * item['quantity']:.2f}",
            font=ctk.CTkFont(size=12),
            width=60
        )
        price_label.pack(side="right", padx=5)
    
    def remove_cart_item(self, idx):
        """حذف عنصر من السلة"""
        if idx < len(self.cart_items):
            self.cart_items.pop(idx)
            self.update_cart_display()
    
    def increase_quantity(self, idx):
        """زيادة الكمية"""
        if idx < len(self.cart_items):
            self.cart_items[idx]['quantity'] += 1
            self.update_cart_display()
    
    def decrease_quantity(self, idx):
        """تقليل الكمية"""
        if idx < len(self.cart_items):
            if self.cart_items[idx]['quantity'] > 1:
                self.cart_items[idx]['quantity'] -= 1
                self.update_cart_display()
    
    def update_item_status(self, idx, status):
        """تحديث حالة العنصر"""
        if idx < len(self.cart_items):
            self.cart_items[idx]['status'] = status
    
    def get_status_text(self, status_option):
        """تحويل رقم الحالة إلى نص"""
        status_map = {0: "Urgent", 1: "Hang", 2: "Fold"}
        return status_map.get(status_option, "Hang")
    
    def add_item_to_cart(self, product_id, name, price, quantity, status_option):
        """إضافة منتج إلى السلة بعد تأكيد النافذة"""
        # التحقق إذا كان المنتج موجود بالفعل بنفس السعر والحالة
        found = False
        for item in self.cart_items:
            if item['id'] == product_id and item['price'] == price and item['status'] == status_option:
                item['quantity'] += quantity
                found = True
                break
        
        if not found:
            item = {
                'id': product_id,
                'name': name,
                'price': price,
                'quantity': quantity,
                'status': status_option
            }
            self.cart_items.append(item)
        
        self.update_cart_display()
    
    def change_service_type(self, service):
        """تغيير نوع الخدمة"""
        self.service_type.set(service)
        self.update_service_button_colors(service)
        self.load_products()
    
    def update_service_button_colors(self, selected_service):
        """تحديث ألوان أزرار الخدمات لإظهار الخدمة المحددة"""
        # ألوان محددة للحالة المحددة
        selected_colors = {
            "#ADD8E6": "#5F9EA0",  # Cadet Blue
            "#90EE90": "#3CB371",  # Medium Sea Green
            "#FFE4B5": "#DEB887",  # Burlywood
            "#DDA0DD": "#9370DB",  # Medium Purple
            "#FFB6C1": "#DB7093"   # Pale Violet Red
        }
        
        for service, btn in self.service_buttons.items():
            if service == selected_service:
                # لون أغمق للزر المحدد
                original_color = self.service_colors[service]
                dark_color = selected_colors.get(original_color, original_color)
                btn.configure(
                    fg_color=dark_color, 
                    text_color="white", 
                    font=ctk.CTkFont(size=13, weight="bold"),
                    hover_color=dark_color
                )
            else:
                # اللون الأصلي للأزرار الأخرى
                original_color = self.service_colors[service]
                hover_col = self.service_hover_colors.get(original_color, original_color)
                btn.configure(
                    fg_color=original_color, 
                    text_color="black", 
                    font=ctk.CTkFont(size=13),
                    hover_color=hover_col
                )
    
    def search_customer(self, event=None):
        """البحث عن عميل"""
        self.show_customer_search()
    
    def scan_cloth(self, event=None):
        """مسح الملابس بالباركود"""
        barcode = self.scan_cloth_entry.get().strip()
        if barcode:
            # البحث عن المنتج بالباركود
            messagebox.showinfo("مسح الباركود", f"تم مسح الباركود: {barcode}")
            self.scan_cloth_entry.delete(0, 'end')
    
    def search_product_live(self, event=None):
        """البحث المباشر عن المنتجات"""
        search_text = self.search_product_entry.get().lower().strip()
        if not search_text:
            # إعادة عرض جميع المنتجات
            self.load_products(self.service_type.get())
            return
        
        # البحث في المنتجات المعروضة
        # يمكن تطوير هذه الوظيفة لاحقاً للبحث في قاعدة البيانات
        pass
    
    def show_search_dialog(self):
        """عرض نافذة البحث الشامل"""
        SearchDialog(self)
    
    def split_invoice(self):
        """تقسيم الفاتورة"""
        if len(self.cart_items) < 2:
            messagebox.showwarning("تحذير", "يجب أن يحتوي السلة على منتجين على الأقل للتقسيم")
            return
        messagebox.showinfo("تقسيم الفاتورة", "سيتم إضافة ميزة تقسيم الفاتورة قريباً")
    
    def quick_delivery(self):
        """توصيل سريع"""
        if not self.cart_items:
            messagebox.showwarning("تحذير", "السلة فارغة!")
            return
        # تعيين تاريخ التسليم لليوم نفسه
        self.delivery_date_entry.delete(0, 'end')
        self.delivery_date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.delivery_time_entry.delete(0, 'end')
        self.delivery_time_entry.insert(0, (datetime.now() + timedelta(hours=2)).strftime("%H:%M"))
        messagebox.showinfo("توصيل سريع", "تم تعيين موعد التوصيل خلال ساعتين!")
    
    def get_all_customers(self):
        """الحصول على جميع العملاء"""
        self.cursor.execute('SELECT * FROM customers')
        rows = self.cursor.fetchall()
        customers = []
        for row in rows:
            customer = type('Customer', (), {
                'id': row[0],
                'phone': row[1],
                'name': row[2],
                'address': row[3],
                'trn_vat': row[4]
            })()
            customers.append(customer)
        return customers
    
    def add_customer(self, phone, name, address, trn_vat):
        """إضافة عميل جديد"""
        self.cursor.execute('''
            INSERT INTO customers (phone, name, address, trn_vat)
            VALUES (?, ?, ?, ?)
        ''', (phone, name, address, trn_vat))
        self.conn.commit()
    
    def show_customer_search(self):
        """عرض نافذة البحث عن العملاء"""
        window = CustomerSearchDialog(self, self)
        self.wait_window(window)
        
        # إذا تم اختيار عميل
        if hasattr(window, 'selected_customer') and window.selected_customer:
            customer = window.selected_customer
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer['phone'])
            self.customer_name_entry.delete(0, 'end')
            self.customer_name_entry.insert(0, customer['name'])
            self.customer_address_entry.delete(0, 'end')
            self.customer_address_entry.insert(0, customer['address'])
            self.trn_entry.delete(0, 'end')
            self.trn_entry.insert(0, customer['trn_vat'])
    
    def load_next_invoice_number(self):
        """تحميل رقم الفاتورة التالي"""
        self.cursor.execute('SELECT MAX(id) FROM invoices')
        result = self.cursor.fetchone()
        next_num = (result[0] or 0) + 1
        self.invoice_number_entry.delete(0, 'end')
        self.invoice_number_entry.insert(0, str(3147 + next_num))
    
    def previous_invoice(self):
        """الانتقال إلى الفاتورة السابقة"""
        try:
            current = int(self.invoice_number_entry.get())
            if current > 3147:
                self.invoice_number_entry.delete(0, 'end')
                self.invoice_number_entry.insert(0, str(current - 1))
        except ValueError:
            pass
    
    def next_invoice(self):
        """الانتقال إلى الفاتورة التالية"""
        try:
            current = int(self.invoice_number_entry.get())
            self.invoice_number_entry.delete(0, 'end')
            self.invoice_number_entry.insert(0, str(current + 1))
        except ValueError:
            pass
    
    def show_menu_dialog(self):
        """عرض نافذة القائمة الرئيسية"""
        MenuDialog(self)
    
    def _on_window_configure(self, event):
        """تحديث الموضع المحفوظ عند تغيير حجم أو موضع النافذة"""
        if event.widget == self:  # التأكد أن الحدث للنافذة الرئيسية فقط
            # تحديث الموضع المحفوظ مؤقتاً لتحسين أداء قائمة الأدمن
            try:
                self._cached_position = (self.winfo_x(), self.winfo_y(), self.winfo_width())
            except:
                self._cached_position = None
    
    def _initialize_cached_position(self):
        """تهيئة الموضع المحفوظ مؤقتاً لتحسين الأداء"""
        try:
            self._cached_position = (self.winfo_x(), self.winfo_y(), self.winfo_width())
        except:
            self._cached_position = (100, 100, 1400)
    
    def show_admin_menu(self):
        """عرض قائمة الأدمن المنسدلة"""
        # منع فتح عدة نوافذ admin في نفس الوقت
        try:
            if self.admin_menu_open and self.admin_menu_open.winfo_exists():
                self.admin_menu_open.lift()
                return
        except:
            # في حالة وجود خطأ، إعادة تعيين المرجع
            self.admin_menu_open = None
        
        # تحسين الأداء: استخدام موضع ثابت محسوب مسبقاً
        if self._cached_position is None:
            # حساب الموضع مرة واحدة فقط عند أول استخدام
            try:
                # استخدام after_idle لتجنب مشاكل التوقيت
                self.after_idle(self._calculate_position_and_show_menu)
                return
            except:
                # موضع افتراضي محسن
                self._cached_position = (100, 100, 1400)
        
        # إنشاء قائمة الأدمن الجديدة
        try:
            self.admin_menu_open = AdminMenuDialog(self)
        except Exception as e:
            print(f"خطأ في فتح قائمة الأدمن: {e}")
            # إعادة تعيين الموضع والمحاولة مرة أخرى
            self._cached_position = None
            self.after_idle(self._calculate_position_and_show_menu)
    
    def _calculate_position_and_show_menu(self):
        """حساب الموضع وعرض القائمة"""
        try:
            parent_x = self.winfo_x()
            parent_y = self.winfo_y() 
            parent_width = self.winfo_width()
            self._cached_position = (parent_x, parent_y, parent_width)
        except:
            self._cached_position = (100, 100, 1400)
        
        self.admin_menu_open = AdminMenuDialog(self)
    
    def adjust_color(self, hex_color, amount):
        """ تعديل لون للحصول على hover effect """
        # إزالة # إذا كانت موجودة
        hex_color = hex_color.lstrip('#')
        
        # تحويل إلى RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # تعديل القيم
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # إرجاع اللون الجديد
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def on_closing(self):
        """عند إغلاق البرنامج"""
        self.conn.close()
        self.destroy()



class ProductAddDialog(ctk.CTkToplevel):
    """نافذة إضافة منتج للسلة مع خيارات التخصيص"""
    
    def __init__(self, parent, product, service_type, current_status):
        super().__init__(parent)
        
        self.parent = parent
        self.product = product
        self.service_type = service_type
        self.original_price = self.get_product_price()
        self.price_modified = False
        
        # إعداد النافذة
        self.title("Add Product")
        self.geometry("620x680")
        self.resizable(False, False)
        
        # جعل النافذة في المقدمة
        self.transient(parent)
        self.grab_set()
        
        # ربط حدث الإغلاق
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # العنوان
        title_label = ctk.CTkLabel(
            self, 
            text=f"{product[1]} - {service_type} - {self.original_price:.2f}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)
        
        # الكمية
        qty_frame = ctk.CTkFrame(self, fg_color="transparent")
        qty_frame.pack(pady=10)
        
        ctk.CTkLabel(qty_frame, text="Qty", font=ctk.CTkFont(size=14)).pack()
        
        qty_controls = ctk.CTkFrame(qty_frame, fg_color="transparent")
        qty_controls.pack(pady=10)
        
        self.qty_var = tk.IntVar(value=1)
        
        ctk.CTkButton(
            qty_controls, text="−", width=80, height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            command=self.decrease_qty
        ).pack(side="left", padx=10)
        
        self.qty_entry = ctk.CTkEntry(
            qty_controls, width=200, height=50,
            font=ctk.CTkFont(size=16),
            textvariable=self.qty_var,
            justify="center"
        )
        self.qty_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            qty_controls, text="+", width=80, height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            command=self.increase_qty
        ).pack(side="left", padx=10)
        
        # السعر
        price_frame = ctk.CTkFrame(self, fg_color="transparent")
        price_frame.pack(pady=10)
        
        ctk.CTkLabel(price_frame, text="Price", font=ctk.CTkFont(size=14)).pack()
        
        price_controls = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_controls.pack(pady=10)
        
        self.price_var = tk.DoubleVar(value=self.original_price)
        
        ctk.CTkButton(
            price_controls, text="−", width=80, height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            command=self.decrease_price
        ).pack(side="left", padx=10)
        
        self.price_entry = ctk.CTkEntry(
            price_controls, width=200, height=50,
            font=ctk.CTkFont(size=16),
            textvariable=self.price_var,
            justify="center"
        )
        self.price_entry.pack(side="left", padx=10)
        self.price_entry.bind("<KeyRelease>", self.on_price_change)
        
        ctk.CTkButton(
            price_controls, text="+", width=80, height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            command=self.increase_price
        ).pack(side="left", padx=10)
        
        # خيارات Hang/Fold
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(pady=10)
        
        self.status_var = tk.IntVar(value=current_status)
        
        ctk.CTkRadioButton(
            options_frame, text="Hang", 
            variable=self.status_var, value=1,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=20)
        
        ctk.CTkRadioButton(
            options_frame, text="Fold", 
            variable=self.status_var, value=2,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=20)
        
        # أزرار Print Tag
        tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        tags_frame.pack(pady=10)
        
        tag_colors = ["#B0E0E6", "#FFB6C1", "#FFFFB0", "#D3D3D3", "#C8A2C8", "#87CEEB", "#4FC3F7"]
        for color in tag_colors:
            ctk.CTkButton(
                tags_frame, text="Print Tag",
                width=70, height=35,
                fg_color=color,
                text_color="black",
                font=ctk.CTkFont(size=10),
                command=lambda c=color: self.print_tag(c)
            ).pack(side="left", padx=3)
        
        # الأزرار السفلية
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=15)
        
        ctk.CTkButton(
            bottom_frame, text="Cancel",
            width=120, height=40,
            fg_color="#2b2b2b",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.cancel
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            bottom_frame, text="Add to cart",
            width=150, height=40,
            fg_color="#00C853",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.add_to_cart
        ).pack(side="left", padx=10)
    
    def get_product_price(self):
        """الحصول على سعر المنتج حسب نوع الخدمة"""
        if self.service_type == "Wash & Press":
            return self.product[3]
        elif self.service_type == "Pressing Only":
            return self.product[4]
        elif self.service_type == "Wash & Press Ur":
            return self.product[5]
        elif self.service_type == "Pressing Urgent":
            return self.product[6]
        else:  # Contract
            return self.product[7]
    
    def increase_qty(self):
        self.qty_var.set(self.qty_var.get() + 1)
    
    def decrease_qty(self):
        if self.qty_var.get() > 1:
            self.qty_var.set(self.qty_var.get() - 1)
    
    def increase_price(self):
        current = self.price_var.get()
        self.price_var.set(round(current + 1, 2))
        self.price_modified = True
    
    def decrease_price(self):
        current = self.price_var.get()
        if current > 0:
            self.price_var.set(round(current - 1, 2))
            self.price_modified = True
    
    def on_price_change(self, event):
        """تحديد أن السعر تم تعديله"""
        try:
            new_price = float(self.price_entry.get())
            if abs(new_price - self.original_price) > 0.01:
                self.price_modified = True
        except:
            pass
    
    def cancel(self):
        """إلغاء وإغلاق النافذة"""
        if self.price_modified:
            result = messagebox.askyesno(
                "تحذير",
                "تم تعديل السعر. هل تريد الخروج بدون حفظ؟",
                parent=self
            )
            if result:
                self.destroy()
        else:
            self.destroy()
    
    def print_tag(self, color):
        """طباعة تاج بلون محدد"""
        product_name = self.product[1]
        qty = self.qty_var.get()
        messagebox.showinfo("طباعة التاج", f"سيتم طباعة {qty} تاج بلون {color} للمنتج: {product_name}")
    
    def add_to_cart(self):
        """إضافة المنتج للسلة"""
        self.parent.add_item_to_cart(
            self.product[0],
            self.product[1],
            self.price_var.get(),
            self.qty_var.get(),
            self.status_var.get()
        )
        self.destroy()


class CustomerSearchDialog(ctk.CTkToplevel):
    """نافذة البحث عن العملاء مع ثلاث تبويبات"""
    
    def __init__(self, parent, laundry_system):
        super().__init__(parent)
        
        self.parent = parent
        self.laundry_system = laundry_system
        self.selected_customer = None
        
        self.title("Add Customer")
        self.geometry("1400x700")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.focus_force()
        
        # إنشاء التبويبات
        self.tabview = ctk.CTkTabview(self, width=1380, height=650)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # إضافة التبويبات
        self.tabview.add("Search Customer")
        self.tabview.add("Add Customer")
        self.tabview.add("Add Package")
        
        # إنشاء محتوى كل تبويبة
        self.create_search_tab()
        self.create_add_customer_tab()
        self.create_add_package_tab()
        
        # زر الإغلاق
        close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=40,
            height=40,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.destroy
        )
        close_btn.place(relx=0.98, rely=0.02, anchor="ne")
    
    def create_search_tab(self):
        """إنشاء تبويبة البحث"""
        tab = self.tabview.tab("Search Customer")
        
        # شريط البحث
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="0000000000",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_customers)
        
        # حقل اسم العميل
        self.customer_name_display = ctk.CTkEntry(
            search_frame,
            placeholder_text="Cash Customer",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14),
            state="readonly"
        )
        self.customer_name_display.pack(side="left", padx=5)
        
        # زر Clear
        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            width=100,
            height=40,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.clear_search
        )
        clear_btn.pack(side="right", padx=5)
        
        # جدول العملاء
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # إنشاء Treeview
        columns = ("#", "Mobile", "Name", "Address", "Telephone", "Action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # تعريف الأعمدة
        self.tree.heading("#", text="#")
        self.tree.heading("Mobile", text="Mobile")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Telephone", text="Telephone")
        self.tree.heading("Action", text="Action")
        
        self.tree.column("#", width=50)
        self.tree.column("Mobile", width=150)
        self.tree.column("Name", width=250)
        self.tree.column("Address", width=400)
        self.tree.column("Telephone", width=150)
        self.tree.column("Action", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double click to select
        self.tree.bind('<Double-Button-1>', self.on_customer_select)
        
        # Load More button
        load_more_btn = ctk.CTkButton(
            tab,
            text="Load More..",
            width=1360,
            height=40,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            font=ctk.CTkFont(size=13),
            command=self.load_more_customers
        )
        load_more_btn.pack(padx=10, pady=5)
        
        # تحميل العملاء
        self.load_customers()
    
    def create_add_customer_tab(self):
        """إنشاء تبويبة إضافة عميل"""
        tab = self.tabview.tab("Add Customer")
        
        # إنشاء نموذج إضافة عميل
        form_frame = ctk.CTkScrollableFrame(tab, fg_color="#f5f5f5")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Customer Mobile
        ctk.CTkLabel(form_frame, text="Customer Mobile", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(15, 2))
        self.mobile_entry = ctk.CTkEntry(form_frame, placeholder_text="0000000000", height=40, border_width=1)
        self.mobile_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.mobile_entry.insert(0, "0000000000")
        
        # DOB
        ctk.CTkLabel(form_frame, text="DOB", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.dob_entry = ctk.CTkEntry(form_frame, placeholder_text="DOB", height=40, border_width=1)
        self.dob_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.dob_entry.insert(0, "DOB")
        
        # Customer Card No
        ctk.CTkLabel(form_frame, text="Customer Card No.", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.card_entry = ctk.CTkEntry(form_frame, placeholder_text="0000", height=40, border_width=1)
        self.card_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.card_entry.insert(0, "0000")
        
        # Customer Name
        ctk.CTkLabel(form_frame, text="Customer Name 1", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="Cash Customer", height=40, border_width=1)
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.name_entry.insert(0, "Cash Customer")
        
        # Customer Address
        ctk.CTkLabel(form_frame, text="Customer Address", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.address_entry = ctk.CTkEntry(form_frame, placeholder_text="Cash Customer address1", height=40, border_width=1)
        self.address_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.address_entry.insert(0, "Cash Customer address1")
        
        # Customer TRN
        ctk.CTkLabel(form_frame, text="Customer TRN", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.trn_cust_entry = ctk.CTkEntry(form_frame, placeholder_text="Customer TRN", height=40, border_width=1)
        self.trn_cust_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.trn_cust_entry.insert(0, "Customer TRN")
        
        # Credit Limit
        ctk.CTkLabel(form_frame, text="Credit Limit", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.credit1_entry = ctk.CTkEntry(form_frame, placeholder_text="0", height=40, border_width=1)
        self.credit1_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.credit1_entry.insert(0, "0")
        
        # Credit Limit (второй)
        ctk.CTkLabel(form_frame, text="Credit Limit", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.credit2_entry = ctk.CTkEntry(form_frame, placeholder_text="Credit Limit", height=40, border_width=1)
        self.credit2_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.credit2_entry.insert(0, "Credit Limit")
        
        # Cust Type
        ctk.CTkLabel(form_frame, text="Cust Type", font=ctk.CTkFont(size=12), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(5, 2))
        self.type_combo = ctk.CTkComboBox(form_frame, values=["Cash Customer"], height=40, border_width=1)
        self.type_combo.set("Cash Customer")
        self.type_combo.pack(fill="x", padx=10, pady=(0, 15))
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(tab, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=15, side="bottom")
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear",
            width=150,
            height=45,
            fg_color="#2c2c2c",
            hover_color="#1a1a1a",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.clear_customer_form
        )
        clear_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Update Customer",
            width=200,
            height=45,
            fg_color="#27ae60",
            hover_color="#229954",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_customer
        )
        save_btn.pack(side="right", padx=5)
    
    def create_add_package_tab(self):
        """إنشاء تبويبة إضافة باقة"""
        tab = self.tabview.tab("Add Package")
        
        # Container frame
        container = ctk.CTkFrame(tab, fg_color="#f5f5f5")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # رسالة عدم وجود باقات
        ctk.CTkLabel(
            container,
            text="No membership/package added !",
            font=ctk.CTkFont(size=13),
            text_color="#c0392b"
        ).pack(pady=20, padx=20, anchor="w")
        
        # Select Membership Package
        ctk.CTkLabel(
            container, 
            text="Select Membership Package", 
            font=ctk.CTkFont(size=12), 
            text_color="#2c3e50"
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        # Start Date label
        ctk.CTkLabel(
            container, 
            text="Start Date", 
            font=ctk.CTkFont(size=12), 
            text_color="#2c3e50"
        ).pack(anchor="w", padx=20, pady=(10, 2))
        
        # Start Date entry with calendar icon
        date_frame = ctk.CTkFrame(container, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        start_date_entry = ctk.CTkEntry(
            date_frame, 
            placeholder_text="",
            height=40,
            border_width=1
        )
        start_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Calendar icon button
        calendar_btn = ctk.CTkButton(
            date_frame,
            text="📅",
            width=50,
            height=40,
            fg_color="#ecf0f1",
            text_color="#2c3e50",
            hover_color="#bdc3c7",
            font=ctk.CTkFont(size=18)
        )
        calendar_btn.pack(side="left")
        
        # Dropdown for membership package
        package_combo = ctk.CTkComboBox(
            container, 
            values=["Select an Option *"], 
            height=40,
            border_width=1
        )
        package_combo.set("Select an Option *")
        package_combo.pack(fill="x", padx=20, pady=(0, 15))
        
        # Payment mode Selection
        ctk.CTkLabel(
            container, 
            text="Payment mode Selection", 
            font=ctk.CTkFont(size=12), 
            text_color="#2c3e50"
        ).pack(anchor="w", padx=20, pady=(10, 2))
        
        payment_combo = ctk.CTkComboBox(
            container, 
            values=["Cash", "Credit Card", "Credit"], 
            height=40,
            border_width=1
        )
        payment_combo.set("Cash")
        payment_combo.pack(fill="x", padx=20, pady=(0, 30))
        
        # Save button
        save_pkg_btn = ctk.CTkButton(
            container,
            text="Save & Pay Membership",
            width=250,
            height=50,
            fg_color="#3498db",
            hover_color="#2980b9",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_pkg_btn.pack(pady=20)
    
    def load_customers(self):
        """تحميل العملاء"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # تحميل العملاء من قاعدة البيانات
        customers = self.laundry_system.get_all_customers()
        for idx, customer in enumerate(customers, 1):
            self.tree.insert('', 'end', values=(
                idx,
                customer.phone,
                customer.name,
                customer.address,
                customer.phone,
                "✏ 🔍"
            ))
    
    def search_customers(self, event=None):
        """البحث في العملاء"""
        search_text = self.search_entry.get().lower()
        
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_text:
            self.load_customers()
            return
        
        # البحث في العملاء
        customers = self.laundry_system.get_all_customers()
        idx = 1
        for customer in customers:
            if (search_text in customer.phone.lower() or 
                search_text in customer.name.lower()):
                self.tree.insert('', 'end', values=(
                    idx,
                    customer.phone,
                    customer.name,
                    customer.address,
                    customer.phone,
                    "✏ 🔍"
                ))
                idx += 1
                
                # Update customer name display
                if customer.phone == search_text:
                    self.customer_name_display.configure(state="normal")
                    self.customer_name_display.delete(0, 'end')
                    self.customer_name_display.insert(0, customer.name)
                    self.customer_name_display.configure(state="readonly")
    
    def on_customer_select(self, event=None):
        """اختيار عميل من الجدول"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # البحث عن العميل في قاعدة البيانات
            customers = self.laundry_system.get_all_customers()
            for customer in customers:
                if customer.phone == values[1]:
                    self.selected_customer = {
                        'phone': customer.phone,
                        'name': customer.name,
                        'address': customer.address,
                        'trn_vat': customer.trn_vat
                    }
                    self.destroy()
                    break
    
    def clear_search(self):
        """مسح البحث"""
        self.search_entry.delete(0, 'end')
        self.customer_name_display.configure(state="normal")
        self.customer_name_display.delete(0, 'end')
        self.customer_name_display.insert(0, "Cash Customer")
        self.customer_name_display.configure(state="readonly")
        self.load_customers()
    
    def load_more_customers(self):
        """تحميل المزيد من العملاء"""
        # يمكن تنفيذ pagination هنا
        pass
    
    def clear_customer_form(self):
        """مسح نموذج العميل"""
        self.mobile_entry.delete(0, 'end')
        self.dob_entry.delete(0, 'end')
        self.card_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.address_entry.delete(0, 'end')
        self.trn_cust_entry.delete(0, 'end')
        self.credit1_entry.delete(0, 'end')
        self.credit2_entry.delete(0, 'end')
    
    def save_customer(self):
        """حفظ العميل"""
        mobile = self.mobile_entry.get()
        name = self.name_entry.get()
        address = self.address_entry.get()
        trn = self.trn_cust_entry.get()
        
        if not mobile or not name:
            messagebox.showerror("خطأ", "الرجاء إدخال رقم الهاتف والاسم")
            return
        
        try:
            self.laundry_system.add_customer(mobile, name, address, trn)
            messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح")
            self.clear_customer_form()
            self.load_customers()
            # Switch to search tab
            self.tabview.set("Search Customer")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")


class MenuDialog(ctk.CTkToplevel):
    """نافذة القائمة الرئيسية"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        self.title("Menu")
        self.geometry("320x480")
        
        # Make window stay on top
        self.lift()
        self.focus_force()
        
        # Main container with light background
        main_frame = ctk.CTkFrame(self, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notifications section at top
        notif_frame = ctk.CTkFrame(main_frame, fg_color="white", height=60, corner_radius=8)
        notif_frame.pack(fill="x", padx=10, pady=(10, 15))
        notif_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            notif_frame,
            text="Notifications",
            font=ctk.CTkFont(size=14),
            text_color="#7f8c8d"
        ).pack(expand=True)
        
        # Search and Menu buttons row
        top_buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        search_menu_btn = ctk.CTkButton(
            top_buttons_frame,
            text="🔍\nSearch",
            width=130,
            height=70,
            fg_color="#2c3e50",
            hover_color="#34495e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        search_menu_btn.pack(side="left", padx=5)
        
        menu_close_btn = ctk.CTkButton(
            top_buttons_frame,
            text="✕\nMenu",
            width=130,
            height=70,
            fg_color="#2c3e50",
            hover_color="#34495e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self.destroy
        )
        menu_close_btn.pack(side="right", padx=5)
        
        # Delivery & Save button
        delivery_btn = ctk.CTkButton(
            main_frame,
            text="Delivery & Save 💾",
            width=280,
            height=50,
            fg_color="#bdc3c7",
            hover_color="#95a5a6",
            text_color="#2c3e50",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self.parent.save_invoice
        )
        delivery_btn.pack(padx=10, pady=(0, 10))
        
        # Grid of action buttons (3 columns)
        actions_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Row 1: Invoice, Print, Track
        self.create_menu_button(actions_container, "📝\nInvoice", "#27ae60", 0, 0, self.show_invoices)
        self.create_menu_button(actions_container, "🖨\nPrint", "#27ae60", 0, 1, self.print_invoice)
        self.create_menu_button(actions_container, "📍\nTrack", "#27ae60", 0, 2, self.track_order)
        
        # Row 2: Sales Return, Delete
        self.create_menu_button(actions_container, "🔄\nSales\nReturn", "#27ae60", 1, 0, self.sales_return)
        self.create_menu_button(actions_container, "🗑\nDelete", "#95a5a6", 1, 1, self.delete_invoice)
        
        # Row 3: Discount, More
        self.create_menu_button(actions_container, "💰\nDiscount", "#95a5a6", 2, 0, self.apply_discount)
        self.create_menu_button(actions_container, "⋯\nMore", "#2c3e50", 2, 1, self.show_more_options)
        
    def create_menu_button(self, parent, text, color, row, col, command=None):
        """إنشاء زر في القائمة"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            width=85,
            height=75,
            fg_color=color,
            hover_color=self.adjust_color(color, -20),
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8,
            command=command if command else lambda: None
        )
        btn.grid(row=row, column=col, padx=5, pady=5)
    
    def show_invoices(self):
        """عرض الفواتير"""
        messagebox.showinfo("الفواتير", "سيتم عرض قائمة الفواتير قريباً")
    
    def print_invoice(self):
        """طباعة الفاتورة الحالية"""
        self.destroy()
        self.parent.print_current_invoice()
    
    def track_order(self):
        """تتبع الطلب"""
        messagebox.showinfo("تتبع الطلب", "سيتم إضافة ميزة تتبع الطلبات قريباً")
    
    def sales_return(self):
        """مرتجع مبيعات"""
        messagebox.showinfo("مرتجع", "سيتم إضافة ميزة المرتجعات قريباً")
    
    def delete_invoice(self):
        """حذف فاتورة"""
        if messagebox.askyesno("حذف", "هل تريد حذف الفاتورة الحالية؟"):
            self.parent.clear_cart()
            messagebox.showinfo("تم الحذف", "تم مسح الفاتورة")
    
    def apply_discount(self):
        """تطبيق خصم"""
        DiscountDialog(self.parent)
    
    def show_more_options(self):
        """خيارات إضافية"""
        messagebox.showinfo("المزيد", "سيتم إضافة خيارات إضافية قريباً")
    
    def adjust_color(self, hex_color, amount):
        """تعديل درجة اللون"""
        hex_color = hex_color.lstrip('#')
        r = max(0, min(255, int(hex_color[0:2], 16) + amount))
        g = max(0, min(255, int(hex_color[2:4], 16) + amount))
        b = max(0, min(255, int(hex_color[4:6], 16) + amount))
        return f'#{r:02x}{g:02x}{b:02x}'


class SearchDialog(ctk.CTkToplevel):
    """نافذة بحث شاملة"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        self.title("Search")
        self.geometry("800x500")
        
        self.lift()
        self.focus_force()
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Search type tabs
        tabview = ctk.CTkTabview(main_frame, width=780, height=450)
        tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        tabview.add("Search Invoice")
        tabview.add("Search Customer")
        tabview.add("Search Product")
        
        # Invoice search tab
        invoice_tab = tabview.tab("Search Invoice")
        ctk.CTkLabel(
            invoice_tab, 
            text="Search by Invoice Number:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        invoice_entry = ctk.CTkEntry(invoice_tab, width=400, height=40)
        invoice_entry.pack(pady=5)
        
        ctk.CTkButton(
            invoice_tab,
            text="Search",
            width=150,
            height=40,
            fg_color="#27ae60",
            command=lambda: self.search_invoice(invoice_entry.get())
        ).pack(pady=10)
        
        # Customer search tab
        customer_tab = tabview.tab("Search Customer")
        ctk.CTkLabel(
            customer_tab, 
            text="Search by Phone or Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        customer_entry = ctk.CTkEntry(customer_tab, width=400, height=40)
        customer_entry.pack(pady=5)
        
        ctk.CTkButton(
            customer_tab,
            text="Search",
            width=150,
            height=40,
            fg_color="#27ae60",
            command=lambda: self.search_customer(customer_entry.get())
        ).pack(pady=10)
        
        # Product search tab
        product_tab = tabview.tab("Search Product")
        ctk.CTkLabel(
            product_tab, 
            text="Search by Product Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        product_entry = ctk.CTkEntry(product_tab, width=400, height=40)
        product_entry.pack(pady=5)
        
        ctk.CTkButton(
            product_tab,
            text="Search",
            width=150,
            height=40,
            fg_color="#27ae60",
            command=lambda: self.search_product(product_entry.get())
        ).pack(pady=10)
    
    def search_invoice(self, query):
        """البحث عن فاتورة"""
        if not query:
            messagebox.showwarning("تحذير", "الرجاء إدخال رقم الفاتورة")
            return
        messagebox.showinfo("بحث الفاتورة", f"البحث عن الفاتورة: {query}")
    
    def search_customer(self, query):
        """البحث عن عميل"""
        if not query:
            messagebox.showwarning("تحذير", "الرجاء إدخال رقم الهاتف أو الاسم")
            return
        self.parent.show_customer_search()
        self.destroy()
    
    def search_product(self, query):
        """البحث عن منتج"""
        if not query:
            messagebox.showwarning("تحذير", "الرجاء إدخال اسم المنتج")
            return
        messagebox.showinfo("بحث المنتج", f"البحث عن المنتج: {query}")


class DiscountDialog(ctk.CTkToplevel):
    """نافذة تطبيق الخصم"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        self.title("Apply Discount")
        self.geometry("400x300")
        
        self.lift()
        self.focus_force()
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame, 
            text="Apply Discount",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2c3e50"
        ).pack(pady=10)
        
        # Discount type
        ctk.CTkLabel(
            main_frame, 
            text="Discount Type:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(15, 5))
        
        self.discount_type = ctk.StringVar(value="Percentage")
        discount_combo = ctk.CTkComboBox(
            main_frame,
            values=["Percentage", "Fixed Amount"],
            variable=self.discount_type,
            width=300,
            height=40
        )
        discount_combo.pack(pady=5)
        
        # Discount value
        ctk.CTkLabel(
            main_frame, 
            text="Discount Value:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(15, 5))
        
        self.discount_value = ctk.DoubleVar(value=0)
        discount_entry = ctk.CTkEntry(
            main_frame,
            textvariable=self.discount_value,
            width=300,
            height=40
        )
        discount_entry.pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=120,
            height=40,
            fg_color="#95a5a6",
            command=self.destroy
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Apply",
            width=120,
            height=40,
            fg_color="#27ae60",
            command=self.apply_discount
        ).pack(side="left", padx=5)
    
    def apply_discount(self):
        """تطبيق الخصم"""
        discount_val = self.discount_value.get()
        discount_type = self.discount_type.get()
        
        if discount_val <= 0:
            messagebox.showwarning("تحذير", "الرجاء إدخال قيمة خصم صحيحة")
            return
        
        messagebox.showinfo(
            "تم تطبيق الخصم", 
            f"تم تطبيق خصم {discount_val}{'%' if discount_type == 'Percentage' else ' AED'} على الفاتورة"
        )
        self.destroy()


class AdminMenuDialog(ctk.CTkToplevel):
    """قائمة الأدمن المنسدلة - محسنة للأداء"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        # إخفاء شريط العنوان
        self.overrideredirect(True)
        
        # استخدام الموضع المحفوظ مؤقتاً لتحسين الأداء
        menu_width = 200
        menu_height = 265
        
        if hasattr(parent, '_cached_position') and parent._cached_position:
            parent_x, parent_y, parent_width = parent._cached_position
            x_position = parent_x + parent_width - menu_width - 30
            y_position = parent_y + 60
        else:
            # موضع افتراضي في حالة عدم توفر الموضع المحفوظ
            x_position = 1180
            y_position = 60
        
        self.geometry(f"{menu_width}x{menu_height}+{x_position}+{y_position}")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.attributes('-topmost', True)
        
        # تحسين الأداء: إنشاء الواجهة بشكل مُحسّن
        self._create_optimized_ui()
        
        # Focus on the window
        self.focus_force()
        
        # تأخير ربط FocusOut لتجنب إغلاق النافذة فوراً بسبب نفس النقرة التي فتحتها
        self.after(300, lambda: self.bind("<FocusOut>", lambda e: self._safe_destroy()))
    
    def _safe_destroy(self):
        """تدمير آمن للنافذة مع تنظيف المراجع"""
        try:
            # إعادة تعيين المرجع في النافذة الأب
            if hasattr(self.parent, 'admin_menu_open'):
                self.parent.admin_menu_open = None
            self.destroy()
        except:
            pass
    
    def destroy(self):
        """تجاوز دالة التدمير لتنظيف المراجع"""
        try:
            # إعادة تعيين المرجع في النافذة الأب
            if hasattr(self.parent, 'admin_menu_open'):
                self.parent.admin_menu_open = None
            super().destroy()
        except:
            pass
    
    def _create_optimized_ui(self):
        """إنشاء الواجهة بشكل محسن للأداء"""
        # Main container with white background and border
        main_frame = ctk.CTkFrame(
            self, 
            fg_color="white",
            corner_radius=8,
            border_width=2,
            border_color="#2b5797"
        )
        main_frame.pack(fill="both", expand=True)
        
        # Admin header
        header = ctk.CTkFrame(main_frame, fg_color="#2b5797", height=40, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="👤 Admin",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(pady=10)
        
        # تحسين الأداء: إنشاء الأزرار بحلقة واحدة مُحسّنة
        button_config = {
            "width": 180,
            "height": 35,
            "fg_color": "white",
            "text_color": "#2c3e50",
            "hover_color": "#ecf0f1",
            "font": ctk.CTkFont(size=12),
            "anchor": "w",
            "corner_radius": 0,
            "border_width": 0
        }
        
        # Menu items - تحسين الأداء بتقليل عدد العمليات
        menu_items = [
            ("📊 Dashboard", self.open_dashboard),
            ("My Profile", self.my_profile),
            ("Help", self.show_help),
            ("Exit", self.exit_app),
            ("Counter Closing", self.counter_closing),
            ("🚪 Logout", self.logout)
        ]
        
        # إنشاء الأزرار بشكل مُحسّن
        for item_text, command in menu_items:
            btn = ctk.CTkButton(main_frame, text=item_text, command=command, **button_config)
            btn.pack(fill="x", padx=5, pady=1)
    
    def open_dashboard(self):
        """فتح لوحة التحكم"""
        self._safe_destroy()
        DashboardWindow(self.parent)

    def my_profile(self):
        """عرض الملف الشخصي"""
        self._safe_destroy()
        ProfileDialog(self.parent)
    
    def show_help(self):
        """عرض المساعدة"""
        self._safe_destroy()
        messagebox.showinfo("المساعدة", "دليل الاستخدام:\n\n1. اختر نوع الخدمة\n2. أضف المنتجات للسلة\n3. احفظ الفاتورة")
    
    def exit_app(self):
        """إغلاق البرنامج"""
        self._safe_destroy()
        if messagebox.askyesno("تأكيد الخروج", "هل تريد إغلاق البرنامج؟"):
            self.parent.on_closing()
    
    def counter_closing(self):
        """إغلاق الكاشير"""
        self._safe_destroy()
        messagebox.showinfo("إغلاق الكاشير", "سيتم فتح صفحة إغلاق الكاشير قريباً")
    
    def logout(self):
        """تسجيل الخروج"""
        self._safe_destroy()
        if messagebox.askyesno("تسجيل الخروج", "هل تريد تسجيل الخروج؟"):
            messagebox.showinfo("تسجيل الخروج", "تم تسجيل الخروج بنجاح")
            self.parent.on_closing()


class DashboardWindow(ctk.CTkToplevel):
    """نافذة لوحة التحكم الرئيسية"""

    SIDEBAR_BG  = "#1e2a3a"
    HEADER_BG   = "#ffffff"
    CONTENT_BG  = "#f0f2f5"

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Dashboard – AP SOFT | WASH HUB LAUNDRY")
        self.geometry("1200x700")
        self.state("zoomed")
        self.lift()
        self.focus_force()
        self._chart_filter = tk.StringVar(value="This Week")
        self._build()
        self.after(100, self._load_data)

    # ------------------------------------------------------------------ build
    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=self.HEADER_BG, height=44)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkButton(top, text="☰", width=40, height=40,
                      fg_color=self.HEADER_BG, hover_color="#e8eef7",
                      text_color="#333", font=ctk.CTkFont(size=18),
                      command=self._toggle_sidebar).pack(side="left", padx=4)

        self._info_lbl = ctk.CTkLabel(
            top, text=self._top_info(), font=ctk.CTkFont(size=11),
            text_color="#555"
        )
        self._info_lbl.pack(side="left", padx=8)

        ctk.CTkLabel(top, text="SMTP Not Set", font=ctk.CTkFont(size=11),
                     text_color="#e74c3c").pack(side="left", padx=8)

        # right side of top bar
        right_top = ctk.CTkFrame(top, fg_color=self.HEADER_BG)
        right_top.pack(side="right", padx=10)
        ctk.CTkLabel(right_top, text="🔔", font=ctk.CTkFont(size=16),
                     text_color="#2b5797").pack(side="left", padx=6)
        ctk.CTkLabel(right_top, text="Admin ▼", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#2b5797").pack(side="left", padx=4)
        ctk.CTkLabel(right_top, text="👤", font=ctk.CTkFont(size=18)).pack(side="left", padx=4)

        # Separator
        sep = tk.Frame(self, bg="#dde3ec", height=1)
        sep.pack(fill="x")

        # Main row: sidebar + content
        self._main_row = ctk.CTkFrame(self, fg_color=self.CONTENT_BG)
        self._main_row.pack(fill="both", expand=True)
        self._main_row.columnconfigure(1, weight=1)
        self._main_row.rowconfigure(0, weight=1)

        self._sidebar_visible = True
        self._build_sidebar()
        self._build_content()

    def _top_info(self):
        now = datetime.now().strftime("%d/%b %I:%M:%S %p")
        return (f"Branch : NIL   Timezone : Asia/Dubai   Currency : AED   "
                f"Language : English   Last Active : {now}")

    # ---------------------------------------------------------------- sidebar
    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self._main_row, fg_color=self.SIDEBAR_BG, width=160
        )
        self._sidebar.grid(row=0, column=0, sticky="ns")
        self._sidebar.grid_propagate(False)

        # Logo area — use logo.png if available
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="#162030", height=72)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        _logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        _logo_inner = ctk.CTkFrame(logo_frame, fg_color="transparent")
        _logo_inner.place(relx=0.5, rely=0.5, anchor="center")
        if os.path.exists(_logo_path):
            try:
                _pil = Image.open(_logo_path).convert("RGBA")
                _pil.thumbnail((36, 36), Image.LANCZOS)
                self._sidebar_logo_img = ImageTk.PhotoImage(_pil)
                ctk.CTkLabel(_logo_inner, image=self._sidebar_logo_img, text="").pack(
                    side="left", padx=(0, 6))
            except Exception:
                self._sidebar_logo_img = None
        else:
            self._sidebar_logo_img = None
        if not self._sidebar_logo_img:
            _icon_box = ctk.CTkFrame(_logo_inner, fg_color="#0e9e8e",
                                     width=30, height=30, corner_radius=6)
            _icon_box.pack(side="left", padx=(0, 6))
        _txt_col = ctk.CTkFrame(_logo_inner, fg_color="transparent")
        _txt_col.pack(side="left")
        ctk.CTkLabel(_txt_col, text="AP SOFT",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(_txt_col, text="WASH HUB",
                     font=ctk.CTkFont(size=8),
                     text_color="#9ab").pack(anchor="w")

        # Welcome
        welcome = ctk.CTkFrame(self._sidebar, fg_color="#253548", height=56)
        welcome.pack(fill="x")
        welcome.pack_propagate(False)
        wf = ctk.CTkFrame(welcome, fg_color="transparent")
        wf.pack(expand=True)
        ctk.CTkLabel(wf, text="👤", font=ctk.CTkFont(size=22),
                     text_color="#aab").pack(side="left", padx=6)
        name_col = ctk.CTkFrame(wf, fg_color="transparent")
        name_col.pack(side="left")
        ctk.CTkLabel(name_col, text="Welcome,", font=ctk.CTkFont(size=10),
                     text_color="#aab").pack(anchor="w")
        ctk.CTkLabel(name_col, text="Admin", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="white").pack(anchor="w")

        # Nav items
        nav_items = [
            ("📊", "Dashboard"),
            ("🛒", "Sales"),
            ("📦", "Products"),
            ("👥", "Customers"),
            ("📈", "Reports"),
            ("🏦", "Accounts"),
        ]
        self._nav_btns = {}
        self._products_submenu_visible = False
        self._products_sub_frame = None

        for icon, label in nav_items:
            if label == "Sales":
                cmd = self._close_and_go_sales
            elif label == "Products":
                cmd = self._toggle_products_submenu
            elif label == "Customers":
                cmd = self._open_customers
            elif label == "Reports":
                cmd = self._open_reports
            elif label == "Accounts":
                cmd = self._open_accounts
            else:
                cmd = lambda l=label: None

            btn = ctk.CTkButton(
                self._sidebar, text=f"  {icon}  {label}",
                anchor="w", width=160, height=38,
                fg_color=self.SIDEBAR_BG if label != "Dashboard" else "#2b5797",
                hover_color="#2b5797",
                text_color="white", font=ctk.CTkFont(size=12),
                corner_radius=0,
                command=cmd
            )
            btn.pack(fill="x")
            self._nav_btns[label] = btn

            if label == "Products":
                self._products_sub_frame = ctk.CTkFrame(
                    self._sidebar, fg_color="#253548"
                )

    def _toggle_products_submenu(self):
        self._products_submenu_visible = not self._products_submenu_visible
        if self._products_submenu_visible:
            self._products_sub_frame.pack(fill="x", after=self._nav_btns["Products"])
            if not self._products_sub_frame.winfo_children():
                sub_items = [
                    ("Products",      self._open_products),
                    ("Categories",    self._open_categories),
                    ("Product Units", self._open_units),
                    ("Multi Rate",    self._open_multi_rate),
                ]
                for name, cmd in sub_items:
                    ctk.CTkButton(
                        self._products_sub_frame,
                        text=f"    •  {name}",
                        anchor="w", width=160, height=32,
                        fg_color="#253548", hover_color="#2b5797",
                        text_color="#cce", font=ctk.CTkFont(size=11),
                        corner_radius=0, command=cmd
                    ).pack(fill="x")
            self._nav_btns["Products"].configure(text="  📦  Products  ▲")
        else:
            self._products_sub_frame.pack_forget()
            self._nav_btns["Products"].configure(text="  📦  Products")

    def _open_products(self):
        from database import DatabaseManager
        db = DatabaseManager()
        ProductManagementWindow(self, db)

    def _open_categories(self):
        CategoriesDialog(self)

    def _open_units(self):
        ProductUnitsDialog(self)

    def _open_multi_rate(self):
        MultiRateDialog(self)

    def _open_customers(self):
        from database import DatabaseManager
        from customer_manager import CustomerManagementWindow
        db = DatabaseManager()
        CustomerManagementWindow(self, db)

    def _open_reports(self):
        ReportsWindow(self)

    def _open_accounts(self):
        AccountsWindow(self)

    def _close_and_go_sales(self):
        """إغلاق لوحة التحكم والعودة للنافذة الرئيسية"""
        self.destroy()
        try:
            self.parent.lift()
            self.parent.focus_force()
        except Exception:
            pass

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self._sidebar.grid_remove()
        else:
            self._sidebar.grid()
        self._sidebar_visible = not self._sidebar_visible

    # --------------------------------------------------------------- content
    def _build_content(self):
        self._content_frame = ctk.CTkScrollableFrame(
            self._main_row, fg_color=self.CONTENT_BG
        )
        self._content_frame.grid(row=0, column=1, sticky="nsew")

        # Quick action cards row
        cards_row = ctk.CTkFrame(self._content_frame, fg_color=self.CONTENT_BG)
        cards_row.pack(fill="x", padx=16, pady=(16, 8))

        self._orders_card = self._make_action_card(
            cards_row, "🛒", "Orders", "#7b5ea7", self._go_orders)
        self._orders_card.pack(side="left", padx=(0, 12))

        self._sales_card = self._make_action_card(
            cards_row, "🎁", "Sales", "#6aaa2a", self._go_sales)
        self._sales_card.pack(side="left")

        # Middle section: chart | balance | widgets
        mid = ctk.CTkFrame(self._content_frame, fg_color=self.CONTENT_BG)
        mid.pack(fill="x", padx=16, pady=8)
        mid.columnconfigure(0, weight=3)
        mid.columnconfigure(1, weight=2)
        mid.columnconfigure(2, weight=2)

        self._chart_frame = self._build_chart_card(mid)
        self._chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._balance_frame = self._build_balance_card(mid)
        self._balance_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        self._widget_frame = self._build_widget_card(mid)
        self._widget_frame.grid(row=0, column=2, sticky="nsew")

        # Stats row
        stats_row = ctk.CTkFrame(self._content_frame, fg_color=self.CONTENT_BG)
        stats_row.pack(fill="x", padx=16, pady=8)
        for i in range(4):
            stats_row.columnconfigure(i, weight=1)

        stat_defs = [
            ("TODAYS ORDER",  "📝", "today"),
            ("THIS WEEK",     "📈", "week"),
            ("THIS MONTH",    "📅", "month"),
            ("THIS YEAR",     "📋", "year"),
        ]
        self._stat_labels = {}
        for col, (title, icon, key) in enumerate(stat_defs):
            card = ctk.CTkFrame(stats_row, fg_color="white",
                                corner_radius=8, border_width=1, border_color="#dde3ec")
            card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0), pady=4)
            inner = ctk.CTkFrame(card, fg_color="white")
            inner.pack(fill="both", expand=True, padx=14, pady=12)
            ctk.CTkLabel(inner, text=title,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#333").pack(anchor="w")
            cnt_lbl = ctk.CTkLabel(inner, text="Order Count : –",
                                   font=ctk.CTkFont(size=11), text_color="#555")
            cnt_lbl.pack(anchor="w", pady=(4, 0))
            amt_lbl = ctk.CTkLabel(inner, text="Order Amount : –",
                                   font=ctk.CTkFont(size=11), text_color="#555")
            amt_lbl.pack(anchor="w")
            # icon on right
            icon_lbl = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=30),
                                    text_color="#2b5797")
            icon_lbl.place(relx=1.0, rely=0.5, x=-14, anchor="e")
            self._stat_labels[key] = (cnt_lbl, amt_lbl)

    def _make_action_card(self, parent, icon, label, color, cmd):
        hover = {"#7b5ea7": "#6a4d96", "#6aaa2a": "#5a9920"}.get(color, color)
        card = ctk.CTkButton(
            parent, text=f"{icon}   {label}",
            fg_color=color, hover_color=hover,
            text_color="white", font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8, command=cmd,
            width=220, height=72
        )
        return card

    # ---------------------------------------------------------- chart card
    def _build_chart_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white",
                            corner_radius=8, border_width=1, border_color="#dde3ec")

        top_bar = ctk.CTkFrame(card, fg_color="white")
        top_bar.pack(fill="x", padx=10, pady=(8, 0))

        # Toggle OK button
        self._chart_ok = ctk.CTkButton(
            top_bar, text="OK", width=48, height=26,
            fg_color="#2ecc71", hover_color="#27ae60",
            text_color="white", font=ctk.CTkFont(size=11),
            corner_radius=13, command=self._refresh_chart
        )
        self._chart_ok.pack(side="left", padx=(0, 8))

        for opt in ("Previous Week", "This Week"):
            ctk.CTkButton(
                top_bar, text=f"{opt} ▼", width=110, height=26,
                fg_color="white", text_color="#555", hover_color="#e8eef7",
                border_width=1, border_color="#ccc",
                font=ctk.CTkFont(size=11), corner_radius=4
            ).pack(side="left", padx=2)

        # Canvas for bar chart
        self._chart_canvas = tk.Canvas(card, bg="white", height=200, highlightthickness=0)
        self._chart_canvas.pack(fill="x", padx=10, pady=(6, 10))
        return card

    def _draw_chart(self, daily_data):
        """Draw a simple bar chart from {day_name: amount} dict."""
        c = self._chart_canvas
        c.delete("all")
        c.update_idletasks()
        W = c.winfo_width() or 400
        H = 200
        pad_l, pad_r, pad_t, pad_b = 40, 10, 10, 30
        values = list(daily_data.values())
        max_val = max(values) if values and max(values) > 0 else 1
        bar_color = "#90e4da"
        n = len(daily_data)
        slot_w = (W - pad_l - pad_r) / max(n, 1)
        bar_w = slot_w * 0.55

        # Y axis labels
        for i in range(5):
            y_val = max_val * (4 - i) / 4
            y_px = pad_t + (H - pad_t - pad_b) * i / 4
            c.create_text(pad_l - 4, y_px, text=f"{y_val:,.0f}",
                          anchor="e", font=("Arial", 8), fill="#888")
            c.create_line(pad_l, y_px, W - pad_r, y_px, fill="#eee")

        for idx, (day, val) in enumerate(daily_data.items()):
            x_center = pad_l + idx * slot_w + slot_w / 2
            bar_h = (H - pad_t - pad_b) * val / max_val
            x0 = x_center - bar_w / 2
            x1 = x_center + bar_w / 2
            y0 = H - pad_b - bar_h
            y1 = H - pad_b
            c.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="")
            c.create_text(x_center, H - pad_b + 4, text=day[:3],
                          anchor="n", font=("Arial", 8), fill="#555")

    # --------------------------------------------------------- balance card
    def _build_balance_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white",
                            corner_radius=8, border_width=1, border_color="#dde3ec")

        hdr = ctk.CTkFrame(card, fg_color="white")
        hdr.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkLabel(hdr, text="Account Balance",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#333").pack(side="left")
        ctk.CTkLabel(hdr, text="This Week ▼",
                     font=ctk.CTkFont(size=11), text_color="#2b5797").pack(side="right")

        # Cash Account row
        cash_row = ctk.CTkFrame(card, fg_color="#1abc9c", corner_radius=4, height=36)
        cash_row.pack(fill="x", padx=10, pady=(2, 2))
        cash_row.pack_propagate(False)
        ctk.CTkLabel(cash_row, text="Cash Account",
                     font=ctk.CTkFont(size=11), text_color="white").pack(side="left", padx=10, pady=8)
        self._cash_lbl = ctk.CTkLabel(cash_row, text="0.00 AED",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color="white")
        self._cash_lbl.pack(side="right", padx=10)

        # Credit Card row
        cc_row = ctk.CTkFrame(card, fg_color="#2c3e50", corner_radius=4, height=36)
        cc_row.pack(fill="x", padx=10, pady=(2, 2))
        cc_row.pack_propagate(False)
        ctk.CTkLabel(cc_row, text="Credit Card Undeposited",
                     font=ctk.CTkFont(size=11), text_color="white").pack(side="left", padx=10, pady=8)
        self._cc_lbl = ctk.CTkLabel(cc_row, text="0.00 AED",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    text_color="white")
        self._cc_lbl.pack(side="right", padx=10)

        # Spacer
        ctk.CTkFrame(card, fg_color="white", height=10).pack(fill="x")

        # Total row
        tot_row = ctk.CTkFrame(card, fg_color="#c0392b", corner_radius=4, height=36)
        tot_row.pack(fill="x", padx=10, pady=(2, 10))
        tot_row.pack_propagate(False)
        ctk.CTkLabel(tot_row, text="Total",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="white").pack(side="left", padx=10, pady=8)
        self._total_lbl = ctk.CTkLabel(tot_row, text="0.00 AED",
                                       font=ctk.CTkFont(size=11, weight="bold"),
                                       text_color="white")
        self._total_lbl.pack(side="right", padx=10)
        return card

    # --------------------------------------------------------- widget card
    def _build_widget_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white",
                            corner_radius=8, border_width=1, border_color="#dde3ec")
        hdr_row = ctk.CTkFrame(card, fg_color="white")
        hdr_row.pack(fill="x", padx=12, pady=(10, 0))
        ctk.CTkLabel(hdr_row, text="Widgets",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#333").pack(side="left")
        ctk.CTkButton(hdr_row, text="+ Add", width=54, height=24,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=10),
                      corner_radius=4, command=self._add_widget).pack(side="right")

        self._widgets_scroll = ctk.CTkScrollableFrame(card, fg_color="#f7f9fc", corner_radius=6)
        self._widgets_scroll.pack(fill="both", expand=True, padx=10, pady=(8, 10))

        # Placeholder shown when no widgets added
        self._widgets_placeholder = ctk.CTkFrame(self._widgets_scroll, fg_color="transparent")
        self._widgets_placeholder.pack(fill="both", expand=True)
        ctk.CTkLabel(self._widgets_placeholder, text="Add New Widget",
                     font=ctk.CTkFont(size=13), text_color="#aaa").pack(pady=(30, 6))
        ctk.CTkLabel(self._widgets_placeholder, text="Click '+ Add' above",
                     font=ctk.CTkFont(size=10), text_color="#ccc").pack()

        self._widget_count = 0
        ctk.CTkButton(card, text="Save position", width=110, height=30,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=11),
                      corner_radius=5, command=self._save_pos).pack(anchor="se", padx=10, pady=(0, 10))
        return card

    def _add_widget_to_dashboard(self, icon, name):
        """Physically add a widget card to the widget panel."""
        if self._widget_count == 0:
            self._widgets_placeholder.pack_forget()
        self._widget_count += 1

        wcard = ctk.CTkFrame(self._widgets_scroll, fg_color="white",
                             corner_radius=6, border_width=1,
                             border_color="#dde3ec", height=50)
        wcard.pack(fill="x", pady=2)
        wcard.pack_propagate(False)

        ctk.CTkLabel(wcard, text=icon, font=ctk.CTkFont(size=18),
                     text_color="#2b5797").place(x=8, rely=0.5, anchor="w")
        ctk.CTkLabel(wcard, text=name, font=ctk.CTkFont(size=11),
                     text_color="#333").place(x=36, rely=0.5, anchor="w")

        def _remove(c=wcard):
            c.destroy()
            self._widget_count -= 1
            if self._widget_count == 0:
                self._widgets_placeholder.pack(fill="both", expand=True)

        ctk.CTkButton(wcard, text="×", width=24, height=24,
                      fg_color="#eee", hover_color="#f0a0a0",
                      text_color="#555", corner_radius=12,
                      font=ctk.CTkFont(size=14),
                      command=_remove).place(relx=1.0, rely=0.5, x=-8, anchor="e")

    # ---------------------------------------------------------- data loading
    def _load_data(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            today = datetime.now().strftime("%d-%m-%Y")
            now = datetime.now()

            def week_start():
                return (now - timedelta(days=now.weekday())).strftime("%d-%m-%Y")

            def month_start():
                return now.replace(day=1).strftime("%d-%m-%Y")

            def year_start():
                return now.replace(month=1, day=1).strftime("%d-%m-%Y")

            def query(from_date, to_date=None):
                if to_date is None:
                    to_date = today
                cur.execute(
                    "SELECT COUNT(*), COALESCE(SUM(subtotal),0) FROM invoices "
                    "WHERE date >= ? AND date <= ?",
                    (from_date, to_date)
                )
                return cur.fetchone()

            stats = {
                "today": query(today),
                "week":  query(week_start()),
                "month": query(month_start()),
                "year":  query(year_start()),
            }
            for key, (cnt, amt) in stats.items():
                cnt_lbl, amt_lbl = self._stat_labels[key]
                cnt_lbl.configure(text=f"Order Count : {cnt}")
                amt_lbl.configure(text=f"Order Amount : {amt:,.2f} AED")

            # Account balance: cash vs credit
            cur.execute(
                "SELECT COALESCE(SUM(subtotal),0) FROM invoices "
                "WHERE date >= ? AND customer_type='Cash Customer'", (week_start(),))
            cash_total = cur.fetchone()[0]

            cur.execute(
                "SELECT COALESCE(SUM(subtotal),0) FROM invoices "
                "WHERE date >= ? AND customer_type!='Cash Customer'", (week_start(),))
            cc_total = cur.fetchone()[0]

            self._cash_lbl.configure(text=f"{cash_total:,.2f} AED")
            self._cc_lbl.configure(text=f"{cc_total:,.2f} AED")
            self._total_lbl.configure(text=f"{cash_total + cc_total:,.2f} AED")

            # Chart: daily totals for this week
            daily = {}
            for i in range(7):
                d = (now - timedelta(days=6 - i))
                day_str = d.strftime("%d-%m-%Y")
                day_name = d.strftime("%a")
                cur.execute(
                    "SELECT COALESCE(SUM(subtotal),0) FROM invoices WHERE date=?",
                    (day_str,))
                daily[day_name] = cur.fetchone()[0]

            conn.close()
            self._daily_data = daily
            self.after(50, lambda: self._draw_chart(daily))

        except Exception as e:
            print(f"Dashboard data error: {e}")

    def _refresh_chart(self):
        if hasattr(self, '_daily_data'):
            self._draw_chart(self._daily_data)

    def _add_widget(self):
        WidgetPickerDialog(self)

    def _save_pos(self):
        messagebox.showinfo("Saved", "Dashboard layout position saved.", parent=self)

    def _go_orders(self):
        OrdersDialog(self)

    def _go_sales(self):
        SalesDialog(self)


class OrdersDialog(ctk.CTkToplevel):
    """قائمة الطلبات / الفواتير"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Orders")
        self.geometry("1000x580")
        self.lift()
        self.focus_force()
        self._build()
        self.after(100, self._load)

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#7b5ea7", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🛒  Orders",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=8)
        ctk.CTkButton(hdr, text="✕", width=32, height=30,
                      fg_color="#5a3d96", hover_color="#c0392b",
                      text_color="white", corner_radius=4,
                      command=self.destroy).pack(side="right", padx=10)

        cols = ("inv", "date", "customer", "service", "amount", "status")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=22)
        headers = {"inv": "Invoice #", "date": "Date", "customer": "Customer",
                   "service": "Service Type", "amount": "Amount (AED)", "status": "Status"}
        widths  = {"inv": 110, "date": 100, "customer": 200,
                   "service": 160, "amount": 120, "status": 90}
        for c in cols:
            self._tree.heading(c, text=headers[c])
            self._tree.column(c, width=widths[c], anchor="center")

        style = ttk.Style()
        style.configure("Orders.Treeview.Heading",
                        font=("Arial", 10, "bold"), foreground="#2b5797")
        style.configure("Orders.Treeview", rowheight=26, font=("Arial", 10))
        self._tree.configure(style="Orders.Treeview")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=10)
        self._tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _load(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            cur.execute("""
                SELECT i.invoice_number, i.date,
                       COALESCE(c.name, 'Cash Customer'),
                       i.service_type, i.subtotal, i.status
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                ORDER BY i.id DESC LIMIT 500
            """)
            self._tree.tag_configure("even", background="#f7f9fc")
            for idx, row in enumerate(cur.fetchall()):
                tag = "even" if idx % 2 == 0 else ""
                self._tree.insert("", "end", tags=(tag,), values=(
                    row[0], row[1], row[2], row[3],
                    f"{row[4]:,.2f}", row[5]
                ))
            conn.close()
        except Exception as e:
            print(f"OrdersDialog error: {e}")


class SalesDialog(ctk.CTkToplevel):
    """ملخص المبيعات"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sales")
        self.geometry("700x540")
        self.lift()
        self.focus_force()
        self._build()
        self.after(100, self._load)

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#6aaa2a", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🎁  Sales Summary",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=8)
        ctk.CTkButton(hdr, text="✕", width=32, height=30,
                      fg_color="#4a8a1a", hover_color="#c0392b",
                      text_color="white", corner_radius=4,
                      command=self.destroy).pack(side="right", padx=10)
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="#f0f2f5")
        self._scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def _load(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            now = datetime.now()
            today   = now.strftime("%d-%m-%Y")
            week_s  = (now - timedelta(days=now.weekday())).strftime("%d-%m-%Y")
            month_s = now.replace(day=1).strftime("%d-%m-%Y")
            year_s  = now.replace(month=1, day=1).strftime("%d-%m-%Y")

            periods = [
                ("Today",      today,   today, "#2ecc71"),
                ("This Week",  week_s,  today, "#3498db"),
                ("This Month", month_s, today, "#9b59b6"),
                ("This Year",  year_s,  today, "#e67e22"),
            ]
            for label, frm, to, color in periods:
                cur.execute(
                    "SELECT COUNT(*), COALESCE(SUM(subtotal),0) "
                    "FROM invoices WHERE date >= ? AND date <= ?",
                    (frm, to))
                cnt, amt = cur.fetchone()
                card = ctk.CTkFrame(self._scroll, fg_color=color,
                                    corner_radius=8, height=64)
                card.pack(fill="x", pady=4)
                card.pack_propagate(False)
                ctk.CTkLabel(card, text=label,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color="white").place(x=14, rely=0.3, anchor="w")
                ctk.CTkLabel(card, text=f"Orders: {cnt}",
                             font=ctk.CTkFont(size=11),
                             text_color="white").place(x=14, rely=0.7, anchor="w")
                ctk.CTkLabel(card, text=f"{amt:,.2f} AED",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color="white").place(relx=1.0, rely=0.5, x=-14, anchor="e")

            # By service type
            ctk.CTkLabel(self._scroll, text="Sales by Service Type (This Year)",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#333").pack(anchor="w", pady=(12, 4))
            cur.execute("""
                SELECT service_type, COUNT(*), COALESCE(SUM(subtotal),0)
                FROM invoices WHERE date >= ?
                GROUP BY service_type ORDER BY SUM(subtotal) DESC
            """, (year_s,))
            rows = cur.fetchall()
            conn.close()

            svc_colors = ["#2b5797", "#1abc9c", "#e67e22", "#9b59b6", "#e74c3c"]
            tbl = ctk.CTkFrame(self._scroll, fg_color="white",
                               corner_radius=8, border_width=1, border_color="#dde3ec")
            tbl.pack(fill="x", pady=4)
            for i, (stype, cnt, amt) in enumerate(rows):
                bg = "#f7f9fc" if i % 2 == 0 else "white"
                row_f = ctk.CTkFrame(tbl, fg_color=bg, height=36)
                row_f.pack(fill="x", padx=4, pady=1)
                row_f.pack_propagate(False)
                dot = svc_colors[i % len(svc_colors)]
                ctk.CTkFrame(row_f, fg_color=dot, width=10, height=10,
                             corner_radius=5).place(x=10, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=stype, font=ctk.CTkFont(size=11),
                             text_color="#333").place(x=28, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=f"{cnt} orders",
                             font=ctk.CTkFont(size=11),
                             text_color="#888").place(relx=0.58, rely=0.5, anchor="w")
                ctk.CTkLabel(row_f, text=f"{amt:,.2f} AED",
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color="#2b5797").place(relx=1.0, rely=0.5, x=-12, anchor="e")
        except Exception as e:
            print(f"SalesDialog error: {e}")


class WidgetPickerDialog(ctk.CTkToplevel):
    """اختيار Widget للوحة التحكم"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Widget")
        self.geometry("420x400")
        self.resizable(False, False)
        self.lift()
        self.focus_force()
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Add New Widget",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=8)
        ctk.CTkButton(hdr, text="✕", width=32, height=30,
                      fg_color="#1a3f73", hover_color="#c0392b",
                      text_color="white", corner_radius=4,
                      command=self.destroy).pack(side="right", padx=10)

        ctk.CTkLabel(self, text="Choose a widget to add to your dashboard:",
                     font=ctk.CTkFont(size=12), text_color="#555").pack(
            pady=(12, 6), padx=16, anchor="w")

        widgets_list = [
            ("📊", "Sales Chart",       "Weekly sales bar chart"),
            ("💰", "Account Balance",   "Cash & credit summary"),
            ("📋", "Recent Orders",     "Latest 10 invoices"),
            ("📅", "Monthly Summary",   "Month-to-date statistics"),
            ("👥", "Top Customers",     "Highest spending customers"),
            ("🏷️", "Top Services",      "Most popular service types"),
        ]

        scroll = ctk.CTkScrollableFrame(self, fg_color="#f5f7fa", height=280)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for icon, name, desc in widgets_list:
            row = ctk.CTkFrame(scroll, fg_color="white", corner_radius=6,
                               border_width=1, border_color="#dde3ec", height=54)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=22),
                         text_color="#2b5797").place(x=10, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=name,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#333").place(x=46, rely=0.3, anchor="w")
            ctk.CTkLabel(row, text=desc,
                         font=ctk.CTkFont(size=10), text_color="#888").place(
                x=46, rely=0.72, anchor="w")
            ctk.CTkButton(row, text="Add", width=56, height=28,
                          fg_color="#2b5797", hover_color="#1a3f73",
                          text_color="white", font=ctk.CTkFont(size=11),
                          corner_radius=4,
                          command=lambda ic=icon, n=name: self._add(ic, n)).place(
                relx=1.0, rely=0.5, x=-10, anchor="e")

    def _add(self, icon, name):
        # Add widget to parent dashboard
        if hasattr(self.master, '_add_widget_to_dashboard'):
            self.master._add_widget_to_dashboard(icon, name)
        else:
            messagebox.showinfo("Widget Added", f"'{name}' added!", parent=self)
        self.destroy()


class CategoriesDialog(ctk.CTkToplevel):
    """\u0625\u062f\u0627\u0631\u0629 \u0641\u0626\u0627\u062a \u0627\u0644\u0645\u0646\u062a\u062c\u0627\u062a"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Categories")
        self.geometry("600x480")
        self.lift()
        self.focus_force()
        self._init_table()
        self._build()
        self._load()

    def _init_table(self):
        conn = sqlite3.connect('laundry_system.db')
        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT ''
            )""")
        conn.commit()
        conn.close()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🏷️  Categories",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(side="left", padx=14, pady=8)

        # Add row
        add_row = ctk.CTkFrame(self, fg_color="#f5f7fa")
        add_row.pack(fill="x", padx=10, pady=(8, 4))
        self._new_cat = ctk.CTkEntry(add_row, placeholder_text="Category name",
                                     width=220, height=32)
        self._new_cat.pack(side="left", padx=(0, 6))
        self._new_desc = ctk.CTkEntry(add_row, placeholder_text="Description (optional)",
                                      width=240, height=32)
        self._new_desc.pack(side="left", padx=(0, 6))
        ctk.CTkButton(add_row, text="+ Add", width=80, height=32,
                      fg_color="#27ae60", hover_color="#1e8449",
                      command=self._add).pack(side="left")

        # Treeview
        cols = ("id", "name", "desc")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        self._tree.heading("id",   text="#");    self._tree.column("id",   width=40)
        self._tree.heading("name", text="Name"); self._tree.column("name", width=200)
        self._tree.heading("desc", text="Description"); self._tree.column("desc", width=300)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=6)
        self._tree.pack(fill="both", expand=True, padx=10, pady=4)

        btn_row = ctk.CTkFrame(self, fg_color="#f5f7fa")
        btn_row.pack(fill="x", padx=10, pady=6)
        ctk.CTkButton(btn_row, text="\u2702  Delete", width=100, height=30,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      command=self._delete).pack(side="left", padx=(0, 6))

    def _load(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        conn = sqlite3.connect('laundry_system.db')
        for row in conn.execute("SELECT id, name, description FROM product_categories ORDER BY name"):
            self._tree.insert("", "end", values=row)
        conn.close()

    def _add(self):
        name = self._new_cat.get().strip()
        desc = self._new_desc.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Category name is required.", parent=self)
            return
        try:
            conn = sqlite3.connect('laundry_system.db')
            conn.execute("INSERT INTO product_categories (name, description) VALUES (?,?)", (name, desc))
            conn.commit(); conn.close()
            self._new_cat.delete(0, 'end')
            self._new_desc.delete(0, 'end')
            self._load()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Category '{name}' already exists.", parent=self)

    def _delete(self):
        sel = self._tree.selection()
        if not sel:
            return
        row_id = self._tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this category?", parent=self):
            conn = sqlite3.connect('laundry_system.db')
            conn.execute("DELETE FROM product_categories WHERE id=?", (row_id,))
            conn.commit(); conn.close()
            self._load()


class ProductUnitsDialog(ctk.CTkToplevel):
    """\u0625\u062f\u0627\u0631\u0629 \u0648\u062d\u062f\u0627\u062a \u0627\u0644\u0645\u0646\u062a\u062c\u0627\u062a (pcs, kg, \u0644\u062a\u0631 ...)"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Product Units")
        self.geometry("480x440")
        self.lift()
        self.focus_force()
        self._init_table()
        self._build()
        self._load()

    def _init_table(self):
        conn = sqlite3.connect('laundry_system.db')
        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_units (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT UNIQUE NOT NULL,
                abbrev TEXT DEFAULT ''
            )""")
        # seed defaults
        for u, a in [("Piece","pcs"),("Kilogram","kg"),("Litre","ltr"),("Pair","pr")]:
            try:
                conn.execute("INSERT OR IGNORE INTO product_units (name,abbrev) VALUES (?,?)", (u, a))
            except Exception:
                pass
        conn.commit()
        conn.close()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="📐  Product Units",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(side="left", padx=14, pady=8)

        add_row = ctk.CTkFrame(self, fg_color="#f5f7fa")
        add_row.pack(fill="x", padx=10, pady=(8, 4))
        self._new_name = ctk.CTkEntry(add_row, placeholder_text="Unit name (e.g. Piece)",
                                      width=200, height=32)
        self._new_name.pack(side="left", padx=(0, 6))
        self._new_abbr = ctk.CTkEntry(add_row, placeholder_text="Abbrev (e.g. pcs)",
                                      width=110, height=32)
        self._new_abbr.pack(side="left", padx=(0, 6))
        ctk.CTkButton(add_row, text="+ Add", width=74, height=32,
                      fg_color="#27ae60", hover_color="#1e8449",
                      command=self._add).pack(side="left")

        cols = ("id", "name", "abbrev")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        self._tree.heading("id",     text="#");     self._tree.column("id",     width=40)
        self._tree.heading("name",   text="Unit");  self._tree.column("name",   width=220)
        self._tree.heading("abbrev", text="Abbrev");self._tree.column("abbrev", width=140)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=6)
        self._tree.pack(fill="both", expand=True, padx=10, pady=4)

        btn_row = ctk.CTkFrame(self, fg_color="#f5f7fa")
        btn_row.pack(fill="x", padx=10, pady=6)
        ctk.CTkButton(btn_row, text="\u2702  Delete", width=100, height=30,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      command=self._delete).pack(side="left")

    def _load(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        conn = sqlite3.connect('laundry_system.db')
        for row in conn.execute("SELECT id, name, abbrev FROM product_units ORDER BY name"):
            self._tree.insert("", "end", values=row)
        conn.close()

    def _add(self):
        name = self._new_name.get().strip()
        abbr = self._new_abbr.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Unit name is required.", parent=self)
            return
        try:
            conn = sqlite3.connect('laundry_system.db')
            conn.execute("INSERT INTO product_units (name,abbrev) VALUES (?,?)", (name, abbr))
            conn.commit(); conn.close()
            self._new_name.delete(0, 'end')
            self._new_abbr.delete(0, 'end')
            self._load()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Unit '{name}' already exists.", parent=self)

    def _delete(self):
        sel = self._tree.selection()
        if not sel:
            return
        row_id = self._tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this unit?", parent=self):
            conn = sqlite3.connect('laundry_system.db')
            conn.execute("DELETE FROM product_units WHERE id=?", (row_id,))
            conn.commit(); conn.close()
            self._load()


class MultiRateDialog(ctk.CTkToplevel):
    """\u0625\u062f\u0627\u0631\u0629 \u0623\u0633\u0639\u0627\u0631 \u0645\u062a\u0639\u062f\u062f\u0629 \u0644\u0644\u062e\u062f\u0645\u0627\u062a"""

    RATE_COLS = [
        ("Wash & Press",        "price_wash_press"),
        ("Press Only",          "price_press_only"),
        ("Wash & Press Urgent", "price_wash_press_urgent"),
        ("Press Urgent",        "price_press_urgent"),
        ("Contract",            "price_contract"),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Multi Rate")
        self.geometry("860x520")
        self.lift()
        self.focus_force()
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="💲  Multi Rate",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(side="left", padx=14, pady=8)

        # Search
        top = ctk.CTkFrame(self, fg_color="#f5f7fa")
        top.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(top, text="Search:", font=ctk.CTkFont(size=12),
                     text_color="#555").pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        ctk.CTkEntry(top, textvariable=self._search_var,
                     placeholder_text="Filter by product name...",
                     width=260, height=30).pack(side="left")
        ctk.CTkButton(top, text="💾  Save Changes", width=130, height=30,
                      fg_color="#27ae60", hover_color="#1e8449",
                      command=self._save).pack(side="right")

        # Treeview with editable feel (edit on double-click)
        tree_cols = ["id", "name"] + [c[0] for c in self.RATE_COLS]
        self._tree = ttk.Treeview(self, columns=tree_cols, show="headings", height=18)
        widths = {"id": 36, "name": 160,
                  "Wash & Press": 110, "Press Only": 95,
                  "Wash & Press Urgent": 150, "Press Urgent": 100, "Contract": 90}
        for c in tree_cols:
            self._tree.heading(c, text=c.replace("_"," ").title() if c not in ("id","name") else c.upper() if c=="id" else "Product")
            self._tree.column(c, width=widths.get(c, 100), anchor="center")
        self._tree.column("name", anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=6)
        self._tree.pack(fill="both", expand=True, padx=10, pady=4)
        self._tree.bind("<Double-1>", self._on_double_click)

        ctk.CTkLabel(self, text="💡 Double-click a price cell to edit it.",
                     font=ctk.CTkFont(size=10), text_color="#888").pack(anchor="w", padx=12, pady=(0,4))

        self._all_rows = []

    def _load(self):
        self._all_rows = []
        conn = sqlite3.connect('laundry_system.db')
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, price_wash_press, price_press_only,
                   price_wash_press_urgent, price_press_urgent, price_contract
            FROM products ORDER BY name""")
        for row in cur.fetchall():
            self._all_rows.append(row)
        conn.close()
        self._filter()

    def _filter(self):
        q = self._search_var.get().lower()
        for i in self._tree.get_children():
            self._tree.delete(i)
        for row in self._all_rows:
            if q in row[1].lower():
                vals = [row[0], row[1]] + [f"{v:.2f}" for v in row[2:]]
                self._tree.insert("", "end", iid=str(row[0]), values=vals)

    def _on_double_click(self, event):
        item = self._tree.identify_row(event.y)
        col  = self._tree.identify_column(event.x)
        if not item or not col:
            return
        col_idx = int(col.lstrip("#")) - 1
        col_name = self._tree["columns"][col_idx]
        if col_name in ("id", "name"):
            return  # not editable

        # Get bounding box for cell
        x, y, w, h = self._tree.bbox(item, col)
        cur_val = self._tree.item(item)["values"][col_idx]

        entry = tk.Entry(self._tree, width=10,
                         font=("Arial", 11), justify="center",
                         bd=1, relief="solid")
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, cur_val)
        entry.select_range(0, 'end')
        entry.focus()

        def commit(e=None):
            val = entry.get().strip()
            try:
                float(val)  # validate
                vals = list(self._tree.item(item)["values"])
                vals[col_idx] = val
                self._tree.item(item, values=vals)
            except ValueError:
                pass
            entry.destroy()

        entry.bind("<Return>",    commit)
        entry.bind("<Tab>",       commit)
        entry.bind("<FocusOut>",  commit)
        entry.bind("<Escape>",    lambda e: entry.destroy())

    def _save(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            updated = 0
            for iid in self._tree.get_children():
                vals = self._tree.item(iid)["values"]
                prod_id = vals[0]
                prices  = [float(vals[2+i]) for i in range(5)]
                cur.execute("""
                    UPDATE products SET
                        price_wash_press=?, price_press_only=?,
                        price_wash_press_urgent=?, price_press_urgent=?,
                        price_contract=?
                    WHERE id=?""", (*prices, prod_id))
                updated += 1
            conn.commit(); conn.close()
            messagebox.showinfo("Saved", f"{updated} product rate(s) updated.", parent=self)
            self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Profile")
        self.geometry("900x620")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()

        # Center the window
        self.update_idletasks()
        pw = parent.winfo_x() + parent.winfo_width() // 2
        ph = parent.winfo_y() + parent.winfo_height() // 2
        self.geometry(f"900x620+{pw - 450}+{ph - 310}")

        self._build_ui()
        self._load_profile()

    def _build_ui(self):
        # ---- top bar ----
        top = ctk.CTkFrame(self, fg_color="#2b5797", height=45)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="Profile", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(side="left", padx=20, pady=10)

        # ---- tab bar ----
        tab_bar = ctk.CTkFrame(self, fg_color="white", height=38)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)
        self._active_tab = tk.StringVar(value="Profile")

        def switch_tab(name):
            self._active_tab.set(name)
            profile_frame.pack_forget()
            settings_frame.pack_forget()
            if name == "Profile":
                profile_frame.pack(fill="both", expand=True)
                tab_profile_btn.configure(fg_color="#e8eef7", text_color="#2b5797",
                                          border_color="#2b5797", border_width=2)
                tab_settings_btn.configure(fg_color="white", text_color="#555",
                                           border_width=0)
            else:
                settings_frame.pack(fill="both", expand=True)
                tab_settings_btn.configure(fg_color="#e8eef7", text_color="#2b5797",
                                           border_color="#2b5797", border_width=2)
                tab_profile_btn.configure(fg_color="white", text_color="#555",
                                          border_width=0)

        tab_profile_btn = ctk.CTkButton(
            tab_bar, text="Profile", width=90, height=30,
            fg_color="#e8eef7", text_color="#2b5797",
            hover_color="#d0ddf0", corner_radius=4,
            border_width=2, border_color="#2b5797",
            font=ctk.CTkFont(size=12),
            command=lambda: switch_tab("Profile")
        )
        tab_profile_btn.pack(side="left", padx=(10, 2), pady=4)

        tab_settings_btn = ctk.CTkButton(
            tab_bar, text="Settings", width=90, height=30,
            fg_color="white", text_color="#555",
            hover_color="#d0ddf0", corner_radius=4,
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=lambda: switch_tab("Settings")
        )
        tab_settings_btn.pack(side="left", padx=2, pady=4)

        # ---- Profile tab ----
        profile_frame = ctk.CTkScrollableFrame(self, fg_color="#f5f7fa")
        profile_frame.pack(fill="both", expand=True)

        # Avatar section
        avatar_frame = ctk.CTkFrame(profile_frame, fg_color="#f5f7fa")
        avatar_frame.pack(pady=(20, 10), padx=30, anchor="w")

        avatar_circle = ctk.CTkFrame(avatar_frame, width=80, height=80,
                                     fg_color="#c8d8f0", corner_radius=40)
        avatar_circle.pack(side="left")
        avatar_circle.pack_propagate(False)
        ctk.CTkLabel(avatar_circle, text="👤", font=ctk.CTkFont(size=36),
                     text_color="#2b5797").place(relx=0.5, rely=0.5, anchor="center")

        # + button on avatar
        plus_btn = ctk.CTkButton(
            avatar_frame, text="+", width=22, height=22,
            fg_color="#e74c3c", hover_color="#c0392b",
            text_color="white", corner_radius=11,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._change_avatar
        )
        plus_btn.place_forget()
        # place after avatar renders
        self.after(50, lambda: plus_btn.place(in_=avatar_circle, relx=1.0, rely=1.0,
                                              x=-4, y=-4, anchor="se"))

        # Fields grid
        fields_frame = ctk.CTkFrame(profile_frame, fg_color="white",
                                    corner_radius=8, border_width=1, border_color="#dde3ec")
        fields_frame.pack(fill="x", padx=30, pady=(0, 10))

        lbl_font = ctk.CTkFont(size=12)
        entry_font = ctk.CTkFont(size=12)

        def make_label(parent, text, row, col):
            ctk.CTkLabel(parent, text=text, font=lbl_font,
                         text_color="#2b5797", anchor="w").grid(
                row=row * 2, column=col, sticky="w", padx=15, pady=(10, 0))

        def make_entry(parent, row, col, textvariable=None):
            e = ctk.CTkEntry(parent, width=340, height=32, font=entry_font,
                             textvariable=textvariable,
                             fg_color="white", border_color="#ccc",
                             text_color="#333")
            e.grid(row=row * 2 + 1, column=col, sticky="ew", padx=15, pady=(2, 4))
            return e

        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)

        self.v_name     = tk.StringVar()
        self.v_city     = tk.StringVar()
        self.v_location = tk.StringVar()
        self.v_email    = tk.StringVar()
        self.v_tel      = tk.StringVar()
        self.v_fax      = tk.StringVar()
        self.v_mobile   = tk.StringVar()

        make_label(fields_frame, "Name",      0, 0); make_entry(fields_frame, 0, 0, self.v_name)
        make_label(fields_frame, "City",      0, 1); make_entry(fields_frame, 0, 1, self.v_city)
        make_label(fields_frame, "Location",  1, 0); make_entry(fields_frame, 1, 0, self.v_location)
        make_label(fields_frame, "Email",     1, 1); make_entry(fields_frame, 1, 1, self.v_email)
        make_label(fields_frame, "Telephone", 2, 0); make_entry(fields_frame, 2, 0, self.v_tel)
        make_label(fields_frame, "Fax",       2, 1); make_entry(fields_frame, 2, 1, self.v_fax)
        make_label(fields_frame, "Mobile",    3, 0); make_entry(fields_frame, 3, 0, self.v_mobile)

        # Address (full width)
        ctk.CTkLabel(fields_frame, text="Address", font=lbl_font,
                     text_color="#2b5797", anchor="w").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 0))
        self.addr_box = ctk.CTkTextbox(fields_frame, width=720, height=70,
                                       font=entry_font, fg_color="white",
                                       border_color="#ccc", border_width=2,
                                       text_color="#333")
        self.addr_box.grid(row=8, column=0, columnspan=2, sticky="ew", padx=15, pady=(2, 10))

        # External Communication Details
        ext_frame = ctk.CTkFrame(profile_frame, fg_color="white",
                                 corner_radius=8, border_width=1, border_color="#dde3ec")
        ext_frame.pack(fill="x", padx=30, pady=(0, 10))
        ext_frame.columnconfigure(0, weight=1)
        ext_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(ext_frame, text="External Communication Details",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#2b5797", anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(12, 4))

        self.v_display_name = tk.StringVar()
        self.v_ext_email    = tk.StringVar()
        self.v_password     = tk.StringVar()

        make_label(ext_frame, "Display Name", 1, 0)
        make_entry(ext_frame, 1, 0, self.v_display_name)
        make_label(ext_frame, "Email", 1, 1)
        make_entry(ext_frame, 1, 1, self.v_ext_email)

        ctk.CTkLabel(ext_frame, text="Password", font=lbl_font,
                     text_color="#2b5797", anchor="w").grid(
            row=4, column=0, sticky="w", padx=15, pady=(10, 0))
        pw_row = ctk.CTkFrame(ext_frame, fg_color="white")
        pw_row.grid(row=5, column=0, columnspan=2, sticky="w", padx=15, pady=(2, 12))
        self.pw_entry = ctk.CTkEntry(pw_row, width=340, height=32, font=entry_font,
                                     textvariable=self.v_password, show="*",
                                     fg_color="white", border_color="#ccc", text_color="#333")
        self.pw_entry.pack(side="left")
        self._pw_visible = False
        self.eye_btn = ctk.CTkButton(
            pw_row, text="👁", width=32, height=32,
            fg_color="white", hover_color="#eee", text_color="#555",
            border_width=1, border_color="#ccc", corner_radius=4,
            command=self._toggle_password
        )
        self.eye_btn.pack(side="left", padx=(4, 0))

        # Save button
        ctk.CTkButton(
            profile_frame, text="Save", width=100, height=35,
            fg_color="#2b5797", hover_color="#1a3f73",
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6, command=self._save_profile
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # ---- Settings tab ----
        settings_frame = ctk.CTkFrame(self, fg_color="#f5f7fa")

        pw_card = ctk.CTkFrame(settings_frame, fg_color="white",
                               corner_radius=8, border_width=1, border_color="#dde3ec")
        pw_card.pack(fill="x", padx=30, pady=30)

        lbl_font2 = ctk.CTkFont(size=12)
        entry_font2 = ctk.CTkFont(size=12)

        def pw_row_widget(parent, label_text, var, row_num):
            ctk.CTkLabel(parent, text=label_text, font=lbl_font2,
                         text_color="#2b5797", anchor="w").pack(
                fill="x", padx=15, pady=(12 if row_num == 0 else 6, 0))
            row_frame = ctk.CTkFrame(parent, fg_color="white")
            row_frame.pack(fill="x", padx=15, pady=(2, 0))
            entry = ctk.CTkEntry(row_frame, height=34, font=entry_font2,
                                 textvariable=var, show="*",
                                 placeholder_text=label_text,
                                 fg_color="white", border_color="#ccc", text_color="#333")
            entry.pack(side="left", fill="x", expand=True)
            visible = [False]
            def toggle(e=entry, v=visible):
                v[0] = not v[0]
                e.configure(show="" if v[0] else "*")
            eye = ctk.CTkButton(row_frame, text="👁", width=34, height=34,
                                fg_color="white", hover_color="#eee", text_color="#2b5797",
                                border_width=1, border_color="#ccc", corner_radius=4,
                                command=toggle)
            eye.pack(side="left", padx=(4, 0))
            return entry

        self.v_cur_pw  = tk.StringVar()
        self.v_new_pw  = tk.StringVar()
        self.v_conf_pw = tk.StringVar()

        pw_row_widget(pw_card, "Current Password",     self.v_cur_pw,  0)
        pw_row_widget(pw_card, "New Password",         self.v_new_pw,  1)
        pw_row_widget(pw_card, "Confirm New Password", self.v_conf_pw, 2)

        ctk.CTkButton(
            pw_card, text="Update", width=100, height=35,
            fg_color="#2b5797", hover_color="#1a3f73",
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6, command=self._update_password
        ).pack(anchor="w", padx=15, pady=(14, 16))

        # show profile tab by default
        profile_frame.pack(fill="both", expand=True)

    def _load_profile(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            cur.execute('SELECT name, city, location, email, telephone, fax, mobile, '
                        'address, display_name, ext_email, password FROM admin_profile LIMIT 1')
            row = cur.fetchone()
            conn.close()
            if row:
                self.v_name.set(row[0] or '')
                self.v_city.set(row[1] or '')
                self.v_location.set(row[2] or '')
                self.v_email.set(row[3] or '')
                self.v_tel.set(row[4] or '')
                self.v_fax.set(row[5] or '')
                self.v_mobile.set(row[6] or '')
                self.addr_box.delete('1.0', 'end')
                self.addr_box.insert('1.0', row[7] or '')
                self.v_display_name.set(row[8] or '')
                self.v_ext_email.set(row[9] or '')
                self.v_password.set(row[10] or '')
        except Exception as e:
            print(f"Error loading profile: {e}")

    def _save_profile(self):
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur = conn.cursor()
            cur.execute('''
                UPDATE admin_profile SET
                    name=?, city=?, location=?, email=?, telephone=?, fax=?,
                    mobile=?, address=?, display_name=?, ext_email=?, password=?
                WHERE id = (SELECT MIN(id) FROM admin_profile)
            ''', (
                self.v_name.get(), self.v_city.get(), self.v_location.get(),
                self.v_email.get(), self.v_tel.get(), self.v_fax.get(),
                self.v_mobile.get(), self.addr_box.get('1.0', 'end').strip(),
                self.v_display_name.get(), self.v_ext_email.get(), self.v_password.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Profile", "Profile saved successfully!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}", parent=self)

    def _toggle_password(self):
        self._pw_visible = not self._pw_visible
        self.pw_entry.configure(show="" if self._pw_visible else "*")

    def _update_password(self):
        cur  = self.v_cur_pw.get().strip()
        new  = self.v_new_pw.get().strip()
        conf = self.v_conf_pw.get().strip()

        if not cur:
            messagebox.showwarning("Validation", "Please enter your current password.", parent=self)
            return
        try:
            conn = sqlite3.connect('laundry_system.db')
            c = conn.cursor()
            c.execute('SELECT password FROM admin_profile LIMIT 1')
            row = c.fetchone()
            conn.close()
            stored = (row[0] or '') if row else ''
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}", parent=self)
            return

        if cur != stored:
            messagebox.showerror("Error", "Current password is incorrect.", parent=self)
            return
        if not new:
            messagebox.showwarning("Validation", "New password cannot be empty.", parent=self)
            return
        if new != conf:
            messagebox.showerror("Error", "New password and confirmation do not match.", parent=self)
            return

        try:
            conn = sqlite3.connect('laundry_system.db')
            c = conn.cursor()
            c.execute('UPDATE admin_profile SET password=? WHERE id=(SELECT MIN(id) FROM admin_profile)', (new,))
            conn.commit()
            conn.close()
            self.v_password.set(new)   # keep Profile tab in sync
            self.v_cur_pw.set('')
            self.v_new_pw.set('')
            self.v_conf_pw.set('')
            messagebox.showinfo("Success", "Password updated successfully!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}", parent=self)

    def _change_avatar(self):
        messagebox.showinfo("Avatar", "Profile picture upload coming soon!", parent=self)


class ReportsWindow(ctk.CTkToplevel):
    """نافذة التقارير الكاملة"""

    REPORT_DEFS = {
        "Sales": [
            ("Sales Invoice", True),
        ],
        "Job-Services": [
            ("To be Delivered", False),
            ("Order-Details", False),
            ("Order-Item Summery", False),
            ("Order-Item Detailed", False),
            ("Job/Service Statement - All", False),
            ("Job/Service Statement - Unpaid", False),
            ("Job/service Statement Unpaid- As Invoice", False),
            ("Job/Service Statement-Paid", False),
            ("Order-Details-Deleted", False),
            ("Order-Item Detailed-Deleted", False),
            ("Pending Orders (Not Delivered)", False),
            ("Paid Invoice Details", False),
            ("All Customers Outstanding", False),
            ("Pending Orders (Not Delivered & Not Paid)", False),
            ("Service Product List & Units", False),
            ("Service Product List", False),
            ("Job Commission Report", False),
            ("Order Item Details Daywise", False),
        ],
        "Payment Received": [
            ("Payment Received On Sales & Order (Advance)", False),
            ("Payment Received Day/Month Wise", False),
            ("Unpaid Paid Sales (Payment of unpaid invoices)", False),
        ],
        "Accounts": [
            ("Ledger Report", False),
            ("Expense Report", False),
            ("Cash A/c Flow Report", False),
            ("Cash & Bank Flow Report", False),
        ],
        "TAX": [
            ("VAT Report", False),
        ],
    }

    CAT_ICONS = {
        "Sales": "📋",
        "Job-Services": "👕",
        "Payment Received": "💳",
        "Accounts": "🏦",
        "TAX": "📋",
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reports")
        self.geometry("1200x700")
        self.state("zoomed")
        self.lift()
        self.focus_force()
        self._active_tab = "All Reports"
        self._search_var = tk.StringVar()
        self._build()

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="white", height=54)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="Reports",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#333").pack(side="left", padx=24, pady=10)

        # Search bar (right)
        srch_frame = ctk.CTkFrame(top, fg_color="white")
        srch_frame.pack(side="right", padx=20, pady=10)
        srch_entry = ctk.CTkEntry(srch_frame, textvariable=self._search_var,
                                  placeholder_text="Search Reports",
                                  width=220, height=32)
        srch_entry.pack(side="left")
        srch_entry.bind("<Return>", lambda e: self._render_all(self._search_var.get()))
        ctk.CTkButton(srch_frame, text="🔍", width=34, height=32,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", corner_radius=4,
                      command=lambda: self._render_all(self._search_var.get())).pack(side="left", padx=(4, 0))

        sep = tk.Frame(self, bg="#dde3ec", height=1)
        sep.pack(fill="x")

        # Tab bar
        tab_bar = ctk.CTkFrame(self, fg_color="#f0f2f5", height=46)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self._tab_btns = {}
        tab_defs = [("⭐  Favourites", "Favourites"),
                    ("🕐  Recents",    "Recents"),
                    ("📋  All Reports","All Reports")]
        for label, key in tab_defs:
            is_active = key == "All Reports"
            btn = ctk.CTkButton(
                tab_bar, text=label, width=160, height=46, corner_radius=0,
                fg_color="#2b5797" if is_active else "#f0f2f5",
                text_color="white" if is_active else "#555",
                hover_color="#1a3f73" if is_active else "#dde3ec",
                font=ctk.CTkFont(size=12),
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(side="left")
            self._tab_btns[key] = btn

        sep2 = tk.Frame(self, bg="#dde3ec", height=1)
        sep2.pack(fill="x")

        # Content
        self._content = ctk.CTkScrollableFrame(self, fg_color="white")
        self._content.pack(fill="both", expand=True)
        self._render_all("")

    def _switch_tab(self, tab):
        self._active_tab = tab
        for k, btn in self._tab_btns.items():
            is_a = k == tab
            btn.configure(fg_color="#2b5797" if is_a else "#f0f2f5",
                          text_color="white" if is_a else "#555")
        if tab == "All Reports":
            self._render_all(self._search_var.get())
        elif tab == "Favourites":
            favs = {cat: [(n, f) for n, f in items if f]
                    for cat, items in self.REPORT_DEFS.items()}
            favs = {c: i for c, i in favs.items() if i}
            self._render_all("", data=favs)
        else:
            self._render_all("", data={})

    def _render_all(self, search="", data=None):
        for w in self._content.winfo_children():
            w.destroy()

        source = data if data is not None else self.REPORT_DEFS

        outer = ctk.CTkFrame(self._content, fg_color="white")
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        col_count = len(source)
        for i in range(col_count):
            outer.columnconfigure(i, weight=1)

        for col_idx, (category, items) in enumerate(source.items()):
            col_frame = ctk.CTkFrame(outer, fg_color="white")
            col_frame.grid(row=0, column=col_idx, sticky="n", padx=10, pady=0)

            # Category header
            icon = self.CAT_ICONS.get(category, "📋")
            ctk.CTkLabel(col_frame,
                         text=f"{icon}  {category}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#2b5797").pack(anchor="w", pady=(0, 10))

            for name, is_fav in items:
                if search and search.lower() not in name.lower():
                    continue
                item_row = ctk.CTkFrame(col_frame, fg_color="white")
                item_row.pack(fill="x", pady=1)
                star_color = "#f1c40f" if is_fav else "#ccc"
                ctk.CTkLabel(item_row, text="★",
                             font=ctk.CTkFont(size=11), text_color=star_color,
                             width=18).pack(side="left")
                ctk.CTkButton(item_row, text=name,
                              font=ctk.CTkFont(size=11),
                              text_color="#2b5797",
                              fg_color="white", hover_color="#e8eef7",
                              anchor="w", height=24,
                              command=lambda n=name, c=category: self._open_report(n, c)
                              ).pack(side="left", fill="x", expand=True)

    def _open_report(self, name, category):
        ReportViewDialog(self, name, category)


class ReportViewDialog(ctk.CTkToplevel):
    """عرض تقرير واحد مع فلترة التاريخ"""

    def __init__(self, parent, report_name, category):
        super().__init__(parent)
        self.title(report_name)
        self.geometry("1050x620")
        self.lift()
        self.focus_force()
        self._report_name = report_name
        self._category = category
        self._build()
        self.after(100, self._load)

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"📋  {self._report_name}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").pack(side="left", padx=20, pady=10)
        ctk.CTkButton(hdr, text="✕", width=32, height=30,
                      fg_color="#1a3f73", hover_color="#c0392b",
                      text_color="white", corner_radius=4,
                      command=self.destroy).pack(side="right", padx=10)

        # Filter bar
        fbar = ctk.CTkFrame(self, fg_color="#f0f2f5", height=44)
        fbar.pack(fill="x")
        fbar.pack_propagate(False)
        lf = ctk.CTkFont(size=11)
        ctk.CTkLabel(fbar, text="From:", font=lf, text_color="#555").pack(side="left", padx=(16, 4))
        self._from_e = ctk.CTkEntry(fbar, width=110, height=28, placeholder_text="DD-MM-YYYY")
        self._from_e.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(fbar, text="To:", font=lf, text_color="#555").pack(side="left", padx=(0, 4))
        self._to_e = ctk.CTkEntry(fbar, width=110, height=28, placeholder_text="DD-MM-YYYY")
        self._to_e.pack(side="left", padx=(0, 12))
        ctk.CTkButton(fbar, text="Generate", width=84, height=30,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=lf,
                      command=self._load).pack(side="left")

        self._frame = ctk.CTkFrame(self, fg_color="white")
        self._frame.pack(fill="both", expand=True, padx=8, pady=8)

    def _load(self):
        for w in self._frame.winfo_children():
            w.destroy()

        now = datetime.now()
        year_s = now.replace(month=1, day=1).strftime("%d-%m-%Y")
        today  = now.strftime("%d-%m-%Y")
        frm = self._from_e.get().strip() or year_s
        to  = self._to_e.get().strip() or today

        try:
            conn = sqlite3.connect('laundry_system.db')
            cur  = conn.cursor()
            name = self._report_name

            if name == "Sales Invoice":
                cols = ("Invoice #", "Date", "Customer", "Service", "Amount (AED)", "Status")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'),
                           i.service_type, i.subtotal, i.status
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date >= ? AND i.date <= ? ORDER BY i.id DESC
                """, (frm, to))

            elif name in ("To be Delivered", "Pending Orders (Not Delivered)",
                          "Pending Orders (Not Delivered & Not Paid)"):
                cols = ("Invoice #", "Date", "Customer", "Delivery Date", "Amount (AED)", "Status")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'),
                           i.delivery_date, i.subtotal, i.status
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.status != 'Delivered' AND i.date >= ? AND i.date <= ?
                    ORDER BY i.delivery_date
                """, (frm, to))

            elif name in ("Order-Details", "Order-Details-Deleted",
                          "Job/Service Statement - All", "Job/Service Statement-Paid",
                          "Job/Service Statement - Unpaid",
                          "Job/service Statement Unpaid- As Invoice",
                          "Paid Invoice Details", "Order Item Details Daywise"):
                cols = ("Invoice #", "Date", "Customer", "Service", "Amount (AED)", "Status")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'),
                           i.service_type, i.subtotal, i.status
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date >= ? AND i.date <= ? ORDER BY i.id DESC
                """, (frm, to))

            elif name in ("Order-Item Summery",):
                cols = ("Product", "Quantity", "Total Amount (AED)")
                cur.execute("""
                    SELECT ii.product_name, SUM(ii.quantity), SUM(ii.total)
                    FROM invoice_items ii JOIN invoices i ON ii.invoice_id=i.id
                    WHERE i.date >= ? AND i.date <= ?
                    GROUP BY ii.product_name ORDER BY SUM(ii.total) DESC
                """, (frm, to))

            elif name in ("Order-Item Detailed", "Order-Item Detailed-Deleted"):
                cols = ("Invoice #", "Date", "Product", "Qty", "Price (AED)", "Total (AED)")
                cur.execute("""
                    SELECT i.invoice_number, i.date, ii.product_name,
                           ii.quantity, ii.price, ii.total
                    FROM invoice_items ii JOIN invoices i ON ii.invoice_id=i.id
                    WHERE i.date >= ? AND i.date <= ? ORDER BY i.date DESC
                """, (frm, to))

            elif name == "All Customers Outstanding":
                cols = ("Customer", "Phone", "Invoices", "Total Outstanding (AED)")
                cur.execute("""
                    SELECT COALESCE(c.name,'Cash Customer'), COALESCE(c.phone,''),
                           COUNT(i.id), SUM(i.subtotal)
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date >= ? AND i.date <= ?
                    GROUP BY i.customer_id ORDER BY SUM(i.subtotal) DESC
                """, (frm, to))

            elif name in ("Service Product List & Units", "Service Product List"):
                cols = ("ID", "Product Name", "Category", "W&P Price", "P Only Price")
                cur.execute("SELECT id, name, category, price_wash_press, price_press_only FROM products ORDER BY name")

            elif name in ("Payment Received On Sales & Order (Advance)",
                          "Payment Received Day/Month Wise",
                          "Unpaid Paid Sales (Payment of unpaid invoices)"):
                cols = ("Invoice #", "Date", "Customer", "Amount (AED)", "Status")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'), i.subtotal, i.status
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date >= ? AND i.date <= ? ORDER BY i.date DESC
                """, (frm, to))

            elif name == "Ledger Report":
                cols = ("Date", "Invoice #", "Customer", "Debit (AED)", "Credit (AED)", "Balance (AED)")
                cur.execute("""
                    SELECT i.date, i.invoice_number,
                           COALESCE(c.name,'Cash Customer'), i.subtotal, 0.0, i.subtotal
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date >= ? AND i.date <= ? ORDER BY i.date
                """, (frm, to))

            elif name == "Expense Report":
                cols = ("Date", "Description", "Category", "Amount (AED)")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS expenses
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT, description TEXT, category TEXT, amount REAL)
                """)
                cur.execute("SELECT date, description, category, amount FROM expenses WHERE date>=? AND date<=? ORDER BY date DESC", (frm, to))

            elif name in ("Cash A/c Flow Report", "Cash & Bank Flow Report"):
                cols = ("Date", "Invoice #", "Customer", "Amount (AED)")
                cur.execute("""
                    SELECT i.date, i.invoice_number,
                           COALESCE(c.name,'Cash Customer'), i.subtotal
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.customer_type='Cash Customer' AND i.date>=? AND i.date<=?
                    ORDER BY i.date DESC
                """, (frm, to))

            elif name == "VAT Report":
                cols = ("Invoice #", "Date", "Customer", "Net (AED)", "VAT 5% (AED)", "Gross (AED)")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'),
                           i.subtotal,
                           ROUND(i.subtotal*0.05, 2),
                           ROUND(i.subtotal*1.05, 2)
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date>=? AND i.date<=? ORDER BY i.date DESC
                """, (frm, to))

            elif name == "Job Commission Report":
                cols = ("Sales Man", "Invoice Count", "Total Sales (AED)")
                cur.execute("""
                    SELECT COALESCE(sales_man,'Unknown'), COUNT(*), SUM(subtotal)
                    FROM invoices WHERE date>=? AND date<=?
                    GROUP BY sales_man ORDER BY SUM(subtotal) DESC
                """, (frm, to))

            else:
                cols = ("Invoice #", "Date", "Customer", "Amount (AED)", "Status")
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'), i.subtotal, i.status
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date>=? AND i.date<=? ORDER BY i.id DESC
                """, (frm, to))

            rows = cur.fetchall()
            conn.close()

        except Exception as e:
            ctk.CTkLabel(self._frame, text=f"Error loading report: {e}",
                         text_color="#e74c3c", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        # Build treeview
        tree_frame = ctk.CTkFrame(self._frame, fg_color="white")
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        col_w = max(100, min(180, 900 // len(cols)))
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=col_w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        tree.tag_configure("even", background="#f7f9fc")
        for idx, row in enumerate(rows):
            display = []
            for v in row:
                if isinstance(v, float):
                    display.append(f"{v:,.2f}")
                else:
                    display.append(str(v) if v is not None else "")
            tree.insert("", "end", values=display, tags=("even" if idx % 2 == 0 else "",))

        ctk.CTkLabel(self._frame,
                     text=f"Total Records: {len(rows)}",
                     font=ctk.CTkFont(size=11), text_color="#555").pack(
            side="bottom", anchor="e", padx=10, pady=4)


class AccountsWindow(ctk.CTkToplevel):
    """نافذة الحسابات مع القائمة الجانبية"""

    ITEMS = [
        ("Chart Of Accounts", "📊"),
        ("Accounts",          "📒"),
        ("Opening Balance",   "💰"),
        ("Journal Entry",     "📝"),
        ("Expenses",          "💸"),
        ("Receipt From POS",  "🧾"),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Accounts")
        self.geometry("1150x680")
        self.state("zoomed")
        self.lift()
        self.focus_force()
        self._build()
        self._select("Chart Of Accounts")

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="white", height=50)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="🏦  Accounts",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#333").pack(side="left", padx=20, pady=10)

        tk.Frame(self, bg="#dde3ec", height=1).pack(fill="x")

        main = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(main, fg_color="#1e2a3a", width=210)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="🏦  Accounts",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(pady=(18, 14), padx=14, anchor="w")

        self._acc_btns = {}
        for name, icon in self.ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=f"   {icon}   {name}", anchor="w",
                width=210, height=40, corner_radius=0,
                fg_color="#1e2a3a", hover_color="#2b5797",
                text_color="white", font=ctk.CTkFont(size=12),
                command=lambda n=name: self._select(n)
            )
            btn.pack(fill="x")
            self._acc_btns[name] = btn

        self._content = ctk.CTkFrame(main, fg_color="#f0f2f5")
        self._content.grid(row=0, column=1, sticky="nsew")

    def _select(self, name):
        for n, btn in self._acc_btns.items():
            btn.configure(fg_color="#2b5797" if n == name else "#1e2a3a")
        for w in self._content.winfo_children():
            w.destroy()
        # Header
        hdr = ctk.CTkFrame(self._content, fg_color="white", height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        icon = {n: i for n, i in self.ITEMS}.get(name, "")
        ctk.CTkLabel(hdr, text=f"{icon}  {name}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#2b5797").pack(side="left", padx=20, pady=10)

        methods = {
            "Chart Of Accounts": self._chart_of_accounts,
            "Accounts":          self._accounts_list,
            "Opening Balance":   self._opening_balance,
            "Journal Entry":     self._journal_entry,
            "Expenses":          self._expenses,
            "Receipt From POS":  self._receipt_from_pos,
        }
        if name in methods:
            methods[name]()

    # ---- Chart of Accounts ----
    def _chart_of_accounts(self):
        frame = ctk.CTkScrollableFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        groups = [
            ("Assets",     "#2ecc71", ["Cash", "Bank Account", "Accounts Receivable", "Inventory"]),
            ("Liabilities","#e74c3c", ["Accounts Payable", "Loans Payable"]),
            ("Equity",     "#3498db", ["Owner's Equity", "Retained Earnings"]),
            ("Revenue",    "#f39c12", ["Sales Revenue", "Service Revenue"]),
            ("Expenses",   "#9b59b6", ["Cost of Goods Sold", "Operating Expenses", "Salaries & Wages"]),
        ]
        for group, color, accounts in groups:
            gh = ctk.CTkFrame(frame, fg_color=color, corner_radius=6, height=38)
            gh.pack(fill="x", pady=(10, 2))
            gh.pack_propagate(False)
            ctk.CTkLabel(gh, text=f"  {group}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").place(x=14, rely=0.5, anchor="w")
            for acc in accounts:
                af = ctk.CTkFrame(frame, fg_color="#f7f9fc", corner_radius=4, height=34)
                af.pack(fill="x", pady=1, padx=12)
                af.pack_propagate(False)
                ctk.CTkFrame(af, fg_color=color, width=4,
                             corner_radius=2).pack(side="left", fill="y", padx=(8, 10))
                ctk.CTkLabel(af, text=acc, font=ctk.CTkFont(size=11),
                             text_color="#333").pack(side="left", pady=6)

    # ---- Accounts List ----
    def _accounts_list(self):
        frame = ctk.CTkFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tb = ctk.CTkFrame(frame, fg_color="white")
        tb.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(tb, text="+ New Account", width=130, height=32,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=11),
                      command=lambda: messagebox.showinfo("Accounts","New account form coming soon!", parent=self)
                      ).pack(side="left", padx=4)

        cols = ("Account Name", "Type", "Opening Balance (AED)", "Current Balance (AED)")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=230)
        sample = [
            ("Cash",                   "Asset",   "0.00", "0.00"),
            ("Bank Account",           "Asset",   "0.00", "0.00"),
            ("Accounts Receivable",    "Asset",   "0.00", "0.00"),
            ("Sales Revenue",          "Revenue", "0.00", "0.00"),
            ("Operating Expenses",     "Expense", "0.00", "0.00"),
        ]
        for r in sample:
            tree.insert("", "end", values=r)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    # ---- Opening Balance ----
    def _opening_balance(self):
        frame = ctk.CTkScrollableFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(frame, text="Set Opening Balances for Accounts",
                     font=ctk.CTkFont(size=12), text_color="#555").pack(anchor="w", pady=(4, 14))
        accs = ["Cash", "Bank Account", "Accounts Receivable",
                "Inventory", "Accounts Payable", "Owner's Equity"]
        self._ob_entries = {}
        for acc in accs:
            row = ctk.CTkFrame(frame, fg_color="#f7f9fc", corner_radius=6, height=46)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=acc, font=ctk.CTkFont(size=11),
                         text_color="#333", width=200, anchor="w").place(x=14, rely=0.5, anchor="w")
            e = ctk.CTkEntry(row, width=160, height=30, placeholder_text="0.00")
            e.place(x=220, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text="AED", font=ctk.CTkFont(size=11),
                         text_color="#888").place(x=394, rely=0.5, anchor="w")
            self._ob_entries[acc] = e
        ctk.CTkButton(frame, text="Save Opening Balances", width=190, height=36,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=12),
                      command=lambda: messagebox.showinfo("Saved", "Opening balances saved!", parent=self)
                      ).pack(anchor="w", pady=18)

    # ---- Journal Entry ----
    def _journal_entry(self):
        frame = ctk.CTkFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = ctk.CTkFrame(frame, fg_color="#f7f9fc", corner_radius=8,
                            border_width=1, border_color="#dde3ec")
        card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(card, text="New Journal Entry",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#2b5797").pack(anchor="w", padx=16, pady=(12, 6))

        sf = ctk.CTkFont(size=11)
        accs = ["Cash", "Bank Account", "Accounts Receivable",
                "Sales Revenue", "Expenses", "Owner's Equity"]

        row1 = ctk.CTkFrame(card, fg_color="#f7f9fc")
        row1.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row1, text="Date:", font=sf, text_color="#555", width=80).pack(side="left")
        de = ctk.CTkEntry(row1, width=120, height=30)
        de.insert(0, datetime.now().strftime("%d-%m-%Y"))
        de.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(row1, text="Description:", font=sf, text_color="#555", width=90).pack(side="left")
        desc_e = ctk.CTkEntry(row1, width=300, height=30)
        desc_e.pack(side="left")

        row2 = ctk.CTkFrame(card, fg_color="#f7f9fc")
        row2.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row2, text="Debit Account:", font=sf, text_color="#555", width=110).pack(side="left")
        deb_acc = ctk.CTkComboBox(row2, values=accs, width=200)
        deb_acc.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(row2, text="Amount (AED):", font=sf, text_color="#555").pack(side="left")
        deb_amt = ctk.CTkEntry(row2, width=120, height=30, placeholder_text="0.00")
        deb_amt.pack(side="left")

        row3 = ctk.CTkFrame(card, fg_color="#f7f9fc")
        row3.pack(fill="x", padx=16, pady=(4, 12))
        ctk.CTkLabel(row3, text="Credit Account:", font=sf, text_color="#555", width=110).pack(side="left")
        crd_acc = ctk.CTkComboBox(row3, values=accs, width=200)
        crd_acc.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(row3, text="Amount (AED):", font=sf, text_color="#555").pack(side="left")
        crd_amt = ctk.CTkEntry(row3, width=120, height=30, placeholder_text="0.00")
        crd_amt.pack(side="left")

        def post():
            try:
                d = float(deb_amt.get())
                c = float(crd_amt.get())
                if abs(d - c) > 0.01:
                    messagebox.showerror("Error", "Debit and Credit amounts must be equal!", parent=self)
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount.", parent=self)
                return
            conn = sqlite3.connect('laundry_system.db')
            cur  = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, description TEXT,
                debit_account TEXT, credit_account TEXT, amount REAL)""")
            cur.execute("INSERT INTO journal_entries VALUES (NULL,?,?,?,?,?)",
                        (de.get(), desc_e.get(), deb_acc.get(), crd_acc.get(), d))
            conn.commit(); conn.close()
            messagebox.showinfo("Posted", "Journal entry posted!", parent=self)
            de.delete(0, "end"); de.insert(0, datetime.now().strftime("%d-%m-%Y"))
            desc_e.delete(0, "end")
            deb_amt.delete(0, "end"); crd_amt.delete(0, "end")
            self._load_journal(jtree)

        ctk.CTkButton(card, text="Post Entry", width=110, height=32,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", command=post).pack(anchor="w", padx=16, pady=(0, 12))

        cols = ("Date", "Description", "Debit Account", "Credit Account", "Amount (AED)")
        jtree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            jtree.heading(c, text=c)
            jtree.column(c, width=180)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=jtree.yview)
        jtree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        jtree.pack(fill="both", expand=True)
        self._load_journal(jtree)

    def _load_journal(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur  = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, description TEXT,
                debit_account TEXT, credit_account TEXT, amount REAL)""")
            cur.execute("SELECT date, description, debit_account, credit_account, amount FROM journal_entries ORDER BY id DESC")
            for row in cur.fetchall():
                tree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{row[4]:,.2f}"))
            conn.close()
        except Exception:
            pass

    # ---- Expenses ----
    def _expenses(self):
        frame = ctk.CTkFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tb = ctk.CTkFrame(frame, fg_color="white")
        tb.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(tb, text="+ Add Expense", width=130, height=32,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=11),
                      command=lambda: ExpenseDialog(self, lambda: self._reload_expenses(etree))
                      ).pack(side="left", padx=4)
        ctk.CTkButton(tb, text="Refresh", width=80, height=32,
                      fg_color="#6c757d", hover_color="#555",
                      text_color="white", font=ctk.CTkFont(size=11),
                      command=lambda: self._reload_expenses(etree)
                      ).pack(side="left", padx=4)

        cols = ("Date", "Description", "Category", "Amount (AED)")
        etree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            etree.heading(c, text=c)
            etree.column(c, width=240)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=etree.yview)
        etree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        etree.pack(fill="both", expand=True)
        self._reload_expenses(etree)

    def _reload_expenses(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur  = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, description TEXT, category TEXT, amount REAL)""")
            cur.execute("SELECT date, description, category, amount FROM expenses ORDER BY date DESC")
            for row in cur.fetchall():
                tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:,.2f}"))
            conn.close()
        except Exception:
            pass

    # ---- Receipt From POS ----
    def _receipt_from_pos(self):
        frame = ctk.CTkFrame(self._content, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tb = ctk.CTkFrame(frame, fg_color="white")
        tb.pack(fill="x", pady=(0, 8))
        sf = ctk.CTkFont(size=11)
        ctk.CTkLabel(tb, text="From:", font=sf, text_color="#555").pack(side="left", padx=(0, 4))
        from_e = ctk.CTkEntry(tb, width=120, height=30, placeholder_text="DD-MM-YYYY")
        from_e.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(tb, text="To:", font=sf, text_color="#555").pack(side="left", padx=(0, 4))
        to_e = ctk.CTkEntry(tb, width=120, height=30, placeholder_text="DD-MM-YYYY")
        to_e.pack(side="left", padx=(0, 8))

        cols = ("Invoice #", "Date", "Customer", "Payment Type", "Amount (AED)")
        rtree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            rtree.heading(c, text=c)
            rtree.column(c, width=190)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=rtree.yview)
        rtree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        rtree.pack(fill="both", expand=True)

        def load():
            for i in rtree.get_children():
                rtree.delete(i)
            now = datetime.now()
            frm = from_e.get().strip() or now.replace(month=1, day=1).strftime("%d-%m-%Y")
            to  = to_e.get().strip() or now.strftime("%d-%m-%Y")
            try:
                conn = sqlite3.connect('laundry_system.db')
                cur  = conn.cursor()
                cur.execute("""
                    SELECT i.invoice_number, i.date,
                           COALESCE(c.name,'Cash Customer'),
                           i.customer_type, i.subtotal
                    FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
                    WHERE i.date>=? AND i.date<=? ORDER BY i.date DESC
                """, (frm, to))
                for row in cur.fetchall():
                    rtree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{row[4]:,.2f}"))
                conn.close()
            except Exception as e:
                print(e)

        ctk.CTkButton(tb, text="Search", width=80, height=30,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", command=load).pack(side="left")
        load()


class ExpenseDialog(ctk.CTkToplevel):
    """إضافة مصروف جديد"""

    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.title("Add Expense")
        self.geometry("420x320")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()
        self._callback = callback
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="#2b5797", height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Add Expense",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", padx=16, pady=8)

        form = ctk.CTkFrame(self, fg_color="white")
        form.pack(fill="both", expand=True, padx=20, pady=14)
        lf = ctk.CTkFont(size=11)

        ctk.CTkLabel(form, text="Date (DD-MM-YYYY):", font=lf, text_color="#555").pack(anchor="w", pady=(4, 0))
        self._v_date = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        ctk.CTkEntry(form, textvariable=self._v_date, height=30).pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Description:", font=lf, text_color="#555").pack(anchor="w")
        self._v_desc = tk.StringVar()
        ctk.CTkEntry(form, textvariable=self._v_desc, height=30).pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Category:", font=lf, text_color="#555").pack(anchor="w")
        self._v_cat = tk.StringVar(value="General")
        ctk.CTkComboBox(form, variable=self._v_cat, height=30,
                        values=["General", "Utilities", "Rent", "Salaries",
                                "Supplies", "Maintenance", "Other"]).pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Amount (AED):", font=lf, text_color="#555").pack(anchor="w")
        self._v_amount = tk.StringVar()
        ctk.CTkEntry(form, textvariable=self._v_amount, height=30).pack(fill="x", pady=(2, 8))

        br = ctk.CTkFrame(self, fg_color="white")
        br.pack(fill="x", padx=20, pady=(0, 14))
        ctk.CTkButton(br, text="Save", width=100, height=34,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", command=self._save).pack(side="right", padx=4)
        ctk.CTkButton(br, text="Cancel", width=100, height=34,
                      fg_color="gray", hover_color="#555",
                      text_color="white", command=self.destroy).pack(side="right")

    def _save(self):
        desc = self._v_desc.get().strip()
        if not desc:
            messagebox.showwarning("Validation", "Description is required.", parent=self)
            return
        try:
            amount = float(self._v_amount.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.", parent=self)
            return
        try:
            conn = sqlite3.connect('laundry_system.db')
            cur  = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, description TEXT, category TEXT, amount REAL)""")
            cur.execute("INSERT INTO expenses (date, description, category, amount) VALUES (?,?,?,?)",
                        (self._v_date.get(), desc, self._v_cat.get(), amount))
            conn.commit(); conn.close()
            if self._callback:
                self._callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class LoginWindow(ctk.CTk):
    """Login window shown before the main application."""

    BG      = "#f0f4f8"
    ACCENT  = "#0e9e8e"   # teal — matches AP SOFT logo colour
    DARK    = "#1e2a3a"

    def __init__(self):
        super().__init__()
        self.title("Login – AP SOFT | WASH HUB LAUNDRY")
        self.geometry("440x580")
        self.resizable(False, False)
        self.configure(fg_color=self.BG)

        # Centre on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - 440) // 2
        y  = (sh - 580) // 2
        self.geometry(f"440x580+{x}+{y}")

        # Set window / taskbar icon
        _logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(_logo_path):
            try:
                _ico = tk.PhotoImage(file=_logo_path)
                self.iconphoto(True, _ico)
                self._icon_ref = _ico   # prevent GC
            except Exception:
                pass

        self._attempts = 0
        self._build()

    def _build(self):
        # ── Logo area ──────────────────────────────────────────────────────
        logo_area = ctk.CTkFrame(self, fg_color=self.DARK, height=160, corner_radius=0)
        logo_area.pack(fill="x")
        logo_area.pack_propagate(False)

        # Load logo.png; fall back to drawn icon if unavailable
        _logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(_logo_path):
            try:
                _pil_img = Image.open(_logo_path).convert("RGBA")
                _pil_img.thumbnail((90, 90), Image.LANCZOS)
                self._login_logo_img = ImageTk.PhotoImage(_pil_img)
                ctk.CTkLabel(logo_area, image=self._login_logo_img, text="").place(
                    relx=0.5, rely=0.45, anchor="center")
            except Exception:
                self._login_logo_img = None
        else:
            self._login_logo_img = None

        if not self._login_logo_img:
            # Fallback: drawn teal box
            icon_box = ctk.CTkFrame(logo_area, fg_color=self.ACCENT,
                                    width=68, height=68, corner_radius=12)
            icon_box.place(relx=0.5, rely=0.42, anchor="center")
            icon_box.pack_propagate(False)
            ctk.CTkLabel(icon_box, text="AP",
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color="white").place(relx=0.5, rely=0.38, anchor="center")
            ctk.CTkLabel(icon_box, text="SOFT",
                         font=ctk.CTkFont(size=9),
                         text_color="white").place(relx=0.5, rely=0.78, anchor="center")

        ctk.CTkLabel(logo_area, text="WASH HUB LAUNDRY",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#aac").place(relx=0.5, rely=0.92, anchor="center")

        # ── Card ────────────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=12,
                            border_width=1, border_color="#dde3ec")
        card.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(card, text="Sign In to your account",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.DARK).pack(pady=(20, 4))
        ctk.CTkLabel(card, text="Enter your credentials to continue",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(pady=(0, 18))

        # Username
        ctk.CTkLabel(card, text="Username",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#444", anchor="w").pack(fill="x", padx=24)
        self._user_entry = ctk.CTkEntry(
            card, placeholder_text="admin",
            width=340, height=38,
            font=ctk.CTkFont(size=13),
            border_color=self.ACCENT, fg_color="white",
            text_color=self.DARK
        )
        self._user_entry.pack(pady=(4, 12), padx=24)
        self._user_entry.insert(0, "admin")

        # Password
        ctk.CTkLabel(card, text="Password",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#444", anchor="w").pack(fill="x", padx=24)
        pwd_row = ctk.CTkFrame(card, fg_color="transparent")
        pwd_row.pack(fill="x", padx=24, pady=(4, 4))
        self._show_pwd = tk.BooleanVar(value=False)
        self._pwd_entry = ctk.CTkEntry(
            pwd_row, placeholder_text="••••",
            height=38, show="•",
            font=ctk.CTkFont(size=14),
            border_color=self.ACCENT, fg_color="white",
            text_color=self.DARK
        )
        self._pwd_entry.pack(side="left", fill="x", expand=True)
        self._pwd_entry.insert(0, "1234")
        eye_btn = ctk.CTkButton(
            pwd_row, text="👁", width=38, height=38,
            fg_color=self.ACCENT, hover_color="#0c8070",
            text_color="white", corner_radius=6,
            command=self._toggle_password
        )
        eye_btn.pack(side="left", padx=(6, 0))

        # Error label (hidden until needed)
        self._err_lbl = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(size=11),
            text_color="#e74c3c"
        )
        self._err_lbl.pack(pady=(4, 0))

        # Login button
        self._login_btn = ctk.CTkButton(
            card, text="LOGIN",
            width=340, height=42,
            fg_color=self.ACCENT, hover_color="#0c8070",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self._do_login
        )
        self._login_btn.pack(pady=(6, 22), padx=24)

        # ── Footer ───────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="© 2026 AP SOFT – All rights reserved",
                     font=ctk.CTkFont(size=10), text_color="#aaa").pack(pady=(0, 10))

        # Keyboard bindings
        self._pwd_entry.bind("<Return>", lambda e: self._do_login())
        self._user_entry.bind("<Return>", lambda e: self._pwd_entry.focus())

    def _toggle_password(self):
        if self._show_pwd.get():
            self._pwd_entry.configure(show="•")
            self._show_pwd.set(False)
        else:
            self._pwd_entry.configure(show="")
            self._show_pwd.set(True)

    def _do_login(self):
        username = self._user_entry.get().strip()
        password = self._pwd_entry.get().strip()

        if username == "admin" and password == "1234":
            self.destroy()
            app = LaundrySystem()
            app.protocol("WM_DELETE_WINDOW", app.on_closing)
            app.mainloop()
        else:
            self._attempts += 1
            self._err_lbl.configure(
                text=f"Invalid username or password. (Attempt {self._attempts})"
            )
            # Shake effect
            self._shake()

    def _shake(self):
        x0 = self.winfo_x()
        y0 = self.winfo_y()
        for i, dx in enumerate([8, -8, 6, -6, 4, -4, 0]):
            self.after(i * 40, lambda d=dx: self.geometry(
                f"440x560+{x0 + d}+{y0}"))


if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
