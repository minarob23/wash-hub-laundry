"""
نماذج قاعدة البيانات لنظام المغسلة
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Customer:
    """نموذج العميل"""
    id: Optional[int] = None
    phone: str = ""
    name: str = ""
    address: str = ""
    trn_vat: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Product:
    """نموذج المنتج/الخدمة"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    price_wash_press: float = 0.0
    price_press_only: float = 0.0
    price_wash_press_urgent: float = 0.0
    price_press_urgent: float = 0.0
    price_contract: float = 0.0
    image_path: Optional[str] = None


@dataclass
class InvoiceItem:
    """نموذج عنصر الفاتورة"""
    id: Optional[int] = None
    invoice_id: int = 0
    product_id: int = 0
    product_name: str = ""
    quantity: int = 1
    price: float = 0.0
    total: float = 0.0


@dataclass
class Invoice:
    """نموذج الفاتورة"""
    id: Optional[int] = None
    invoice_number: str = ""
    customer_id: int = 0
    date: str = ""
    delivery_date: str = ""
    delivery_time: str = ""
    service_type: str = ""
    customer_type: str = "Cash Customer"
    sales_man: str = ""
    depot: str = ""
    delivery_method: str = "PICKUP"
    status: str = "Hang"
    is_urgent: bool = False
    is_fold: bool = False
    is_tag: bool = True
    remark: str = ""
    subtotal: float = 0.0
    discount: float = 0.0
    vat: float = 0.0
    total: float = 0.0
    created_at: Optional[datetime] = None
    items: List[InvoiceItem] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
