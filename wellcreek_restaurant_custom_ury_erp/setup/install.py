# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	"""Create custom fields after app installation"""
	create_qr_ordering_custom_fields()
	create_roles()


def create_qr_ordering_custom_fields():
	"""Create custom fields for QR ordering system"""
	custom_fields = {
		"Sales Order": [
			{
				"fieldname": "custom_table",
				"label": "Table",
				"fieldtype": "Link",
				"options": "Restaurant Table",
				"insert_after": "customer",
				"read_only": 1,
			},
			{
				"fieldname": "custom_session",
				"label": "Customer Session",
				"fieldtype": "Link",
				"options": "Customer Session",
				"insert_after": "custom_table",
				"read_only": 1,
			},
			{
				"fieldname": "custom_special_instructions",
				"label": "Special Instructions",
				"fieldtype": "Text",
				"insert_after": "custom_session",
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()


def create_roles():
	"""Create roles for QR ordering system"""
	roles = [
		{
			"role_name": "Restaurant Manager",
			"desk_access": 1,
		},
		{
			"role_name": "Waiter",
			"desk_access": 1,
		},
	]

	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.get_doc({"doctype": "Role", **role_data})
			role.insert(ignore_permissions=True)

	frappe.db.commit()
