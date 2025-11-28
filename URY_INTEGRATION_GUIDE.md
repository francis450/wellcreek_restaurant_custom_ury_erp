# URY Integration Guide

## Overview

This guide explains how the Wellcreek Restaurant Custom App extends URY ERP to add QR code-based table ordering, bill viewing, and M-Pesa payment capabilities.

## Architecture

### Phase 1: URY Table Extension (Completed)

Instead of creating a separate "Restaurant Table" doctype, we now **extend URY's existing Table doctype** using Custom Fields and Document Event Hooks.

#### Custom Fields Added to URY Table

The following custom fields are automatically added to "URY Table" when you install this app:

1. **custom_qr_code** (Attach Image) - Stores the generated QR code image
2. **custom_qr_code_preview** (Image) - Preview of the QR code
3. **custom_qr_code_url** (Small Text) - The URL encoded in the QR code
4. **custom_security_token** (Data, Hidden) - Secure token for table access validation
5. **custom_online_ordering_enabled** (Check) - Enable/disable online ordering per table

#### Document Event Hooks

When a URY Table is saved:
- A unique security token is generated (if not exists)
- A QR code is automatically generated with the table's URL
- The QR code image is saved and attached to the table record

#### Integration Points

**Customer Session Doctype**
- Links to "URY Table" instead of separate "Restaurant Table"
- Tracks customer activity per table visit
- Updates URY Table status (Occupied/Available) based on session state

**Waiter Call Doctype**
- References "URY Table" for waiter assistance requests
- Maintains compatibility with URY's table management

**Sales Order Integration**
- Adds `custom_ury_table` field to link orders to URY Tables
- Adds `custom_session` field to track customer sessions
- Adds `custom_special_instructions` field for customer notes

## Installation Instructions

### Prerequisites

1. **URY ERP must be installed first**
   ```bash
   # Install URY ERP
   bench get-app https://github.com/ury-erp/ury
   bench --site your-site install-app ury
   ```

2. **Python dependencies**
   ```bash
   bench pip install qrcode[pil] Pillow
   ```

### Installation Steps

1. **Get the Wellcreek custom app**
   ```bash
   cd /path/to/frappe-bench
   bench get-app https://github.com/francis450/wellcreek_restaurant_custom_ury_erp --branch develop
   ```

2. **Install the app on your site**
   ```bash
   bench --site your-site install-app wellcreek_restaurant_custom_ury_erp
   ```

3. **Run migrations to create custom fields**
   ```bash
   bench --site your-site migrate
   ```

4. **Import fixtures to add custom fields**
   ```bash
   bench --site your-site import-fixtures
   ```

5. **Restart bench**
   ```bash
   bench restart
   ```

## Usage

### 1. Enable Online Ordering for Tables

1. Navigate to **URY Table** list in your ERPNext instance
2. Open any table you want to enable for online ordering
3. Check the **Enable Online Ordering** checkbox
4. Save the document
5. A QR code will be automatically generated
6. Print or download the QR code from the **QR Code Preview** field

### 2. Customer Experience

When customers scan the QR code:
1. They're redirected to `/table-order?table={table_id}&token={security_token}`
2. A customer session is automatically created or resumed
3. They can browse the menu, add items to cart, and place orders
4. They can view their order history
5. They can call for waiter assistance

### 3. Staff Management

**Viewing Active Sessions**
- Go to **Customer Session** list
- Filter by "Status = Active" to see current dining sessions
- View session statistics (orders placed, amount spent, waiter calls)

**Handling Waiter Calls**
- Go to **Waiter Call** list
- View pending calls in real-time
- Acknowledge and resolve customer requests
- Track response times

**Viewing Orders**
- Orders appear in **Sales Order** list
- Filter by `custom_ury_table` to see orders per table
- Filter by `custom_session` to see orders per dining session

## API Endpoints

All endpoints are whitelisted for guest access where appropriate:

### Public Endpoints (Guest Access)

```python
# Get menu items
frappe.call('wellcreek_restaurant_custom_ury_erp.qr_ordering.api.get_menu_items', {
    category: 'Optional category filter',
    session_token: 'Session token'
})

# Create order
frappe.call('wellcreek_restaurant_custom_ury_erp.qr_ordering.api.create_customer_order', {
    session_token: 'Session token',
    table: 'URY Table ID',
    items: [{item_code: 'ITEM-001', qty: 2, rate: 100}],
    special_instructions: 'Optional notes'
})

# Get session orders
frappe.call('wellcreek_restaurant_custom_ury_erp.qr_ordering.api.get_session_orders', {
    session_token: 'Session token'
})

# Call waiter
frappe.call('wellcreek_restaurant_custom_ury_erp.qr_ordering.doctype.waiter_call.waiter_call.create_waiter_call', {
    session_token: 'Session token',
    table: 'URY Table ID',
    call_reason: 'Assistance Required',
    customer_message: 'Optional message'
})

# Validate table access
frappe.call('wellcreek_restaurant_custom_ury_erp.overrides.ury_table.validate_table_access', {
    table: 'URY Table ID',
    token: 'Security token from QR code'
})
```

### Protected Endpoints (Requires Authentication)

```python
# Get pending waiter calls
frappe.call('wellcreek_restaurant_custom_ury_erp.qr_ordering.doctype.waiter_call.waiter_call.get_pending_calls')

# Regenerate QR code for a table
frappe.call('wellcreek_restaurant_custom_ury_erp.overrides.ury_table.regenerate_qr_code', {
    table_name: 'URY Table ID'
})
```

## Security Features

1. **Token-based Access Control**
   - Each table has a unique, secure token (32-byte URL-safe)
   - Tokens are validated on every customer request
   - Invalid tokens are rejected with appropriate error messages

2. **Session Management**
   - Each customer visit creates a unique session
   - Sessions track all orders and activities
   - Sessions expire when marked as "Completed" or "Abandoned"

3. **Guest Access Restrictions**
   - Only specific API endpoints allow guest access
   - All customer actions require valid session tokens
   - Table access requires both table ID and security token

## Customization

### Changing Order Doctype

By default, orders create **Sales Orders**. To use URY's Restaurant Order or POS Invoice:

1. Edit `qr_ordering/api.py`
2. Modify the `create_customer_order` function:

```python
# Change from:
order = frappe.get_doc({
    "doctype": "Sales Order",
    ...
})

# To:
order = frappe.get_doc({
    "doctype": "Restaurant Order",  # or "POS Invoice"
    ...
})
```

3. Update field names as per the target doctype's schema

### Customizing the Customer Interface

Edit `/templates/pages/table-order.html` to modify:
- Layout and styling (CSS in `<style>` section)
- Functionality (JavaScript in `<script>` section)
- UI elements (HTML in `{% block page_content %}`)

### Adding Custom Fields to Orders

Edit `fixtures/custom_field.json` to add more custom fields to Sales Order or other doctypes.

## Troubleshooting

### QR Codes Not Generating

**Issue**: Custom fields not visible or QR code not generating

**Solution**:
```bash
bench --site your-site migrate
bench --site your-site import-fixtures
bench restart
```

### "URY Table not found" Error

**Issue**: URY ERP not installed or table doctype has different name

**Solution**:
1. Verify URY is installed: `bench --site your-site list-apps`
2. Check table doctype name in URY
3. Update references in code if needed

### Orders Not Creating

**Issue**: Sales Order creation fails

**Solution**:
1. Ensure "Walk-In Customer" exists
2. Check Sales Order permissions
3. Verify custom fields are imported: `bench --site your-site import-fixtures`

### Session Validation Failing

**Issue**: Customers can't access menu after scanning QR code

**Solution**:
1. Check if online ordering is enabled for the table
2. Verify security token is valid
3. Check guest access is enabled for the site
4. Review error logs: `bench --site your-site logs`

## Phase 2: Bill Viewing & M-Pesa Payment (Upcoming)

The next phase will add:
1. **Bill Viewing Interface** - Real-time bill calculation and display
2. **M-Pesa Integration** - STK Push payment processing
3. **Payment Tracking** - Payment status and receipt generation
4. **Bill Splitting** - Multiple payment methods per bill

## Support

For issues or questions:
- **GitHub**: https://github.com/francis450/wellcreek_restaurant_custom_ury_erp
- **Email**: franciskamande2001@gmail.com

## References

- [URY ERP Documentation](https://ury.app/docs/)
- [URY GitHub Repository](https://github.com/ury-erp/ury)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com/)
