# QR Code Table Ordering System - User Guide

## Overview

The QR Code Table Ordering System extends URY ERP to provide customers with a seamless self-service ordering experience. Customers can scan a QR code at their table to view the menu, place orders, and call for waiter assistance.

## Features

### 1. QR Code Table Management
- Each table has a unique QR code that customers can scan
- QR codes are automatically generated and secured with tokens
- Printable QR codes for easy deployment
- Table status tracking (Available, Occupied, Reserved, Inactive)

### 2. Customer Self-Service Interface
- **Menu Browsing**: View all menu items with images, descriptions, and prices
- **Category Filtering**: Filter items by category for easier navigation
- **Shopping Cart**: Add items, adjust quantities, and review order before placing
- **Order Placement**: Submit orders directly to the kitchen
- **Order History**: View all orders placed during the current session
- **Call Waiter**: Request waiter assistance with reason and optional message

### 3. Session Management
- Automatic session creation when customer scans QR code
- Track customer activity and order history per session
- Session statistics (total orders, amount spent, waiter calls)

### 4. Waiter Call System
- Real-time notifications to waiters
- Track response times
- Call reasons (Assistance Required, Order Inquiry, Bill Request, Complaint, Other)

## Installation

### Prerequisites
- URY ERP installed and configured
- Frappe Framework v15 or higher
- Python 3.10 or higher

### Install Steps

1. **Get the app:**
   ```bash
   cd $PATH_TO_YOUR_BENCH
   bench get-app https://github.com/francis450/wellcreek_restaurant_custom_ury_erp --branch develop
   ```

2. **Install dependencies:**
   ```bash
   bench pip install qrcode[pil] Pillow
   ```

3. **Install the app on your site:**
   ```bash
   bench --site your-site-name install-app wellcreek_restaurant_custom_ury_erp
   ```

   The installation will automatically:
   - Create custom fields on Sales Order
   - Create Restaurant Manager and Waiter roles
   - Set up the QR Ordering workspace

4. **Run migrations (if needed):**
   ```bash
   bench --site your-site-name migrate
   ```

## Setup Guide

### 1. Create Restaurant Tables

1. Navigate to **Restaurant Table** doctype
2. Click **New**
3. Fill in the details:
   - **Table Number**: Unique identifier (e.g., "T1", "T2")
   - **Table Name**: Display name (optional)
   - **Seating Capacity**: Number of seats
   - **Outlet**: Link to warehouse/outlet (optional)
   - **Floor**: Floor or area location (optional)
4. Save the document - QR code will be automatically generated
5. The QR code image will appear in the document

### 2. Print QR Codes

1. Open the Restaurant Table document
2. Print the document or download the QR code image
3. Place the printed QR code on the table

**Pro Tip**: Create laminated table tents with the QR code for durability

### 3. Configure Menu Items

Ensure your menu items in the **Item** master have:
- Clear item names
- Descriptions
- Images
- Standard rates (prices)
- Item groups (categories)

### 4. Set Up User Roles

Assign appropriate roles to your staff:

**Restaurant Manager**:
- Full access to all features
- Can manage tables, sessions, and orders
- Receives waiter call notifications

**Waiter**:
- View tables and sessions
- Manage waiter calls
- View orders

## Usage

### For Customers

1. **Scan QR Code**: Use your phone camera to scan the QR code on your table
2. **Browse Menu**: Explore menu items and categories
3. **Add to Cart**: Select items and adjust quantities
4. **Place Order**: Review your cart and submit the order
5. **Track Orders**: View order status in the "My Orders" tab
6. **Call Waiter**: Tap the floating button to request assistance

### For Staff

#### Managing Tables

1. Go to **Restaurant Table** list
2. View table status (Available, Occupied, Reserved)
3. Edit table details as needed
4. Regenerate QR codes if needed using the "Regenerate QR Code" button

#### Managing Sessions

1. Go to **Customer Session** list
2. View active sessions and their statistics
3. Monitor customer activity
4. Mark sessions as completed when customers leave

#### Handling Waiter Calls

1. Receive real-time notifications when customers call
2. Go to **Waiter Call** list
3. Acknowledge calls to show you're responding
4. Mark calls as resolved after assisting the customer
5. View response time metrics

#### Viewing Orders

1. Orders appear in **Sales Order** list
2. Filter by table or session
3. Process orders through URY POS or kitchen display

## Technical Details

### DocTypes Created

1. **Restaurant Table**
   - Stores table information and QR codes
   - Auto-generates secure QR codes with tokens
   - Tracks table status

2. **Customer Session**
   - Tracks customer visits per table
   - Maintains session statistics
   - Links orders to specific sessions

3. **Waiter Call**
   - Records waiter assistance requests
   - Tracks response times
   - Sends real-time notifications

### API Endpoints

All endpoints are accessible at `/api/method/wellcreek_restaurant_custom_ury_erp.qr_ordering.*`

**Public Endpoints** (guest access):
- `api.get_menu_items` - Fetch menu items
- `api.create_customer_order` - Place an order
- `api.get_session_orders` - Get orders for a session
- `api.get_item_details` - Get item details
- `restaurant_table.validate_table_access` - Validate table token
- `customer_session.get_or_create_session` - Create/resume session
- `waiter_call.create_waiter_call` - Request waiter assistance

**Protected Endpoints** (requires authentication):
- `waiter_call.get_pending_calls` - Get pending waiter calls
- `waiter_call.acknowledge_call` - Acknowledge a call
- `waiter_call.resolve_call` - Mark call as resolved

### Custom Fields Added

**Sales Order**:
- `custom_table` - Links order to table
- `custom_session` - Links order to customer session
- `custom_special_instructions` - Customer notes

### Security Features

- Secure token-based table access
- Session validation for all customer actions
- Guest access limited to specific API endpoints
- Rate limiting recommended for production

## Troubleshooting

### QR Code Not Generating

1. Check if Pillow and qrcode libraries are installed:
   ```bash
   bench pip install qrcode[pil] Pillow
   ```

2. Check error logs:
   ```bash
   bench --site your-site-name console
   frappe.get_all("Error Log", limit=5)
   ```

### Customer Can't Access Menu

1. Verify table token is valid
2. Check if site is accessible from customer's network
3. Ensure guest access is enabled for the site

### Orders Not Appearing

1. Check Sales Order permissions
2. Verify "Walk-In Customer" is created
3. Check custom fields are properly installed:
   - Custom fields should be automatically created during app installation
   - If missing, try reinstalling the app:
   ```bash
   bench --site your-site-name uninstall-app wellcreek_restaurant_custom_ury_erp
   bench --site your-site-name install-app wellcreek_restaurant_custom_ury_erp
   ```

### Waiter Notifications Not Working

1. Ensure SocketIO is running:
   ```bash
   bench --site your-site-name start-socketio
   ```

2. Check Frappe real-time settings

## Customization

### Changing Order Document Type

By default, orders create Sales Orders. To use a different doctype (e.g., Restaurant Order from URY):

1. Edit `qr_ordering/api.py`
2. Modify the `create_customer_order` function
3. Change `doctype: "Sales Order"` to your preferred doctype

### Customizing Menu Display

Edit the template file:
```
wellcreek_restaurant_custom_ury_erp/templates/pages/table-order.html
```

Modify the CSS in the `<style>` section or JavaScript in the `<script>` section.

### Adding Payment Integration

To add payment functionality:

1. Create a payment API endpoint
2. Add payment button to the customer interface
3. Integrate with your payment gateway
4. Update order status after successful payment

## Best Practices

1. **QR Code Placement**: Place QR codes in visible, accessible locations
2. **Menu Maintenance**: Keep menu items updated with accurate prices and images
3. **Session Management**: Regularly close completed sessions
4. **Monitor Calls**: Check waiter call response times to improve service
5. **Regular Backups**: Back up your database regularly

## Support

For issues or feature requests:
- Create an issue on GitHub
- Contact: franciskamande2001@gmail.com

## License

MIT License - See license.txt for details
