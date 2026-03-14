# CoreInventory

CoreInventory is a modern, responsive, and robust Inventory Management System built with **Django 5, HTMX, Alpine.js, and Tailwind CSS**. It is designed to handle complex warehouse operations, maintain an immutable ledger, and provide real-time stock visibility with a seamless, single-page-application (SPA-like) user experience.

---

## 🚀 Key Features

### Core Operations
*   **Receipts:** Manage incoming stock from suppliers with a robust validation workflow (Draft → Waiting → Ready → Done).
*   **Deliveries:** Process outbound orders to customers, ensuring stock availability before processing.
*   **Transfers:** Handle internal inventory movements between different warehouses and locations.
*   **Adjustments:** Reconcile system inventory with physical stock counts easily.

### Inventory & Ledger
*   **Products Catalog:** Manage items with SKUs, Categories, Units of Measure, and configurable Reorder Points.
*   **Immutable Ledger & StockMoves:** Every validated operation generates immutable `StockMove` records, ensuring a perfect audit trail.
*   **Real-time Stock Valuation:** The system calculates real-time aggregated static per product and per location.

### Management & Alerts
*   **Admin Panel:** A restricted interface for system administrators to manage Users, Warehouses, Locations, custom Roles, and Permissions.
*   **Notifications System:** Real-time HTMX-powered notification badges alerting managers about low stock or out-of-stock items.
*   **Dynamic Dashboard:** High-level metrics, KPI summary cards, and quick navigation.

---

## 🛠️ Tech Stack

*   **Backend:** Django 5, Django REST Framework
*   **Frontend:** Django Templates, HTMX, Alpine.js, Tailwind CSS (via CDN)
*   **Database:** SQLite (Development) / PostgreSQL (Production ready)
*   **Authentication:** `django-allauth` (Email-based, OTP support)
*   **Static Files:** WhiteNoise for efficient static asset serving in production.

---

## ⚙️ Quick Setup Guide

Follow these steps to set up the project locally on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/harshilnpatel2003/Odoo-CoreInventory.git
cd Odoo-CoreInventory
git checkout backend
```

### 2. Set Up Python Virtual Environment
```bash
# Create the virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
```bash
# Apply all database migrations
python manage.py migrate

# Seed the database with demo data (Important for initial roles/permissions)
# This creates demo Users, Products, Categories, Warehouses, and configures Roles.
python manage.py seed_data
```

### 5. Static Files (Optional for Prod Verification)
```bash
python manage.py collectstatic --noinput
```

### 6. Run the Application
```bash
python manage.py runserver
```

Open your browser and navigate to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

## 🔑 Demo Login Credentials

The `seed_data` command generates the following accounts for immediate testing:

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **Admin** | `admin@coreinventory.com` | `admin123` | Full system access + Admin Panel |
| **Manager** | `manager@coreinventory.com` | `manager123` | Can validate operations & manage products |
| **Staff** | `staff1@coreinventory.com` | `staff123` | Can view and create draft operations |
| **Viewer** | `viewer@coreinventory.com` | `viewer123` | Read-only access to standard modules |

---

## 📁 Project Architecture

```
├── config/            # Core settings, URL routing, generic configurations
├── apps/
│   ├── accounts/      # Custom User model replacing default Django user
│   ├── access/        # RBAC (Role-Based Access Control) & Admin Panel
│   ├── dashboard/     # Aggregated KPI and summary views
│   ├── products/      # Catalog, categories, reorder levels
│   ├── warehouses/    # Site and bin-level location management
│   ├── ledger/        # Immutable StockMoves and static balance snapshots
│   ├── receipts/      # Inbound logistics module
│   ├── deliveries/    # Outbound logistics module
│   ├── transfers/     # Internal logistics module
│   ├── adjustments/   # Cycle counts and discrepancy logging
│   └── alerts/        # Threshold monitoring and notifications
├── templates/         # Reusable HTML partials, layouts, forms
└── static/            # Static assets (custom CSS, JS)
```

## 📜 Key Commands

*   `python manage.py create_permissions` — Idempotent command to generate default Role-Based Access guidelines.
*   `python manage.py seed_data` — Populates databases securely using factories for immediate testing.
