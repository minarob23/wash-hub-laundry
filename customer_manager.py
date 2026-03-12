"""
نوافذ مساعدة - إدارة العملاء
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from database import DatabaseManager
from models import Customer


class CustomerManagementWindow(ctk.CTkToplevel):
    """نافذة إدارة العملاء"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        
        self.db = db
        self.selected_customer = None
        
        self.title("إدارة العملاء")
        self.geometry("900x600")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.focus_force()
        
        self.create_widgets()
        self.load_customers()
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # شريط البحث
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="البحث:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="البحث بالاسم أو رقم الهاتف")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_customers)
        
        ctk.CTkButton(search_frame, text="عميل جديد", command=self.add_customer).pack(side="right", padx=5)
        
        # جدول العملاء
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # إنشاء Treeview
        columns = ("ID", "Phone", "Name", "Address", "TRN/VAT")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # تعريف الأعمدة
        self.tree.heading("ID", text="الرقم")
        self.tree.heading("Phone", text="الهاتف")
        self.tree.heading("Name", text="الاسم")
        self.tree.heading("Address", text="العنوان")
        self.tree.heading("TRN/VAT", text="TRN/VAT")
        
        self.tree.column("ID", width=50)
        self.tree.column("Phone", width=120)
        self.tree.column("Name", width=200)
        self.tree.column("Address", width=300)
        self.tree.column("TRN/VAT", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(buttons_frame, text="تعديل", command=self.edit_customer, width=100).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="حذف", command=self.delete_customer, fg_color="red", width=100).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="اختيار", command=self.select_customer, width=100).pack(side="right", padx=5)
    
    def load_customers(self):
        """تحميل العملاء"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # تحميل العملاء
        customers = self.db.get_all_customers()
        for customer in customers:
            self.tree.insert('', 'end', values=(
                customer.id,
                customer.phone,
                customer.name,
                customer.address,
                customer.trn_vat
            ))
    
    def search_customers(self, event=None):
        """البحث في العملاء"""
        search_text = self.search_entry.get().lower()
        
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # تحميل العملاء المطابقة
        customers = self.db.get_all_customers()
        for customer in customers:
            if (search_text in customer.name.lower() or 
                search_text in customer.phone.lower()):
                self.tree.insert('', 'end', values=(
                    customer.id,
                    customer.phone,
                    customer.name,
                    customer.address,
                    customer.trn_vat
                ))
    
    def add_customer(self):
        """إضافة عميل جديد"""
        CustomerEditDialog(self, self.db, None, self.load_customers)
    
    def edit_customer(self):
        """تعديل عميل"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار عميل للتعديل")
            return
        
        item = self.tree.item(selected[0])
        customer_id = item['values'][0]
        
        # الحصول على بيانات العميل
        customers = self.db.get_all_customers()
        customer = next((c for c in customers if c.id == customer_id), None)
        
        if customer:
            CustomerEditDialog(self, self.db, customer, self.load_customers)
    
    def delete_customer(self):
        """حذف عميل"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار عميل للحذف")
            return
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا العميل؟"):
            # TODO: إضافة وظيفة الحذف
            messagebox.showinfo("معلومات", "سيتم إضافة هذه الميزة قريباً")
    
    def select_customer(self):
        """اختيار عميل"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار عميل")
            return
        
        item = self.tree.item(selected[0])
        self.selected_customer = {
            'id': item['values'][0],
            'phone': item['values'][1],
            'name': item['values'][2],
            'address': item['values'][3],
            'trn_vat': item['values'][4]
        }
        self.destroy()


class CustomerEditDialog(ctk.CTkToplevel):
    """نافذة تعديل/إضافة عميل"""
    
    def __init__(self, parent, db: DatabaseManager, customer: Customer = None, callback=None):
        super().__init__(parent)
        
        self.db = db
        self.customer = customer
        self.callback = callback
        
        self.title("تعديل عميل" if customer else "عميل جديد")
        self.geometry("500x400")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.focus_force()
        
        self.create_widgets()
        
        if customer:
            self.load_customer_data()
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الحقول
        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # رقم الهاتف
        ctk.CTkLabel(fields_frame, text="رقم الهاتف:").grid(row=0, column=0, sticky="w", pady=10)
        self.phone_entry = ctk.CTkEntry(fields_frame, width=300)
        self.phone_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # الاسم
        ctk.CTkLabel(fields_frame, text="الاسم:").grid(row=1, column=0, sticky="w", pady=10)
        self.name_entry = ctk.CTkEntry(fields_frame, width=300)
        self.name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # العنوان
        ctk.CTkLabel(fields_frame, text="العنوان:").grid(row=2, column=0, sticky="w", pady=10)
        self.address_entry = ctk.CTkEntry(fields_frame, width=300)
        self.address_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # TRN/VAT
        ctk.CTkLabel(fields_frame, text="TRN/VAT:").grid(row=3, column=0, sticky="w", pady=10)
        self.trn_entry = ctk.CTkEntry(fields_frame, width=300)
        self.trn_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # الأزرار
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(buttons_frame, text="حفظ", command=self.save, width=100).pack(side="right", padx=5)
        ctk.CTkButton(buttons_frame, text="إلغاء", command=self.destroy, width=100, 
                     fg_color="gray").pack(side="right", padx=5)
    
    def load_customer_data(self):
        """تحميل بيانات العميل"""
        self.phone_entry.insert(0, self.customer.phone)
        self.name_entry.insert(0, self.customer.name)
        self.address_entry.insert(0, self.customer.address or "")
        self.trn_entry.insert(0, self.customer.trn_vat or "")
    
    def save(self):
        """حفظ العميل"""
        phone = self.phone_entry.get().strip()
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        trn_vat = self.trn_entry.get().strip()
        
        if not phone or not name:
            messagebox.showerror("خطأ", "يرجى إدخال رقم الهاتف والاسم")
            return
        
        try:
            if self.customer:
                # تحديث
                self.customer.phone = phone
                self.customer.name = name
                self.customer.address = address
                self.customer.trn_vat = trn_vat
                self.db.update_customer(self.customer)
                messagebox.showinfo("نجاح", "تم تحديث بيانات العميل بنجاح")
            else:
                # إضافة جديد
                customer = Customer(phone=phone, name=name, address=address, trn_vat=trn_vat)
                self.db.add_customer(customer)
                messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح")
            
            if self.callback:
                self.callback()
            
            self.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "رقم الهاتف موجود بالفعل")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
