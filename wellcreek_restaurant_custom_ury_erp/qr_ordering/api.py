# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_menu_items(category=None, session_token=None):
	"""Get menu items for customer ordering"""
	try:
		# Build filters
		filters = {
			"disabled": 0,
			"is_stock_item": 1
		}

		# Add category filter if provided
		if category:
			filters["item_group"] = category

		# Get items
		items = frappe.get_all(
			"Item",
			filters=filters,
			fields=[
				"name",
				"item_name",
				"item_group",
				"description",
				"image",
				"standard_rate",
				"stock_uom"
			],
			order_by="item_name"
		)

		# Get item categories
		categories = frappe.get_all(
			"Item Group",
			filters={"is_group": 0},
			fields=["name", "item_group_name"],
			order_by="item_group_name"
		)

		return {
			"success": True,
			"items": items,
			"categories": categories
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Menu Items Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def create_customer_order(session_token, table, items, special_instructions=None):
	"""Create an order from customer interface"""
	try:
		# Validate session
		session = frappe.get_doc("Customer Session", {"session_token": session_token})
		if session.status != "Active":
			frappe.throw(_("Session is not active"))

		if not items or len(items) == 0:
			frappe.throw(_("No items in order"))

		# Parse items if it's a JSON string
		if isinstance(items, str):
			import json
			items = json.loads(items)

		# Create Sales Order or Sales Invoice based on URY setup
		# For now, we'll create a Sales Order
		order = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": get_or_create_walk_in_customer(),
			"order_type": "Sales",
			"transaction_date": frappe.utils.today(),
			"delivery_date": frappe.utils.today(),
			"items": [],
			"custom_ury_table": table,
			"custom_session": session.name
		})

		# Add items to order
		total_amount = 0
		for item in items:
			item_code = item.get("item_code")
			qty = item.get("qty", 1)
			rate = item.get("rate") or frappe.db.get_value("Item", item_code, "standard_rate")

			order.append("items", {
				"item_code": item_code,
				"qty": qty,
				"rate": rate,
				"delivery_date": frappe.utils.today()
			})
			total_amount += rate * qty

		# Add special instructions if provided
		if special_instructions:
			order.custom_special_instructions = special_instructions

		order.insert(ignore_permissions=True)
		order.submit()

		# Update session statistics
		session.increment_order_count(total_amount)

		frappe.db.commit()

		return {
			"success": True,
			"order_id": order.name,
			"order_total": total_amount,
			"message": "Order placed successfully"
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Customer Order Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_session_orders(session_token):
	"""Get all orders for a customer session"""
	try:
		session = frappe.get_doc("Customer Session", {"session_token": session_token})

		orders = frappe.get_all(
			"Sales Order",
			filters={"custom_session": session.name},
			fields=["name", "transaction_date", "grand_total", "status", "docstatus"],
			order_by="creation desc"
		)

		# Get order items for each order
		for order in orders:
			order_items = frappe.get_all(
				"Sales Order Item",
				filters={"parent": order.name},
				fields=["item_code", "item_name", "qty", "rate", "amount"]
			)
			order["items"] = order_items

		return {
			"success": True,
			"orders": orders
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Session Orders Error")
		return {"success": False, "message": str(e)}


def get_or_create_walk_in_customer():
	"""Get or create walk-in customer"""
	customer_name = "Walk-In Customer"

	if not frappe.db.exists("Customer", customer_name):
		customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": "Individual",
			"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual",
			"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
		})
		customer.insert(ignore_permissions=True)
		frappe.db.commit()

	return customer_name


@frappe.whitelist(allow_guest=True)
def get_item_details(item_code):
	"""Get detailed information about a menu item"""
	try:
		item = frappe.get_doc("Item", item_code)

		return {
			"success": True,
			"item": {
				"name": item.name,
				"item_name": item.item_name,
				"description": item.description,
				"image": item.image,
				"standard_rate": item.standard_rate,
				"stock_uom": item.stock_uom,
				"item_group": item.item_group
			}
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Item Details Error")
		return {"success": False, "message": str(e)}
