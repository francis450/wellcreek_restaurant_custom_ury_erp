# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe


def get_context(context):
	"""Get context for table order page"""
	context.no_cache = 1

	# Initialize context variables to prevent template errors
	context.table = None
	context.table_name = None
	context.table_number = None
	context.session_token = None
	context.session_name = None
	context.error = None
	context.currency = frappe.defaults.get_global_default("currency") or "KSh"

	# Get table and token from query parameters
	table = frappe.form_dict.get("table")
	token = frappe.form_dict.get("token")

	if not table or not token:
		context.error = "Invalid QR code. Please scan again."
		return context

	# Validate table access
	try:
		# Use the validation function from overrides
		from wellcreek_restaurant_custom_ury_erp.overrides.ury_table import validate_table_access

		validation = validate_table_access(table, token)
		if not validation.get("valid"):
			context.error = validation.get("message", "Invalid access token. Please scan the correct QR code.")
			return context

		# Get table details
		table_doc = frappe.get_doc("URY Table", table)

		# Get or create session
		from wellcreek_restaurant_custom_ury_erp.qr_ordering.doctype.customer_session.customer_session import get_or_create_session

		session = get_or_create_session(table, token)

		# Debug logging
		frappe.logger().info(f"Table: {table}, Session: {session}")

		# Set context variables
		context.table = table
		context.table_number = table_doc.name
		context.table_name = table_doc.get("table_name") or table_doc.name
		context.session_token = session.get("session_token") or session.get("session_token")
		context.session_name = session.get("name")

		# Log successful context setup
		frappe.logger().info(f"Context set - Table: {context.table_name}, Session: {context.session_name}")

	except frappe.DoesNotExistError as e:
		frappe.log_error(f"Table not found: {table}\n{frappe.get_traceback()}", "Table Order Page - Table Not Found")
		context.error = "Table not found. Please contact staff."
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Table Order Page Error")
		context.error = f"An error occurred: {str(e)}. Please contact staff."

	return context
