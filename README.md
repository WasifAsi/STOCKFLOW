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
├── manage.py                # Django project launcher
├── requirements.txt         # Python dependencies
├── db.sqlite3              # Local database (auto-created)
├── stockflow/              # Main Django configuration
│   ├── settings.py         # Settings and app registration
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── apps/
│   ├── accounts/           # User authentication and roles
│   │   ├── models.py       # Custom User model with Role field
│   │   ├── views.py        # Login/logout views
│   │   ├── admin.py        # User admin interface
│   │   └── urls.py         # Auth URLs
│   └── inventory/          # Core inventory app
│       ├── models.py       # Warehouse, Product, StockLevel, StockTransfer, StockMovement
│       ├── views.py        # Dashboard, product list, warehouse list, transfers
│       ├── admin.py        # Model admin interfaces
│       └── urls.py         # Inventory URLs
├── templates/              # HTML templates
│   ├── base.html           # Base layout template
│   ├── registration/       # Login template
│   └── inventory/          # Dashboard, product, warehouse, transfer templates
└── static/
    └── css/
        └── app.css         # Global stylesheet
```

## Quick Launch

### For Windows (Easiest)
1. Open File Explorer and navigate to the STOCKFLOW folder
2. **Double-click `run.bat`** — This automatically handles everything:
   - Creates a virtual environment
   - Installs dependencies
   - Sets up the database
   - Creates an admin user (if needed)
   - Opens the dashboard in your browser

### For macOS / Linux
1. Open Terminal and navigate to the STOCKFLOW folder:
   ```bash
   cd path/to/STOCKFLOW
   ```
2. Run the launcher:
   ```bash
   python run.py
   ```

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

## Quick Start

### First-Time Setup in Django Admin

1. Log in to the admin panel at `/admin/`.
2. Create at least one **Warehouse** with a unique code (e.g., `WH001`).
3. Create **Categories** (e.g., Electronics, Consumables).
4. Create **Suppliers** (optional, but helpful for purchase tracking).
5. Add **Products** linked to categories with SKUs and reorder points.
6. Populate **Stock Levels** for each product in each warehouse.

### Dashboard Overview

The dashboard displays:
- Warehouse, product, transfer, and movement counts
- Low-stock alerts (items at or below reorder point)
- Recent stock movements with timestamps and performers
- Pending transfer queue with status

### User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, all operations |
| **Manager** | Approve transfers, view all data, create movements |
| **Staff** | Create transfers and movements, view inventory |
| **Viewer** | View-only access to dashboard and data |

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

## Development

### Running Tests

To set up a test suite, create a `tests.py` file in each app and run:
```bash
python manage.py test
```

### Making Database Changes

After modifying models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating a Superuser (Admin)

```bash
python manage.py createsuperuser
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
