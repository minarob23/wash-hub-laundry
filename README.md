# 🧺 Wash Hub Laundry - AiFSoft Bt | WASH HUB LAUNDRY

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

**A professional laundry POS & management system with a modern, easy-to-use interface**

[Quick Start](#-installation--setup) • [Features](#-features) • [User Guide](USER_GUIDE.md) • [Support](#-support)

</div>

---

## 📸 Screenshots

> The system is designed with a modern UI and packed with powerful features

---

## 📋 Features

### ✨ Invoice Management
- Create new invoices with automatic sequential numbering
- Save and retrieve invoices
- Print invoices
- Manage dates and delivery times

### 👤 Customer Management
- Add and edit customer information
- Quick search by phone number
- Support for cash and credit customers
- Store addresses and TRN/VAT numbers

### 🧥 Service Types
1. **Wash & Press** - Full wash and ironing
2. **Pressing Only** - Ironing only
3. **Wash & Press Urgent** - Express wash and ironing
4. **Pressing Urgent** - Express ironing
5. **Contract** - Contract-based service

### 📦 Supported Products
- Jacket
- Trouser
- Pullovers
- Shirt
- White Dishdasha
- Ghutra Wool
- Vest
- Socks
- Skirt
- Frock
- Dressing Gown
- Lady Suit
- Dress Cotton
- Night Dress
- Abaya
- Sheila
- And more...

### 💰 Billing & Accounting
- Subtotal calculation
- Discounts
- VAT (Value Added Tax)
- Grand total

### 📊 Additional Options
- **PICKUP** or **Home Delivery**
- Garment status: **Urgent**, **Hang**, **Fold**
- **TAG** - Identification labels
- Invoice remarks/notes
- Dashboard with analytics
- Full reports module
- Accounts & expenses tracking

## 🚀 Installation & Setup

### Requirements
- ✅ Python 3.8 or newer
- ✅ Windows 10/11 (compatible with Windows 7+)
- ✅ At least 200 MB free disk space
- ✅ Screen resolution: 1366x768 or higher (recommended: 1920x1080)

### 🎯 Installation Methods

#### Method 1: Using Launcher (Easiest - Recommended) ⭐
1. **Download Python** from [python.org](https://www.python.org/downloads/)
   - ✅ Make sure to check "Add Python to PATH"
2. **Double-click** `launcher.bat`
3. **Select** [2] to install dependencies (only once)
4. **Select** [1] to run the application

#### Method 2: Direct Run
```bash
# Double-click run.bat
```

#### Method 3: Manual (For Developers)
```bash
# 1. Clone or download the project
git clone https://github.com/minarob23/wash-hub-laundry.git
cd wash-hub-laundry

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

### ⚡ First-Time Quick Start
Read [`QUICKSTART.md`](QUICKSTART.md) for a step-by-step beginner guide!

## 📖 How to Use

### Creating a New Invoice
1. Select the service type from the top tabs
2. Enter customer details (phone, name, address)
3. Click on products to add them to the cart
4. Set the quantity for each item
5. Choose delivery method (PICKUP or Home Delivery)
6. Set garment status (Urgent, Hang, Fold)
7. Click **"Delivery & Save"** to save the invoice

### Searching for a Customer
- Type the phone number in the "Customer" field
- Or click the search button (🔍) for advanced search

### Retrieving an Invoice
1. Click the **"Retrieve"** button
2. Enter the invoice number
3. All invoice data will be loaded automatically

## 🗄️ Database

The system uses a local SQLite database with the following tables:
- **customers** - Customer records
- **products** - Products and services
- **invoices** - Main invoice records
- **invoice_items** - Line items for each invoice
- **admin_profile** - Admin profile and settings

## 🎨 UI & Technology

Built with a modern interface using:
- **CustomTkinter** - Modern Python GUI framework
- **SQLite** - Lightweight local database
- **Pillow** - Image handling
- Eye-friendly color scheme
- Responsive layout for large screens

## 📝 Notes

- Data is stored locally in `laundry_system.db`
- Back up this file regularly
- Make sure your printer is connected before printing

## 📁 Project Structure

```
wash-hub-laundry/
│
├── 🚀 Launchers
│   ├── launcher.bat          # Interactive menu launcher (recommended)
│   ├── run.bat               # Direct run
│   └── install.bat           # Install dependencies
│
├── 💻 Source Code
│   ├── main.py               # Main application file
│   ├── database.py           # Database management
│   ├── models.py             # Data models
│   ├── customer_manager.py   # Customer management window
│   └── product_manager.py    # Product management window
│
├── 📚 Documentation
│   ├── README.md             # This file
│   ├── QUICKSTART.md         # Quick start guide
│   ├── USER_GUIDE.md         # Full user guide
│   └── DEVELOPER_GUIDE.md    # Developer guide
│
├── ⚙️ Configuration
│   └── requirements.txt      # Python dependencies
│
└── 💾 Data
    └── laundry_system.db     # SQLite database (auto-created on first run)
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create your branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Upcoming Features

- [ ] 🖨️ Invoice printing (thermal + A4)
- [ ] 📊 Detailed reports (daily, monthly, yearly)
- [ ] 💬 Automatic WhatsApp notifications
- [ ] 📱 Mobile companion app
- [ ] 🌐 Web-based version
- [ ] 📷 Barcode scanning
- [ ] 🎨 Dark mode
- [ ] 🏪 Multi-branch support
- [ ] 📤 Export reports (Excel, PDF)
- [ ] 🔐 Role-based user permissions

## 🐛 Bug Reports

If you encounter any issues:
1. Check the [Troubleshooting Guide](QUICKSTART.md)
2. Search through [open Issues](../../issues)
3. Open a new issue with a detailed description

## 💡 Feature Requests

Have an idea to improve the system?
- Open a [Feature Request](../../issues/new)
- Share your idea with details

## 🔧 Support

### For End Users:
- 📖 Read the [User Guide](USER_GUIDE.md)
- ⚡ Check the [Quick Start](QUICKSTART.md)
- ❓ Browse the [FAQ](USER_GUIDE.md)

### For Developers:
- 👨‍💻 Read the [Developer Guide](DEVELOPER_GUIDE.md)
- 📧 Contact the development team

## 🙏 Acknowledgements

- **CustomTkinter** - For the modern GUI framework
- **Python Community** - For the amazing tools and libraries
- **All Contributors** - For making this project better

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 AiFSoft Bt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 📞 Contact

-  Support: [Open a ticket](../../issues/new)
- 🌐 Website: Coming soon

---

<div align="center">

**Made with ❤️ for laundry business owners**

[![GitHub stars](https://img.shields.io/github/stars/minarob23/wash-hub-laundry?style=social)](../../stargazers)
[![GitHub forks](https://img.shields.io/github/forks/minarob23/wash-hub-laundry?style=social)](../../network/members)

**Wash Hub Laundry © 2026 — All Rights Reserved**

[⬆ Back to Top](#-wash-hub-laundry---aifsoft-bt--wash-hub-laundry)

</div>
