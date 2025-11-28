# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import secrets
from datetime import datetime


class CustomerSession(Document):
	def before_save(self):
		"""Generate session token before saving"""
		if not self.session_token:
			self.session_token = secrets.token_urlsafe(32)

		# Update last activity
		self.last_activity = frappe.utils.now()

	def after_insert(self):
		"""Update table status after session creation"""
		if self.table and self.status == "Active":
			frappe.db.set_value("Restaurant Table", self.table, "status", "Occupied")

	def on_update(self):
		"""Update table status based on session status"""
		if self.has_value_changed("status"):
			if self.status in ["Completed", "Abandoned"]:
				# Check if there are any other active sessions for this table
				active_sessions = frappe.db.count("Customer Session", {
					"table": self.table,
					"status": "Active",
					"name": ["!=", self.name]
				})

				if active_sessions == 0:
					frappe.db.set_value("Restaurant Table", self.table, "status", "Available")

				if self.status == "Completed" and not self.end_time:
					self.end_time = frappe.utils.now()

	def increment_order_count(self, amount=0):
		"""Increment order count and total amount"""
		self.total_orders = (self.total_orders or 0) + 1
		self.total_amount = (self.total_amount or 0) + amount
		self.last_activity = frappe.utils.now()
		self.save(ignore_permissions=True)

	def increment_waiter_calls(self):
		"""Increment waiter call count"""
		self.waiter_calls = (self.waiter_calls or 0) + 1
		self.last_activity = frappe.utils.now()
		self.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def get_or_create_session(table, table_token):
	"""Get existing active session or create a new one"""
	# Validate table access
	table_doc = frappe.get_doc("Restaurant Table", table)
	if table_doc.security_token != table_token:
		frappe.throw("Invalid table access token")

	# Check for existing active session
	existing_sessions = frappe.get_all(
		"Customer Session",
		filters={
			"table": table,
			"status": "Active"
		},
		fields=["name", "session_token", "table_number", "start_time"],
		order_by="creation desc",
		limit=1
	)

	if existing_sessions:
		session = existing_sessions[0]
		# Update last activity
		frappe.db.set_value("Customer Session", session.name, "last_activity", frappe.utils.now())
		frappe.db.commit()
		return session

	# Create new session
	session = frappe.get_doc({
		"doctype": "Customer Session",
		"table": table,
		"status": "Active",
		"start_time": frappe.utils.now()
	})
	session.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"name": session.name,
		"session_token": session.session_token,
		"table_number": session.table_number,
		"start_time": session.start_time
	}


@frappe.whitelist(allow_guest=True)
def validate_session(session_token):
	"""Validate session token and return session details"""
	try:
		session = frappe.get_doc("Customer Session", {"session_token": session_token})
		if session.status == "Active":
			# Update last activity
			frappe.db.set_value("Customer Session", session.name, "last_activity", frappe.utils.now())
			frappe.db.commit()

			return {
				"valid": True,
				"session_name": session.name,
				"table": session.table,
				"table_number": session.table_number,
				"start_time": session.start_time
			}
		else:
			return {"valid": False, "message": "Session is not active"}
	except frappe.DoesNotExistError:
		return {"valid": False, "message": "Invalid session token"}
