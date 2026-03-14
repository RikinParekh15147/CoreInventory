# CoreInventory: Smart Inventory Management System

**CoreInventory** is a comprehensive and intelligently structured inventory management application designed to streamline internal operations, track stock movements, and optimize warehouse performance. 

By mapping real-world physical stock adjustments, receipts, and deliveries to a digital ledger, CoreInventory provides businesses with total visibility and control over their supply chain operations from a single centralized dashboard.

---

## 🚀 How CoreInventory Helps You

Running a warehouse without dedicated software leads to misplaced stock, unfulfilled orders, and lost revenue. CoreInventory helps managers and workers:
- **Prevent Stockouts & Overstocking:** Proactive low-stock alerts and tracking mechanisms.
- **Maintain Accurate Ledgers:** Every movement—from vendor receipt to customer delivery—is securely logged automatically.
- **Save Time with Smart Navigation:** Search by SKU, dynamic filters by document type or status, and dedicated product categories allow instant data retrieval.
- **Organize Multiple Locations:** Efficiently manage complex, multi-warehouse ecosystems and internal goods movement without manual spreadsheets.

---

## 🔒 Authentication & Security

A fast, secure, and intuitive onboarding process ensures only authorized personnel can access business-critical operations.
- **User Registration & Login:** Direct authentication mechanism.
- **OTP-Based Password Reset:** Secure password recovery using One-Time Passwords.
- **Immediate Dashboard Access:** Post-login redirection straight into the operational hub.

---

## 📊 Dashboard View & KPIs

The landing page acts as the operational nerve center, providing a high-level snapshot of current inventory health.

### Key Performance Indicators (KPIs)
- **Total Products in Stock:** Real-time visibility of aggregate inventory.
- **Low Stock & Out of Stock:** Immediate alerts for critical inventory depletion.
- **Pending Receipts:** Awaiting vendor deliveries.
- **Pending Deliveries:** Awaiting outbound shipments to customers.
- **Internal Transfers Scheduled:** Overview of domestic stock movement.

### Dynamic Smart Filters
Quickly sort and find operational data via robust filtering:
- **By Document Type:** Receipts / Delivery / Internal / Adjustments
- **By Status:** Draft, Waiting, Ready, Done, Canceled
- **By Location/Warehouse:** Pinpoint stock across different geographical buildings.
- **By Product Category:** Filter items based on organizational classifications.

---

## 🗺️ Navigation & Interface Structure

The system is logically divided to reduce operational friction.

### 1. Products
- **Creation & Management:** Register new or edit existing products.
- **Location Mapping:** Check exact stock availability per isolated bin/location.
- **Categorization:** Group products logically.
- **Reordering Rules:** Automate stock replenishment limits.

### 2. Operations Hub
- **Receipts:** Manage incoming stock from vendors.
- **Delivery Orders:** Manage outbound stock to clients.
- **Internal Transfers:** Manage stock shifting across internal warehouse zones.
- **Inventory Adjustments:** Reconcile system records with physical audits.
- **Move History & Ledger:** Unalterable audit log of every item that moved.

### 3. Settings & Configuration
- **Warehouse Setup:** Define building names and internal storage bins to map out the physical architecture electronically.

### 4. Profile Menu
- **My Profile & Settings**
- **System Logout**

---

## 🛠️ Core Features In-Depth

### 1. Product Management Master
Easily create robust product profiles encompassing:
- Name and description
- Unique SKU / Codes
- Organizational Category
- Unit of Measure (liters, pieces, kg, etc.)
- Initial stock configurations

### 2. Receipts (Incoming Stock Flow)
Used securely when shipments arrive from suppliers.
**The Flow:**
1. Create a new digital receipt.
2. Link the supplier and select incoming product lines.
3. Input received quantities accurately.
4. Validate the receipt → **System automatically increases available stock.**
> *Example:* You receive a shipment of 50 units of "Steel Rods". Upon validation, your digital stock level instantly augments to +50.

### 3. Delivery Orders (Outgoing Stock Flow)
Critical for ensuring customer sales orders are fulfilled efficiently.
**The Flow:**
1. Pick the requested items from their bin locations.
2. Pack the order for shipment.
3. Validate the delivery → **System automatically decreases available stock.**
> *Example:* A sales order is processed for 10 office chairs. When the delivery order is validated, the available stock for chairs immediately reduces by 10.

### 4. Internal Transfers
Operate gracefully across complex enterprise domains by transferring stock without altering total net company stock.
**Common Scenarios:**
- Main Warehouse → Production Floor
- Rack A → Rack B
- Warehouse Building 1 → Warehouse Building 2
> *Each specific internal movement is strictly logged in the audit ledger.*

### 5. Stock Adjustments (Physical Reconciliations)
Occasionally, digital records misalign with reality due to damage, shrinkage, or counting errors. Adjustments fix these mismatches easily.
**The Flow:**
1. Select the specific product and physical location.
2. Enter the absolute counted physical quantity.
3. The system automatically computes the difference, logs the adjustment reason, and updates the core ledger.

### 6. Additional Integrated Features
- **Low Stock Alarms:** Never run out of your best-selling or critical-path items.
- **Multi-Warehouse Support:** Infinitely scalable physical architectures.
- **Deep Search:** Smart SKU mapping allows scanning to instantly pull up product data.

---

## 📘 Simplified Example: Understanding the Supply Flow

Here is exactly how CoreInventory effortlessly handles day-to-day warehouse operations natively:

- **Step 1: Receive Goods**
  - Scenario: A vendor delivers 100 kg of Steel to the receiving dock.
  - Action: Validate Receipt. 
  - Result: *Stock becomes +100 kg.*
- **Step 2: Stage for Production**
  - Scenario: The Steel must be moved from the dock to the cutting floor.
  - Action: Validate Internal Transfer (Main Store → Production Rack). 
  - Result: *Total stock is unchanged, but the digital location map is instantly updated.*
- **Step 3: Fulfill Customer Sales**
  - Scenario: Customer buys manufactured steel frames utilizing 20 kg of steel.
  - Action: Validate Delivery Order. 
  - Result: *Stock reduces by -20 kg.*
- **Step 4: Audit & Shrinkage**
  - Scenario: A forklift operator accidentally damages 3 kg of steel.
  - Action: Execute Stock Adjustment. 
  - Result: *Stock reduces by -3 kg.*

*Every single action in this 4-step real-world flow is immutably documented inside the **Stock Ledger**, providing perfect clarity for auditors and management.*
