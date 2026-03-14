# CoreInventory — Implementation Task List

## Phase 1: Project Foundation & Configuration
- [x] Restructure project layout: `config/` (settings, urls, wsgi, celery) + `apps/` directory
- [x] Create split settings: [base.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/config/settings/base.py), [development.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/config/settings/development.py), [production.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/config/settings/production.py)
- [x] Configure [config/celery.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/config/celery.py)
- [x] Create [requirements.txt](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/requirements.txt) with all dependencies
- [x] Create [.env.example](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/.env.example), [Procfile](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/Procfile), [railway.toml](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/railway.toml)
- [x] Update [manage.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/manage.py) to point to `config.settings.development`
- [x] Install dependencies into venv and verify

## Phase 2: Data Models
- [x] [apps/accounts/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/accounts/models.py) — [CustomUser(AbstractUser)](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/accounts/models.py#5-38)
- [x] [apps/access/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/access/models.py) — [Role](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/access/models.py#4-19), [Permission](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/access/models.py#21-35), [RolePermission](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/access/models.py#37-58)
- [x] [apps/products/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/products/models.py) — [ProductCategory](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/products/models.py#7-25), [UnitOfMeasure](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/products/models.py#27-39), [Product](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/products/models.py#47-107)
- [x] [apps/warehouses/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/warehouses/models.py) — [Warehouse](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/warehouses/models.py#4-15), [Location](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/warehouses/models.py#17-33)
- [x] [apps/receipts/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/receipts/models.py) — [Receipt](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/receipts/models.py#14-60), [ReceiptLine](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/receipts/models.py#62-84)
- [x] [apps/deliveries/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/deliveries/models.py) — [Delivery](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/deliveries/models.py#14-61), [DeliveryLine](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/deliveries/models.py#63-85)
- [x] [apps/transfers/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/transfers/models.py) — [Transfer](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/transfers/models.py#14-63), [TransferLine](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/transfers/models.py#65-85)
- [x] [apps/adjustments/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/adjustments/models.py) — [Adjustment](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/adjustments/models.py#14-63), [AdjustmentLine](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/adjustments/models.py#65-97)
- [x] [apps/ledger/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/ledger/models.py) — [StockMove](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/ledger/models.py#5-67), [Stock](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/ledger/models.py#69-89)
- [x] [apps/alerts/models.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/alerts/models.py) — [Notification](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/apps/alerts/models.py#4-33)
- [x] `apps/dashboard/` — app skeleton (no models)
- [x] Run `makemigrations` and `migrate`

## Phase 3: Business Logic — Services Layer
- [x] `apps/receipts/services.py` — `validate_receipt()`
- [x] `apps/deliveries/services.py` — `validate_delivery()`
- [x] `apps/transfers/services.py` — `validate_transfer()`
- [x] `apps/adjustments/services.py` — `validate_adjustment()`
- [x] Auto-reference generation in model save methods

## Phase 4: Access Control System
- [x] Custom permission decorator `@require_permission`
- [x] Template tag `{% has_permission %}`
- [x] Permission middleware for admin panel access check

## Phase 5: Authentication (django-allauth)
- [x] Configure `django-allauth` in settings (email login, OTP, session auth)
- [ ] Templates: login, signup, password reset, profile
- [ ] Redirect flows

## Phase 6: Management Commands
- [x] `python manage.py create_permissions` — seed all permissions & system roles
- [x] `python manage.py seed_data` — demo data

## Phase 7: Static Assets & Base Templates
- [x] `static/css/styles.css` — CSS variables
- [ ] `templates/base.html` — sidebar, topbar, CDN links
- [ ] Reusable partials: `stat_card`, `status_badge`, `data_table`, etc.
- [ ] Configure WhiteNoise for static serving

## Phase 8: Dashboard
- [ ] Dashboard view + KPI query logic
- [ ] Templates + HTMX endpoints

## Phase 9: Products Module
- [ ] List / Detail / Create / Edit views + templates

## Phase 10: Operations Modules
- [ ] Receipts views + templates
- [ ] Deliveries views + templates
- [ ] Transfers views + templates
- [ ] Adjustments views + templates

## Phase 11: Ledger / Move History
- [ ] Read-only list view + templates

## Phase 12: Custom Admin Panel (`/admin-panel/`)
- [ ] User, Role, Permissions, Warehouse, Audit Log sections

## Phase 13: Alerts & Celery Tasks
- [x] `apps/alerts/tasks.py` — `check_low_stock`
- [ ] Notification views + endpoints

## Phase 14: Deployment & Polish
- [x] Health check endpoint
- [x] `config/urls.py` wiring
- [ ] End-to-end smoke test
