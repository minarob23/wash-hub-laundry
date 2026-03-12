"""
نوافذ مساعدة - إدارة المنتجات
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from database import DatabaseManager
from models import Product
import os
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ProductManagementWindow(ctk.CTkToplevel):
    """نافذة إدارة المنتجات"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        
        self.db = db
        
        self.title("إدارة المنتجات والخدمات")
        self.geometry("1000x600")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.focus_force()
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # شريط الأدوات
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(toolbar, text="منتج جديد", command=self.add_product).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="تحديث", command=self.load_products).pack(side="left", padx=5)
        
        # جدول المنتجات
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # إنشاء Treeview
        columns = ("ID", "Name", "Category", "W&P", "P Only", "W&P Ur", "P Ur", "Contract")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # تعريف الأعمدة
        self.tree.heading("ID", text="الرقم")
        self.tree.heading("Name", text="اسم المنتج")
        self.tree.heading("Category", text="الفئة")
        self.tree.heading("W&P", text="غسيل وكوي")
        self.tree.heading("P Only", text="كوي فقط")
        self.tree.heading("W&P Ur", text="غسيل وكوي عاجل")
        self.tree.heading("P Ur", text="كوي عاجل")
        self.tree.heading("Contract", text="عقد")
        
        self.tree.column("ID", width=40)
        self.tree.column("Name", width=150)
        self.tree.column("Category", width=120)
        self.tree.column("W&P", width=80)
        self.tree.column("P Only", width=80)
        self.tree.column("W&P Ur", width=80)
        self.tree.column("P Ur", width=80)
        self.tree.column("Contract", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(buttons_frame, text="تعديل", command=self.edit_product, width=100).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="حذف", command=self.delete_product, fg_color="red", width=100).pack(side="left", padx=5)
    
    def load_products(self):
        """تحميل المنتجات"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # تحميل المنتجات
        products = self.db.get_all_products()
        for product in products:
            self.tree.insert('', 'end', values=(
                product[0],  # ID
                product[1],  # Name
                product[2],  # Category
                f"{product[3]:.2f}",  # W&P
                f"{product[4]:.2f}",  # P Only
                f"{product[5]:.2f}",  # W&P Ur
                f"{product[6]:.2f}",  # P Ur
                f"{product[7]:.2f}"   # Contract
            ))
    
    def add_product(self):
        """إضافة منتج جديد"""
        ProductEditDialog(self, self.db, None, self.load_products)
    
    def edit_product(self):
        """تعديل منتج"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار منتج للتعديل")
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        
        # الحصول على بيانات المنتج
        product = self.db.get_product_by_id(product_id)
        
        if product:
            ProductEditDialog(self, self.db, product, self.load_products)
    
    def delete_product(self):
        """حذف منتج"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار منتج للحذف")
            return
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا المنتج؟"):
            messagebox.showinfo("معلومات", "سيتم إضافة هذه الميزة قريباً")


class ProductEditDialog(ctk.CTkToplevel):
    """نافذة تعديل/إضافة منتج"""
    
    def __init__(self, parent, db: DatabaseManager, product: Product = None, callback=None):
        super().__init__(parent)
        
        self.db = db
        self.product = product
        self.callback = callback
        self.image_path = None
        self._photo = None
        
        self.title("تعديل منتج" if product else "منتج جديد")
        self.geometry("640x600")
        
        # جعل النافذة في المقدمة
        self.lift()
        self.focus_force()
        
        self.create_widgets()
        
        if product:
            self.load_product_data()
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الحقول
        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        row = 0
        
        # اسم المنتج
        ctk.CTkLabel(fields_frame, text="اسم المنتج:").grid(row=row, column=0, sticky="w", pady=10)
        self.name_entry = ctk.CTkEntry(fields_frame, width=300)
        self.name_entry.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        # الفئة
        ctk.CTkLabel(fields_frame, text="الفئة:").grid(row=row, column=0, sticky="w", pady=10)
        self.category_entry = ctk.CTkComboBox(fields_frame, width=300,
                                             values=["Wash & Press", "Specialty", "Accessories"])
        self.category_entry.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        # الأسعار
        ctk.CTkLabel(fields_frame, text="غسيل وكوي:").grid(row=row, column=0, sticky="w", pady=10)
        self.price_wp = ctk.CTkEntry(fields_frame, width=300)
        self.price_wp.insert(0, "0.00")
        self.price_wp.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        ctk.CTkLabel(fields_frame, text="كوي فقط:").grid(row=row, column=0, sticky="w", pady=10)
        self.price_po = ctk.CTkEntry(fields_frame, width=300)
        self.price_po.insert(0, "0.00")
        self.price_po.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        ctk.CTkLabel(fields_frame, text="غسيل وكوي عاجل:").grid(row=row, column=0, sticky="w", pady=10)
        self.price_wpu = ctk.CTkEntry(fields_frame, width=300)
        self.price_wpu.insert(0, "0.00")
        self.price_wpu.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        ctk.CTkLabel(fields_frame, text="كوي عاجل:").grid(row=row, column=0, sticky="w", pady=10)
        self.price_pu = ctk.CTkEntry(fields_frame, width=300)
        self.price_pu.insert(0, "0.00")
        self.price_pu.grid(row=row, column=1, pady=10, padx=10)
        row += 1
        
        ctk.CTkLabel(fields_frame, text="عقد:").grid(row=row, column=0, sticky="w", pady=10)
        self.price_contract = ctk.CTkEntry(fields_frame, width=300)
        self.price_contract.insert(0, "0.00")
        self.price_contract.grid(row=row, column=1, pady=10, padx=10)
        row += 1

        # صورة المنتج
        ctk.CTkLabel(fields_frame, text="صورة المنتج:").grid(row=row, column=0, sticky="nw", pady=10)
        img_col = ctk.CTkFrame(fields_frame, fg_color="transparent")
        img_col.grid(row=row, column=1, sticky="w", pady=10, padx=10)

        # Preview canvas
        self._img_canvas = tk.Canvas(img_col, width=120, height=120,
                                     bg="#f0f2f5", highlightthickness=1,
                                     highlightbackground="#ccc")
        self._img_canvas.pack(side="left")
        self._img_canvas.create_text(60, 60, text="No Image",
                                     fill="#aaa", font=("Arial", 9), tags="placeholder")

        img_btn_col = ctk.CTkFrame(img_col, fg_color="transparent")
        img_btn_col.pack(side="left", padx=10, anchor="n")
        ctk.CTkButton(img_btn_col, text="Choose Image", width=120, height=32,
                      fg_color="#2b5797", hover_color="#1a3f73",
                      text_color="white", font=ctk.CTkFont(size=11),
                      command=self._pick_image).pack(pady=(0, 6))
        ctk.CTkButton(img_btn_col, text="Clear Image", width=120, height=32,
                      fg_color="#6c757d", hover_color="#555",
                      text_color="white", font=ctk.CTkFont(size=11),
                      command=self._clear_image).pack()
        self._img_path_lbl = ctk.CTkLabel(img_btn_col, text="",
                                          font=ctk.CTkFont(size=9),
                                          text_color="#888", wraplength=120)
        self._img_path_lbl.pack(pady=(6, 0))
        row += 1

        # الأزرار
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(buttons_frame, text="حفظ", command=self.save, width=100).pack(side="right", padx=5)
        ctk.CTkButton(buttons_frame, text="إلغاء", command=self.destroy, width=100, 
                     fg_color="gray").pack(side="right", padx=5)
    
    def _pick_image(self):
        """فتح مربع حوار اختيار الصورة"""
        path = filedialog.askopenfilename(
            title="Choose Product Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                       ("All Files", "*.*")]
        )
        if path:
            self.image_path = path
            self._show_image_preview(path)
            self._img_path_lbl.configure(text=os.path.basename(path))

    def _clear_image(self):
        self.image_path = None
        self._photo = None
        self._img_canvas.delete("all")
        self._img_canvas.create_text(60, 60, text="No Image",
                                     fill="#aaa", font=("Arial", 9), tags="placeholder")
        self._img_path_lbl.configure(text="")

    def _show_image_preview(self, path):
        """عرض معاينة الصورة في الـ Canvas"""
        self._img_canvas.delete("all")
        if not PIL_AVAILABLE:
            self._img_canvas.create_text(60, 60, text="PIL not installed",
                                         fill="#e74c3c", font=("Arial", 8))
            return
        try:
            img = Image.open(path)
            img.thumbnail((120, 120), Image.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            self._img_canvas.create_image(60, 60, image=self._photo, anchor="center")
        except Exception as ex:
            self._img_canvas.create_text(60, 60, text=f"Error:\n{ex}",
                                         fill="#e74c3c", font=("Arial", 8))

    def load_product_data(self):
        """تحميل بيانات المنتج"""
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, self.product.name)
        
        self.category_entry.set(self.product.category)
        
        self.price_wp.delete(0, 'end')
        self.price_wp.insert(0, str(self.product.price_wash_press))
        
        self.price_po.delete(0, 'end')
        self.price_po.insert(0, str(self.product.price_press_only))
        
        self.price_wpu.delete(0, 'end')
        self.price_wpu.insert(0, str(self.product.price_wash_press_urgent))
        
        self.price_pu.delete(0, 'end')
        self.price_pu.insert(0, str(self.product.price_press_urgent))
        
        self.price_contract.delete(0, 'end')
        self.price_contract.insert(0, str(self.product.price_contract))

        # Load image if exists
        if hasattr(self.product, 'image_path') and self.product.image_path:
            self.image_path = self.product.image_path
            self._img_path_lbl.configure(text=os.path.basename(self.product.image_path))
            self._show_image_preview(self.product.image_path)
    
    def save(self):
        """حفظ المنتج"""
        name = self.name_entry.get().strip()
        category = self.category_entry.get()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المنتج")
            return
        
        try:
            price_wp = float(self.price_wp.get())
            price_po = float(self.price_po.get())
            price_wpu = float(self.price_wpu.get())
            price_pu = float(self.price_pu.get())
            price_contract = float(self.price_contract.get())
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أسعار صحيحة")
            return
        
        try:
            if self.product:
                # تحديث المنتج الموجود
                import sqlite3
                conn = sqlite3.connect('laundry_system.db')
                cur = conn.cursor()
                cur.execute("""
                    UPDATE products SET
                        name=?, category=?,
                        price_wash_press=?, price_press_only=?,
                        price_wash_press_urgent=?, price_press_urgent=?,
                        price_contract=?, image_path=?
                    WHERE id=?
                """, (name, category, price_wp, price_po, price_wpu,
                        price_pu, price_contract, self.image_path, self.product.id))
                conn.commit()
                conn.close()
                messagebox.showinfo("نجاح", "تم تحديث المنتج بنجاح")
            else:
                # إضافة جديد
                product = Product(
                    name=name,
                    category=category,
                    price_wash_press=price_wp,
                    price_press_only=price_po,
                    price_wash_press_urgent=price_wpu,
                    price_press_urgent=price_pu,
                    price_contract=price_contract,
                    image_path=self.image_path
                )
                self.db.add_product(product)
                messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح")
            
            if self.callback:
                self.callback()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
