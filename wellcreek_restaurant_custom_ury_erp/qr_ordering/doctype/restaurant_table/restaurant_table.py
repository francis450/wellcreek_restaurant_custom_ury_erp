# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import qrcode
import io
import base64
import secrets


class RestaurantTable(Document):
	def before_save(self):
		"""Generate QR code and security token before saving"""
		if not self.security_token:
			self.security_token = secrets.token_urlsafe(32)

		if not self.qr_code or self.has_value_changed("table_number"):
			self.generate_qr_code()

	def generate_qr_code(self):
		"""Generate QR code for the table"""
		# Get site URL
		site_url = frappe.utils.get_url()

		# Create QR code URL with table ID and security token
		qr_url = f"{site_url}/table-order?table={self.name}&token={self.security_token}"
		self.qr_code_url = qr_url

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

		# Save as file
		file_name = f"qr_code_{self.table_number}_{self.name}.png"
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": file_name,
			"attached_to_doctype": self.doctype,
			"attached_to_name": self.name,
			"content": buffer.getvalue(),
			"is_private": 0
		})
		file_doc.save(ignore_permissions=True)

		self.qr_code = file_doc.file_url

	@frappe.whitelist()
	def regenerate_qr_code(self):
		"""Regenerate QR code and security token"""
		self.security_token = secrets.token_urlsafe(32)
		self.generate_qr_code()
		self.save()
		return self.qr_code


@frappe.whitelist(allow_guest=True)
def validate_table_access(table, token):
	"""Validate table access using security token"""
	try:
		table_doc = frappe.get_doc("Restaurant Table", table)
		if table_doc.security_token == token:
			return {
				"valid": True,
				"table_number": table_doc.table_number,
				"table_name": table_doc.table_name,
				"status": table_doc.status
			}
		else:
			return {"valid": False, "message": "Invalid access token"}
	except frappe.DoesNotExistError:
		return {"valid": False, "message": "Table not found"}
