### Wellcreek Restaurant Custom URY ERP

This is the custom app to extend the URY ERP restaurant system to include specific features required by Wellcreek Restaurant.

## Features

### 1. QR Code Table Ordering System

A complete self-service ordering solution that allows customers to:
- Scan QR codes at their table to access the menu
- Browse menu items with images, descriptions, and prices
- Place orders directly from their mobile devices
- Track order status in real-time
- Call for waiter assistance with a single tap
- View order history for their dining session

**Key Components:**
- **Restaurant Table Management**: Create tables with auto-generated QR codes
- **Customer Sessions**: Track customer activity and orders per table visit
- **Waiter Call System**: Real-time notifications for customer assistance requests
- **Mobile-First Interface**: Responsive design optimized for smartphones
- **Secure Access**: Token-based authentication for table access

For detailed setup and usage instructions, see [QR_ORDERING_GUIDE.md](./QR_ORDERING_GUIDE.md)

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app wellcreek_restaurant_custom_ury_erp
```

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
