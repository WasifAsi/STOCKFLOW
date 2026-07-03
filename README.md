# STOCKFLOW

**Open-source offline multi-warehouse inventory management system built with Django.**

StockFlow is a self-hosted, self-contained inventory control system designed for teams managing stock across multiple warehouses without external dependencies. Built on Django, it runs locally and stores all data in a portable SQLite database.

## Features

- **Multi-warehouse stock tracking** — Track inventory levels, reserved quantities, and available stock across all warehouses in one system.
- **Role-based access control** — Four user roles (Admin, Manager, Staff, Viewer) with tailored access permissions.
- **Stock transfers** — Request, approve, and track inter-warehouse transfers with full audit trails.
- **Stock movements** — Log receipts, issues, and adjustments with timestamps and performed-by tracking.
- **Low-stock alerts** — Dashboard highlights products at or below reorder points.
- **Product catalog** — Organize products by category, link to suppliers, and set unit types and reorder thresholds.
- **Django admin** — Full administrative interface for data management and user administration.
- **Offline-first** — Works without internet; all data stored locally.

## Project Structure

```
STOCKFLOW/
├── run.bat                 # Windows launcher (double-click to start)
├── run.py                  # macOS/Linux launcher (python run.py)
├── manage.py               # Django project launcher
├── requirements.txt        # Python dependencies (Django)
├── README.md               # This file
├── LICENSE                 # MIT License
├── db.sqlite3              # Local database (auto-created after first run)
├── venv/                   # Virtual environment (auto-created by launchers)
├── stockflow/              # Main Django configuration
│   ├── __init__.py         # Package marker
│   ├── settings.py         # Settings and app registration
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── apps/                   # Django applications
│   ├── accounts/           # User authentication and roles
│   │   ├── __init__.py
│   │   ├── models.py       # Custom User model with Role field (ADMIN/MANAGER/STAFF/VIEWER)
│   │   ├── views.py        # Login/logout views
│   │   ├── admin.py        # User admin interface
│   │   ├── urls.py         # Authentication URLs
│   │   └── migrations/     # Database migration files
│   └── inventory/          # Core inventory app
│       ├── __init__.py
│       ├── models.py       # Warehouse, Product, Category, Supplier, StockLevel, StockTransfer, StockMovement
│       ├── views.py        # Dashboard, product list, warehouse list, transfer list
│       ├── admin.py        # Model admin interfaces
│       ├── urls.py         # Inventory URLs
│       └── migrations/     # Database migration files
├── templates/              # HTML templates
│   ├── base.html           # Base layout template
│   ├── registration/       # Login/logout templates
│   │   └── login.html      # Login page
│   └── inventory/          # Dashboard and inventory templates
│       ├── dashboard.html  # Main dashboard with metrics and alerts
│       ├── product_list.html
│       ├── warehouse_list.html
│       └── transfer_list.html
└── static/                 # Static files (CSS, images, JavaScript)
    └── css/
        └── app.css         # Global stylesheet with responsive design
```

## Quick Launch

### Windows Users
**Easiest way:** Open File Explorer, navigate to the STOCKFLOW folder, and **double-click `run.bat`**.

The batch file automatically:
- ✓ Detects Python installation
- ✓ Creates a virtual environment (first run only)
- ✓ Installs Django and dependencies
- ✓ Applies database migrations
- ✓ Creates an admin account (prompts only on first run)
- ✓ Opens http://127.0.0.1:8000 in your browser
- ✓ Starts the development server

### macOS / Linux Users
1. Open Terminal and navigate to the folder:
   ```bash
   cd path/to/STOCKFLOW
   ```
2. Run the launcher:
   ```bash
   python run.py
   ```

The Python script does the same automated setup as the batch file.

### First Time Running
On your first run, you'll be prompted to create an admin account. Enter:
- **Username:** Any username you like
- **Email:** Your email address
- **Password:** A secure password
- **Role:** Select `ADMIN` for full access

After setup completes, your browser will open to the dashboard at **http://127.0.0.1:8000/**. Log in with the admin credentials you just created.

---

## Installation

### Prerequisites

- Python 3.11+
- pip (Python package installer)

### Manual Setup

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url> STOCKFLOW
   cd STOCKFLOW
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create an admin user:**
   ```bash
   python manage.py createsuperuser
   ```
   Enter a username, email, password, and select a role (ADMIN recommended for first user).

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Dashboard: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Quick Start Guide

### Step 1: Set Up Your Inventory Data

After your first login, go to the **Admin Panel** (`http://127.0.0.1:8000/admin/`) to set up your inventory:

1. **Create Warehouses**
   - Click "Warehouses" → "Add Warehouse"
   - Enter name (e.g., "Main Warehouse") and code (e.g., "WH001")
   - Assign a manager (optional)
   - Click Save

2. **Create Categories**
   - Click "Categories" → "Add Category"
   - Examples: Electronics, Consumables, Raw Materials

3. **Create Suppliers** (optional but recommended)
   - Click "Suppliers" → "Add Supplier"
   - Add contact information for tracking purchases

4. **Add Products**
   - Click "Products" → "Add Product"
   - Enter SKU (unique identifier), name, category, unit type (pcs, kg, etc.)
   - Set a reorder point (threshold for low-stock alerts)
   - Link to a supplier if applicable

5. **Set Stock Levels**
   - Click "Stock Levels" → "Add Stock Level"
   - Select product and warehouse
   - Enter current quantity on hand

### Step 2: Explore the Dashboard

Once you've added data, view the main dashboard (`http://127.0.0.1:8000/`):

**Metrics Section**
- Total warehouses, products, transfers, and stock movements

**Low Stock Alerts**
- Products at or below their reorder point
- Helps you identify what needs reordering

**Recent Movements**
- Latest stock receipts, issues, and adjustments
- Shows who performed each movement and when

**Transfer Queue**
- Pending inter-warehouse transfers
- Track status: Requested → Approved → In Transit → Received

### Step 3: Record Stock Movements

Click "Transfers" to:
- **Request a transfer** — Send stock from one warehouse to another
- **View pending transfers** — Managers can approve or reject
- **Track completed transfers** — Full audit trail with timestamps

### User Roles & Permissions

| Role | Dashboard | Admin Panel | Create Transfer | Approve Transfer | Create Movement |
|------|-----------|-------------|-----------------|------------------|------------------|
| **Admin** | ✓ | ✓ (Full) | ✓ | ✓ | ✓ |
| **Manager** | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Staff** | ✓ | ✗ | ✓ | ✗ | ✓ |
| **Viewer** | ✓ | ✗ | ✗ | ✗ | ✗ |

## Database Schema

### Core Models

**User** (Custom)
- Extends Django's AbstractUser
- Fields: `username`, `email`, `password`, `first_name`, `last_name`, `role` (ADMIN/MANAGER/STAFF/VIEWER), `phone`

**Warehouse**
- `name` — Unique warehouse name
- `code` — Short warehouse code (e.g., WH001)
- `location` — Geographic location or address
- `manager` — ForeignKey to User
- `is_active` — Boolean flag for soft deletion

**Product**
- `sku` — Unique stock keeping unit
- `name` — Product name
- `category` — ForeignKey to Category
- `supplier` — ForeignKey to Supplier (optional)
- `unit` — Unit type (pcs, kg, liters, etc.)
- `reorder_point` — Quantity at which low-stock alert triggers
- `is_active` — Boolean flag

**Category**
- `name` — Unique category name
- `description` — Optional description

**Supplier**
- `name` — Unique supplier name
- `contact_name`, `email`, `phone` — Contact information
- `address` — Supplier address

**StockLevel**
- `product` — ForeignKey to Product
- `warehouse` — ForeignKey to Warehouse
- `quantity` — Current quantity on hand
- `reserved_quantity` — Quantity reserved for pending transfers
- `available_quantity` — Computed property: `quantity - reserved_quantity`

**StockTransfer**
- `reference` — Unique transfer reference number
- `product` — ForeignKey to Product
- `quantity` — Amount being transferred
- `from_warehouse`, `to_warehouse` — ForeignKey to Warehouse
- `requested_by`, `approved_by` — ForeignKey to User
- `status` — REQUESTED, APPROVED, IN_TRANSIT, RECEIVED, CANCELLED
- `notes` — Optional transfer notes
- `completed_at` — Timestamp when transfer finalized

**StockMovement**
- `movement_type` — RECEIPT, ISSUE, TRANSFER_IN, TRANSFER_OUT, ADJUSTMENT
- `product` — ForeignKey to Product
- `warehouse` — ForeignKey to Warehouse
- `quantity` — Positive or negative quantity
- `reference` — External reference (PO number, issue ticket, etc.)
- `notes` — Optional notes
- `transfer` — Optional link to related StockTransfer
- `performed_by` — ForeignKey to User

## Development & Administration

### Managing Users

**Add a new user:**
```bash
python manage.py createsuperuser  # For admin users
```
Or use the Admin Panel → Users → Add User

### Database Backups

Your data is stored in `db.sqlite3`. To backup:
1. Stop the server (press CTRL+C)
2. Copy `db.sqlite3` to a safe location
3. Restart with the launcher

To restore, replace `db.sqlite3` with your backup and restart.

### Making Code Changes

If you modify Django models:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Running Tests

To test the system:
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run tests
python manage.py test
```

## Planned Enhancements

- **Setup wizard** — First-run configuration workflow
- **Forms and workflows** — Product receiving, issuing, transfer workflows
- **Reporting** — Stock reports, movement history, transfer audits
- **Search & filters** — Advanced search, date range filters, status filters
- **Print-friendly views** — Stock cards, transfer documents, inventory sheets
- **Export** — CSV and PDF export for inventory reports
- **Barcode scanning** — Integration with barcode readers for faster stock capture
- **API** — REST API for mobile apps or external integrations

## Configuration

Key settings in `stockflow/settings.py`:
- `DEBUG = True` — Set to `False` for production
- `SECRET_KEY` — Change before deployment
- `ALLOWED_HOSTS` — Add domain names for production
- `DATABASES` — Configure PostgreSQL or MySQL for production instead of SQLite

## Troubleshooting

### "No module named 'django'"
Ensure your virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port 8000 is already in use
Use a different port:
```bash
python manage.py runserver 8001
```

### Migrations not applying
Clear and reapply migrations:
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## Support

For issues, questions, or feature requests, please open an issue on the repository.
