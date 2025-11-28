# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe


def get_context(context):
	"""Get context for table order page"""
	context.no_cache = 1

	# Get table and token from query parameters
	table = frappe.form_dict.get("table")
	token = frappe.form_dict.get("token")

	if not table or not token:
		context.error = "Invalid QR code. Please scan again."
		return context

	# Validate table access
	try:
		table_doc = frappe.get_doc("Restaurant Table", table)

		if table_doc.security_token != token:
			context.error = "Invalid access token. Please scan the correct QR code."
			return context

		# Get or create session
		from wellcreek_restaurant_custom_ury_erp.qr_ordering.doctype.customer_session.customer_session import get_or_create_session

		session = get_or_create_session(table, token)

		# Set context variables
		context.table = table
		context.table_number = table_doc.table_number
		context.table_name = table_doc.table_name or f"Table {table_doc.table_number}"
		context.session_token = session.get("session_token")
		context.session_name = session.get("name")

	except frappe.DoesNotExistError:
		context.error = "Table not found. Please contact staff."
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Table Order Page Error")
		context.error = "An error occurred. Please contact staff."

	return context
