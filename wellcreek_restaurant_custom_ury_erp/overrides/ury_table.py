# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
import qrcode
import io
import base64
import secrets


def generate_qr_code(doc, method=None):
	"""
	Generate QR code for URY Table
	This function is called via document event hook
	"""
	# Only generate if online ordering is enabled
	if not doc.get("custom_online_ordering_enabled"):
		return

	# Generate security token if not exists
	if not doc.get("custom_security_token"):
		doc.custom_security_token = secrets.token_urlsafe(32)

	# Generate QR code if not exists or table number changed
	if not doc.get("custom_qr_code") or doc.has_value_changed("name"):
		_create_qr_code(doc)


def _create_qr_code(doc):
	"""Create QR code image and save it"""
	# Get site URL
	site_url = frappe.utils.get_url()

	# Create QR code URL with table ID and security token
	qr_url = f"{site_url}/table-order?table={doc.name}&token={doc.custom_security_token}"
	doc.custom_qr_code_url = qr_url

	# Generate QR code image
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(qr_url)
	qr.make(fit=True)

	# Create image
	img = qr.make_image(fill_color="black", back_color="white")

	# Save to BytesIO
	buffer = io.BytesIO()
	img.save(buffer, format='PNG')
	buffer.seek(0)

	# Convert to base64
	img_base64 = base64.b64encode(buffer.getvalue()).decode()

	# Delete old QR code file if exists
	if doc.get("custom_qr_code"):
		try:
			old_file = frappe.get_doc("File", {"file_url": doc.custom_qr_code})
			old_file.delete()
		except:
			pass

	# Save as file
	file_name = f"qr_code_table_{doc.name}.png"
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": file_name,
		"attached_to_doctype": doc.doctype,
		"attached_to_name": doc.name,
		"content": buffer.getvalue(),
		"is_private": 0
	})
	file_doc.save(ignore_permissions=True)

	doc.custom_qr_code = file_doc.file_url


@frappe.whitelist()
def regenerate_qr_code(table_name):
	"""Regenerate QR code for a specific table"""
	doc = frappe.get_doc("URY Table", table_name)
	doc.custom_security_token = secrets.token_urlsafe(32)
	_create_qr_code(doc)
	doc.save(ignore_permissions=True)
	return {
		"success": True,
		"qr_code": doc.custom_qr_code,
		"qr_code_url": doc.custom_qr_code_url
	}


@frappe.whitelist(allow_guest=True)
def validate_table_access(table, token):
	"""Validate table access using security token"""
	try:
		# Try to get URY Table
		table_doc = frappe.get_doc("URY Table", table)

		# Check if online ordering is enabled
		if not table_doc.get("custom_online_ordering_enabled"):
			return {
				"valid": False,
				"message": "Online ordering is not enabled for this table"
			}

		# Validate security token
		if table_doc.get("custom_security_token") == token:
			return {
				"valid": True,
				"table_name": table_doc.name,
				"status": table_doc.status if hasattr(table_doc, 'status') else "Available"
			}
		else:
			return {"valid": False, "message": "Invalid access token"}
	except frappe.DoesNotExistError:
		return {"valid": False, "message": "Table not found"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Validate Table Access Error")
		return {"valid": False, "message": str(e)}
