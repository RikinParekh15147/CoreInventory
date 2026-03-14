# CoreInventory — Implementation Plan

A complete, production-ready Django Inventory Management System that replaces manual stock management with a centralized web app. The workspace currently has a bare Django scaffold (`CoreInventory/`) that must be restructured entirely.

---

## Proposed Changes

### 1. Project Foundation & Configuration

> **Goal:** Replace the default `CoreInventory/` Django config with the spec's `config/` layout and split settings, wire up Celery, and create all deployment files.

#### [DELETE] [settings.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/settings.py)
The default monolithic settings file will be replaced by split settings under `config/settings/`.

#### [DELETE] [urls.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/urls.py)
Replaced by `config/urls.py`.

#### [DELETE] [wsgi.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/wsgi.py)
Replaced by `config/wsgi.py`.

#### [DELETE] [asgi.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/asgi.py)
No longer needed under the new layout.

#### [MODIFY] [manage.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/manage.py)
Change `DJANGO_SETTINGS_MODULE` to `config.settings.development`.

#### [NEW] `config/settings/base.py`
All shared settings: `INSTALLED_APPS` (all 11 apps + allauth, htmx, DRF, cloudinary, celery-beat, whitenoise), `AUTH_USER_MODEL = 'accounts.CustomUser'`, middleware stack, templates config, static/media config, `CELERY_*` settings, `ALLAUTH_*` settings, CSS/JS CDN references, Cloudinary config via env vars.

#### [NEW] `config/settings/development.py`
`DEBUG = True`, `DATABASES` using SQLite for local dev, console email backend, CORS allow all.

#### [NEW] `config/settings/production.py`
`DEBUG = False`, `DATABASES` via `dj-database-url`, WhiteNoise, `SECURE_*` flags, `REDIS_URL` for Celery broker, SMTP email backend.

#### [NEW] `config/celery.py`
Standard Celery app with `autodiscover_tasks()`.

#### [NEW] `config/urls.py`
Root URL conf including all app URLs, allauth paths, health check endpoint, Django admin.

#### [NEW] `config/wsgi.py`
WSGI application pointing to `config.settings.production` (overridable via env).

#### [NEW] `requirements.txt`
All packages from the spec.

#### [NEW] `.env.example`
Template of all required environment variables.

#### [NEW] `Procfile` / `railway.toml`
Deployment configs as specified.

---

### 2. Data Models (11 Django Apps)

> **Goal:** Create all Django apps under `apps/` with models matching the spec exactly, including `__str__`, properties, auto-generated fields, and `Meta` options.

#### [NEW] `apps/accounts/` — models, admin, apps, urls
`CustomUser(AbstractUser)` with email as login field, FK to `Role`, FK to `Warehouse`.

#### [NEW] `apps/access/` — models, admin, apps, urls
`Role`, `Permission`, `RolePermission` models. System roles are non-deletable.

#### [NEW] `apps/products/` — models, admin, apps, urls
`ProductCategory` (self-FK for nesting), `UnitOfMeasure`, `Product` (CloudinaryField for image, auto-SKU via `pre_save`, `total_stock` and `is_low_stock` properties).

#### [NEW] `apps/warehouses/` — models, admin, apps, urls
`Warehouse`, `Location` (FK to Warehouse).

#### [NEW] `apps/receipts/` — models, admin, apps, urls
`Receipt` (auto-ref `RCP-YYYY-NNNN`), `ReceiptLine`.

#### [NEW] `apps/deliveries/` — models, admin, apps, urls
`Delivery` (auto-ref `DLV-YYYY-NNNN`), `DeliveryLine`.

#### [NEW] `apps/transfers/` — models, admin, apps, urls
`Transfer` (auto-ref `TRF-YYYY-NNNN`), `TransferLine`.

#### [NEW] `apps/adjustments/` — models, admin, apps, urls
`Adjustment` (auto-ref `ADJ-YYYY-NNNN`), `AdjustmentLine` (with `difference` property).

#### [NEW] `apps/ledger/` — models, admin, apps, urls
`StockMove` (immutable ledger), `Stock` (`unique_together = ('product', 'location')`).

#### [NEW] `apps/alerts/` — models, admin, apps, urls
`Notification` model.

#### [NEW] `apps/dashboard/` — apps, urls
No models — view-only app.

---

### 3. Business Logic — Services Layer

> **Goal:** Encapsulate all stock mutation logic in service functions, never in views. Every mutation wrapped in `transaction.atomic()`.

#### [NEW] `apps/receipts/services.py`
`validate_receipt(receipt, user)` — creates `StockMove` + upserts `Stock`, sets status to `done`, triggers async low-stock check.

#### [NEW] `apps/deliveries/services.py`
`validate_delivery(delivery, user)` — checks sufficient stock, raises `InsufficientStockError`, creates `StockMove`, decrements `Stock`.

#### [NEW] `apps/transfers/services.py`
`validate_transfer(transfer, user)` — creates paired `StockMove` records (transfer_out + transfer_in), adjusts `Stock` at both locations.

#### [NEW] `apps/adjustments/services.py`
`validate_adjustment(adjustment, user)` — compares `actual_qty` vs `recorded_qty`, creates `adjustment_in` or `adjustment_out` `StockMove`, sets `Stock.quantity = actual_qty`.

#### [NEW] `apps/products/signals.py` / `apps/receipts/signals.py` etc.
`pre_save` signals for auto-reference generation (`RCP-YYYY-NNNN`) and auto-SKU (`PRD-XXXXXX`).

---

### 4. Access Control System

> **Goal:** Build a custom permission system separate from Django's built-in `auth` perms, using the `Role`→`RolePermission`→`Permission` model chain.

#### [NEW] `apps/access/decorators.py`
`@require_permission('codename')` — checks `RolePermission` for the logged-in user's role.

#### [NEW] `apps/access/templatetags/access_tags.py`
`{% has_permission user 'codename' as var %}` template tag.

#### [NEW] `apps/access/middleware.py`
Middleware to restrict `/admin-panel/` to Admin role or superusers.

---

### 5. Authentication (django-allauth)

> **Goal:** Email-based login, OTP password reset, session auth, proper redirects.

#### [MODIFY] `config/settings/base.py`
Add allauth settings: `ACCOUNT_AUTHENTICATION_METHOD = 'email'`, `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`, `LOGIN_REDIRECT_URL = '/dashboard/'`, etc.

#### [NEW] `templates/accounts/login.html`
#### [NEW] `templates/accounts/signup.html`
#### [NEW] `templates/accounts/password_reset.html`
#### [NEW] `templates/accounts/profile.html`

---

### 6. Management Commands

#### [NEW] `apps/access/management/commands/create_permissions.py`
Seeds all `Permission` records, creates the 4 system `Role` records, assigns default permissions via `RolePermission`. Idempotent.

#### [NEW] `apps/accounts/management/commands/seed_data.py`
Creates demo warehouses, locations, users, products, categories, UoMs, receipts, deliveries, stock moves. Depends on `create_permissions` running first.

---

### 7. Static Assets & Base Templates

> **Goal:** Dark sidebar + white content area layout; CDN-based Tailwind, HTMX, Alpine.js; Google Fonts (Inter, JetBrains Mono); CSS variables for the color palette.

#### [NEW] `templates/base.html`
Full page shell: sidebar nav (with conditional visibility per permission), top bar (breadcrumb, notification bell, search), content block, Tailwind CDN, HTMX CDN, Alpine.js CDN, Google Fonts, toast container.

#### [NEW] `templates/components/stat_card.html`
#### [NEW] `templates/components/status_badge.html`
#### [NEW] `templates/components/data_table.html`
#### [NEW] `templates/components/page_header.html`
#### [NEW] `templates/components/modal.html`
#### [NEW] `templates/components/toast.html`
#### [NEW] `templates/components/empty_state.html`
#### [NEW] `templates/components/line_item_row.html`

#### [NEW] `static/css/styles.css`
CSS variables for the entire color palette, custom utility classes.

---

### 8. Dashboard

#### [NEW] `apps/dashboard/views.py`
`DashboardView` — computes KPIs (total products, low stock, out of stock, pending receipts/deliveries), fetches last 15 `StockMove` records, returns full page or HTMX partial.

#### [NEW] `apps/dashboard/urls.py`
`/dashboard/`, `/dashboard/kpis/` (HTMX partial for auto-refresh).

#### [NEW] `templates/dashboard/index.html`
KPI cards, recent activity feed, quick action buttons.

---

### 9. Products Module

#### [NEW] `apps/products/views.py`
List (filterable, searchable), Detail, Create, Edit views. Product search autocomplete endpoint. Stock-by-location partial.

#### [NEW] `apps/products/urls.py`
#### [NEW] `apps/products/forms.py`
#### [NEW] `templates/products/list.html`, `detail.html`, `form.html`, `partials/`

---

### 10. Operations Modules

> **Goal:** Receipts, Deliveries, Transfers, and Adjustments each get List, Detail/Form, and Create views with HTMX inline lines and status workflow (Draft → Ready → Done/Cancelled).

For **each** of the four modules:

#### [NEW] `apps/<module>/views.py`
List view (HTMX filtering by status/location/date/search), Detail/Form view (inline lines, status workflow buttons), Create view (auto-ref on save).

#### [NEW] `apps/<module>/urls.py`
#### [NEW] `apps/<module>/forms.py`
#### [NEW] `templates/<module>/list.html`, `detail.html`, `form.html`, `partials/`

---

### 11. Ledger / Move History

#### [NEW] `apps/ledger/views.py`
Read-only list with HTMX filtering by product, location, type, date range, user.

#### [NEW] `templates/ledger/move_list.html`

---

### 12. Custom Admin Panel (`/admin-panel/`)

> **Goal:** Entirely separate from Django's `/admin/`. Only accessible by Admin role or superusers.

#### [NEW] `apps/access/views.py`
Views for: User Management (CRUD + deactivate + filter), Role Management (list, create, clone, protect system), Permissions Matrix (grid + bulk save), Warehouse Management (CRUD + user assignment), Audit Log (read-only StockMove + login events).

#### [NEW] `apps/access/urls.py`
URL namespace `admin-panel/` → `users/`, `roles/`, `roles/<id>/permissions/`, `warehouses/`, `audit-log/`.

#### [NEW] `templates/access/` — 10+ templates for each admin section.

---

### 13. Alerts & Celery Tasks

#### [NEW] `apps/alerts/tasks.py`
`check_low_stock()` — queries `Stock` where `quantity <= product.reorder_point`, creates `Notification` records. Registered as periodic task (every 6 hours via `django-celery-beat`).

#### [NEW] `apps/alerts/views.py`
Notification list (mark read), unread count endpoint (HTMX).

#### [NEW] `apps/alerts/urls.py`
#### [NEW] `templates/alerts/`

---

### 14. Config Finalization & Deployment

#### [MODIFY] `config/urls.py`
Final wiring of all apps, health check.

#### Review
- `select_related` / `prefetch_related` audit on all list querysets
- Inline validation errors via HTMX on all forms
- `__str__` on every model

---

## Verification Plan

### Automated Tests

1. **Model Unit Tests** — for each app, verify model creation, `__str__`, properties (`total_stock`, `is_low_stock`, `difference`), auto-ref generation, auto-SKU generation. Run with:
   ```
   python manage.py test apps.products.tests apps.ledger.tests --settings=config.settings.development
   ```

2. **Service Layer Tests** — test `validate_receipt`, `validate_delivery`, `validate_transfer`, `validate_adjustment` in isolation, including:
   - Happy path (stock created/updated correctly)
   - `InsufficientStockError` raised when stock is too low
   - Atomic rollback on error
   - `StockMove` records created with correct types
   ```
   python manage.py test apps.receipts.tests apps.deliveries.tests apps.transfers.tests apps.adjustments.tests --settings=config.settings.development
   ```

3. **Access Control Tests** — test `@require_permission` decorator returns 403 for unauthorized, 200 for authorized. Test template tag output.
   ```
   python manage.py test apps.access.tests --settings=config.settings.development
   ```

4. **Management Command Tests** — run `create_permissions` and `seed_data`, verify records exist.
   ```
   python manage.py create_permissions --settings=config.settings.development
   python manage.py seed_data --settings=config.settings.development
   ```

5. **Full Test Suite:**
   ```
   python manage.py test --settings=config.settings.development
   ```

### Manual Verification

1. **Boot test:** Run `python manage.py runserver` and confirm no errors, home page redirects to login.
2. **Seed and login:** Run `seed_data`, log in as `admin@coreinventory.com / admin123`, confirm dashboard loads with KPI cards.
3. **Navigation:** Click every sidebar link, confirm pages load without errors.
4. **HTMX interactions:** On receipts list, change status filter tab — verify table updates without page reload.
5. **Validation flow:** Create a new receipt with 2 line items → Confirm → Validate → verify stock updated in product detail.
6. **Admin panel:** Navigate to `/admin-panel/`, verify user list, role list, permissions matrix, and audit log all render.
7. **Permission enforcement:** Log in as Viewer user, confirm cannot see "New Receipt" button or access create URL directly (should get 403).

> [!IMPORTANT]
> **Restructuring the existing scaffold.** The existing `CoreInventory/` directory will be replaced by the `config/` package. The old [settings.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/settings.py), [urls.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/urls.py), [wsgi.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/wsgi.py), and [asgi.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/CoreInventory/asgi.py) will be deleted. [manage.py](file:///c:/Users/Rikin%20Parekh/AntiGravity/CoreInventory/manage.py) will be updated. This is a non-reversible structural change.

> [!NOTE]
> **Local development will use SQLite** — no PostgreSQL or Redis required for dev. The production settings will read `DATABASE_URL` and `REDIS_URL` from environment variables.
