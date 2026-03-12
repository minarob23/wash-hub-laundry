# 🧺 نظام إدارة مغسلة - AiFSoft Bt | WASH HUB LAUNDRY

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

**نظام كاشير احترافي لإدارة المغاسل مع واجهة عصرية وسهلة الاستخدام**

[البدء السريع](#-التثبيت-والتشغيل) • [المميزات](#-المميزات) • [دليل الاستخدام](USER_GUIDE.md) • [دعم فني](#-الدعم-الفني)

</div>

---

## 📸 لقطات الشاشة

> النظام مصمم ليطابق الصورة المرفقة مع ميزات إضافية

---

## 📋 المميزات

### ✨ إدارة الفواتير
- إصدار فواتير جديدة برقم تسلسلي تلقائي
- حفظ واسترجاع الفواتير
- طباعة الفواتير
- إدارة التواريخ ووقت التسليم

### 👤 إدارة العملاء
- إضافة وتعديل بيانات العملاء
- البحث السريع بالهاتف
- عملاء نقديين وآجلين
- حفظ العناوين ورقم TRN/VAT

### 🧥 أنواع الخدمات
1. **Wash & Press** - غسيل وكوي
2. **Pressing Only** - كوي فقط
3. **Wash & Press Urgent** - غسيل وكوي عاجل
4. **Pressing Urgent** - كوي عاجل
5. **Contract** - عقود

### 📦 المنتجات
- Jacket (جاكيت)
- Trouser (بنطلون)
- Pullovers (بلوفر)
- Shirt (قميص)
- White Dishdasha (دشداشة بيضاء)
- Ghutra Wool (غترة صوف)
- Vest (صديري)
- Socks (جوارب)
- Skirt (تنورة)
- Frock (فستان أطفال)
- Dressing Gown (روب)
- Lady Suit (بدلة نسائية)
- Dress Cotton (فستان قطن)
- Night Dress (قمصان نوم)
- Abaya (عباية)
- Sheila (شيلة)
- وأكثر...

### 💰 نظام الحسابات
- حساب الإجمالي الفرعي
- الخصومات
- ضريبة القيمة المضافة (VAT)
- الإجمالي النهائي

### 📊 خيارات إضافية
- **PICKUP** أو **Home Delivery** (توصيل منزلي)
- حالة الملابس: **Urgent** (عاجل), **Hang** (علاقة), **Fold** (مطوي)
- **TAG** - ملصقات التعريف
- ملاحظات للفاتورة

## 🚀 التثبيت والتشغيل

### المتطلبات
- ✅ Python 3.8 أو أحدث
- ✅ Windows 10/11 (متوافق مع Windows 7+)
- ✅ 200 MB مساحة فارغة على الأقل
- ✅ دقة شاشة: 1366x768 أو أعلى (موصى به: 1920x1080)

### 🎯 طرق التثبيت والتشغيل

#### الطريقة 1: استخدام Launcher (الأسهل - موصى به) ⭐
1. **قم بتحميل Python** من [python.org](https://www.python.org/downloads/)
   - ✅ تأكد من تفعيل "Add Python to PATH"
2. **انقر مزدوجاً على** `launcher.bat`
3. **اختر** [2] لتثبيت المكتبات (مرة واحدة فقط)
4. **اختر** [1] لتشغيل البرنامج

#### الطريقة 2: تشغيل مباشر
```bash
# انقر مزدوجاً على run.bat
```

#### الطريقة 3: يدوياً (للمطورين)
```bash
# 1. استنساخ أو تحميل المشروع
git clone <repository-url>
cd "سيستم مغسلة"

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. تشغيل البرنامج
python main.py
```

### ⚡ البدء السريع (لأول مرة)
اقرأ ملف [`QUICKSTART.md`](QUICKSTART.md) للحصول على دليل سريع خطوة بخطوة!

## 📖 طريقة الاستخدام

### إصدار فاتورة جديدة
1. اختر نوع الخدمة من التبويبات العلوية
2. أدخل بيانات العميل (رقم الهاتف، الاسم، العنوان)
3. اختر المنتجات بالنقر عليها
4. حدد الكمية لكل منتج
5. اختر طريقة التسليم (PICKUP أو Home Delivery)
6. حدد حالة الملابس (Urgent, Hang, Fold)
7. اضغط "Save Order" لحفظ الفاتورة

### البحث عن عميل
- أدخل رقم الهاتف في حقل "Customer"
- أو اضغط على زر البحث (🔍) للبحث المتقدم

### استرجاع فاتورة
1. اضغط على زر "Retrieve"
2. أدخل رقم الفاتورة
3. سيتم تحميل جميع بيانات الفاتورة

## 🗄️ قاعدة البيانات

يستخدم النظام قاعدة بيانات SQLite المحلية مع الجداول التالية:
- **customers** - بيانات العملاء
- **products** - المنتجات والخدمات
- **invoices** - الفواتير الرئيسية
- **invoice_items** - تفاصيل كل فاتورة

## 🎨 الواجهة

النظام مصمم بواجهة عصرية باستخدام:
- **CustomTkinter** - واجهة رسومية حديثة
- ألوان مريحة للعين
- تصميم سهل الاستخدام
- دعم الشاشات الكبيرة

## 📝 ملاحظات

- النظام يحفظ البيانات محلياً في ملف `laundry_system.db`
- يمكن عمل نسخة احتياطية من الملف بانتظام
- للطباعة، تأكد من توصيل الطابعة

## � هيكل المشروع

```
سيستم مغسلة/
│
├── 🚀 ملفات التشغيل
│   ├── launcher.bat          # قائمة تفاعلية (موصى به)
│   ├── run.bat               # تشغيل مباشر
│   └── install.bat           # تثبيت المكتبات
│
├── 💻 ملفات البرنامج
│   ├── main.py               # الملف الرئيسي
│   ├── database.py           # إدارة قاعدة البيانات
│   ├── models.py             # نماذج البيانات
│   ├── customer_manager.py   # إدارة العملاء
│   └── product_manager.py    # إدارة المنتجات
│
├── 📚 التوثيق
│   ├── README.md             # هذا الملف
│   ├── QUICKSTART.md         # دليل البدء السريع
│   ├── USER_GUIDE.md         # دليل المستخدم الكامل
│   └── DEVELOPER_GUIDE.md    # دليل المطور
│
├── ⚙️ الإعدادات
│   └── requirements.txt      # المكتبات المطلوبة
│
└── 💾 البيانات
    └── laundry_system.db     # قاعدة البيانات (تُنشأ تلقائياً)
```

## 🤝 المساهمة

نرحب بمساهماتك! إذا كنت ترغب في تحسين المشروع:

1. Fork المشروع
2. أنشئ branch (`git checkout -b feature/AmazingFeature`)
3. Commit تغييراتك (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى Branch (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

## 📝 التحديثات القادمة

- [ ] 🖨️ طباعة الفواتير (حراري + A4)
- [ ] 📊 التقارير المفصلة (يومي، شهري، سنوي)
- [ ] 💬 إرسال رسائل واتساب تلقائياً
- [ ] 📱 تطبيق موبايل للمتابعة
- [ ] 🌐 نسخة ويب أونلاين
- [ ] 📷 مسح الباركود
- [ ] 🎨 المظهر الداكن
- [ ] 🏪 دعم عدة فروع
- [ ] 📤 تصدير التقارير (Excel, PDF)
- [ ] 🔐 نظام صلاحيات المستخدمين

## 🐛 الإبلاغ عن مشاكل

إذا واجهت أي مشكلة:
1. تحقق من [دليل حل المشاكل](QUICKSTART.md#-حل-المشاكل-الشائعة)
2. ابحث في [Issues](../../issues) المفتوحة
3. اعمل Issue جديد مع وصف تفصيلي للمشكلة

## 💡 أفكار وطلبات ميزات

لديك فكرة لتحسين النظام؟
- افتح [Feature Request](../../issues/new)
- شارك فكرتك مع التفاصيل

## 🔧 الدعم الفني

### للمستخدمين العاديين:
- 📖 اقرأ [دليل المستخدم](USER_GUIDE.md)
- ⚡ راجع [البدء السريع](QUICKSTART.md)
- ❓ اطلع على [الأسئلة الشائعة](USER_GUIDE.md#-الأسئلة-الشائعة)

### للمطورين:
- 👨‍💻 راجع [دليل المطور](DEVELOPER_GUIDE.md)
- 📧 تواصل مع فريق التطوير

## 🙏 شكر وتقدير

- **CustomTkinter** - للواجهة الرسومية الحديثة
- **Python Community** - للأدوات والمكتبات الرائعة
- **جميع المساهمين** - لجعل هذا المشروع أفضل

## 📜 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل

```
MIT License

Copyright (c) 2026 AiFSoft Bt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 📞 التواصل

- 📧 البريد الإلكتروني: support@example.com
- 💬 الدعم الفني: [فتح تذكرة](../../issues/new)
- 🌐 الموقع: [قريباً]

---

<div align="center">

**صُنع بـ ❤️ لأصحاب المغاسل**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/laundry-system?style=social)](../../stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/laundry-system?style=social)](../../network/members)

**نظام إدارة مغسلة © 2026 - جميع الحقوق محفوظة**

[⬆ العودة للأعلى](#-نظام-إدارة-مغسلة---aifsoft-bt--wash-hub-laundry)

</div>
