# CoreInventory

Inventory Management System built with Django 5, HTMX, Alpine.js, and Tailwind CSS.

## Quick Setup

```bash
# 1. Clone & enter the project
git clone https://github.com/harshilnpatel2003/Odoo-CoreInventory.git
cd Odoo-CoreInventory
git checkout backend

# 2. Create virtual environment & activate
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Seed demo data (creates users, products, warehouses, roles)
python manage.py seed_data

# 6. Run the server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** → you'll see the login page.

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@coreinventory.com | admin123 |
| Manager | manager@coreinventory.com | manager123 |
| Staff | staff1@coreinventory.com | staff123 |
| Viewer | viewer@coreinventory.com | viewer123 |

## Tech Stack

- **Backend:** Django 5, Django REST Framework, Celery + django-celery-beat
- **Frontend:** Django Templates, HTMX, Alpine.js, Tailwind CSS (CDN)
- **Auth:** django-allauth (email login, OTP password reset)
- **DB:** SQLite (dev) / PostgreSQL (prod via `DATABASE_URL`)

## Project Structure

```
├── config/            # Settings (base/dev/prod), URLs, Celery, WSGI
├── apps/
│   ├── accounts/      # Custom user model (email login)
│   ├── access/        # Roles, permissions, admin panel middleware
│   ├── products/      # Products, categories, units of measure
│   ├── warehouses/    # Warehouses & locations
│   ├── receipts/      # Incoming stock
│   ├── deliveries/    # Outgoing stock
│   ├── transfers/     # Internal transfers
│   ├── adjustments/   # Stock corrections
│   ├── ledger/        # StockMove (immutable ledger) & Stock snapshot
│   ├── alerts/        # Low-stock notifications & Celery tasks
│   └── dashboard/     # KPI dashboard
├── templates/         # Django templates (base layout, dashboard, login)
└── static/            # CSS, JS, icons
```

## Key Management Commands

```bash
python manage.py create_permissions   # Seed roles & permissions (idempotent)
python manage.py seed_data            # Seed demo data (calls create_permissions first)
```
