### Wellcreek Restaurant Custom URY ERP

This is the custom app to extend the URY ERP restaurant system to include specific features required by Wellcreek Restaurant.

## Features

### 1. QR Code Table Ordering System (Phase 1 ✅)

A complete self-service ordering solution that **extends URY's native Table doctype** to add:
- **QR Code Generation**: Automatically generates secure QR codes for URY Tables
- **Mobile Menu Browsing**: Responsive interface for customers to browse menu items
- **Direct Ordering**: Customers can place orders from their mobile devices
- **Session Tracking**: Track customer activity and orders per table visit
- **Waiter Call System**: Real-time notifications for customer assistance requests
- **Secure Access**: Token-based authentication for table access

**Key Components:**
- **URY Table Extension**: Custom fields added to URY Table for QR codes and security
- **Customer Sessions**: Track customer activity and orders per table visit
- **Waiter Call System**: Real-time notifications for customer assistance requests
- **Mobile-First Interface**: Responsive design optimized for smartphones
- **Order Integration**: Links orders to URY Tables and customer sessions

### 2. Bill Viewing & M-Pesa Payment (Phase 2 🚧)

Upcoming features:
- **Real-time Bill Display**: View itemized bills with taxes and charges
- **M-Pesa Integration**: STK Push for mobile payments (Safaricom Daraja API)
- **Payment Tracking**: Track payment status and generate receipts
- **Bill Splitting**: Support for multiple payment methods per bill
- **Tip Management**: Add tips to bills

### Documentation

- **[URY Integration Guide](./URY_INTEGRATION_GUIDE.md)** - Detailed integration architecture and setup
- **[QR Ordering User Guide](./QR_ORDERING_GUIDE.md)** - User guide for the QR ordering system

### Installation

**Prerequisites**: URY ERP must be installed first

```bash
# 1. Install URY ERP (if not already installed)
bench get-app https://github.com/ury-erp/ury
bench --site your-site install-app ury

# 2. Install Python dependencies
bench pip install qrcode[pil] Pillow

# 3. Get this app
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/francis450/wellcreek_restaurant_custom_ury_erp --branch develop

# 4. Install the app
bench --site your-site install-app wellcreek_restaurant_custom_ury_erp

# 5. Import fixtures (custom fields)
bench --site your-site import-fixtures

# 6. Restart
bench restart
```

For detailed installation instructions, see [URY_INTEGRATION_GUIDE.md](./URY_INTEGRATION_GUIDE.md)

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/wellcreek_restaurant_custom_ury_erp
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
