# Copyright (c) 2025, Njoroge Francis and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class WaiterCall(Document):
	def on_update(self):
		"""Calculate response time when status changes"""
		if self.has_value_changed("status"):
			if self.status == "Acknowledged" and not self.acknowledged_time:
				self.acknowledged_time = frappe.utils.now()
				self.calculate_response_time()

			elif self.status == "Resolved" and not self.resolved_time:
				self.resolved_time = frappe.utils.now()
				self.calculate_response_time()

	def calculate_response_time(self):
		"""Calculate response time in minutes"""
		if self.acknowledged_time and self.call_time:
			call_time = frappe.utils.get_datetime(self.call_time)
			ack_time = frappe.utils.get_datetime(self.acknowledged_time)
			time_diff = ack_time - call_time
			self.response_time_minutes = time_diff.total_seconds() / 60

	def after_insert(self):
		"""Send real-time notification to waiters after creating a call"""
		self.send_waiter_notification()

	def send_waiter_notification(self):
		"""Send real-time notification using Frappe's publish_realtime"""
		frappe.publish_realtime(
			event="waiter_call",
			message={
				"call_id": self.name,
				"table": self.table,
				"table_number": self.table_number,
				"call_time": self.call_time,
				"call_reason": self.call_reason,
				"customer_message": self.customer_message
			},
			user="Restaurant Manager"  # Send to all users with Restaurant Manager role
		)

		# Also send to Waiter role
		frappe.publish_realtime(
			event="waiter_call",
			message={
				"call_id": self.name,
				"table": self.table,
				"table_number": self.table_number,
				"call_time": self.call_time,
				"call_reason": self.call_reason,
				"customer_message": self.customer_message
			},
			user="Waiter"
		)


@frappe.whitelist(allow_guest=True)
def create_waiter_call(session_token, table, call_reason=None, customer_message=None):
	"""Create a waiter call from customer interface"""
	# Validate session
	try:
		session = frappe.get_doc("Customer Session", {"session_token": session_token})
		if session.status != "Active":
			frappe.throw("Session is not active")

		# Create waiter call
		call = frappe.get_doc({
			"doctype": "Waiter Call",
			"table": table,
			"session": session.name,
			"call_time": frappe.utils.now(),
			"status": "Pending",
			"call_reason": call_reason or "Assistance Required",
			"customer_message": customer_message
		})
		call.insert(ignore_permissions=True)

		# Update session waiter calls count
		session.increment_waiter_calls()

		frappe.db.commit()

		return {
			"success": True,
			"call_id": call.name,
			"message": "Waiter has been notified"
		}

	except frappe.DoesNotExistError:
		return {"success": False, "message": "Invalid session"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Waiter Call Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_pending_calls():
	"""Get all pending waiter calls"""
	calls = frappe.get_all(
		"Waiter Call",
		filters={"status": ["in", ["Pending", "Acknowledged"]]},
		fields=["name", "table", "table_number", "call_time", "status", "call_reason", "customer_message"],
		order_by="call_time desc"
	)
	return calls


@frappe.whitelist()
def acknowledge_call(call_id):
	"""Acknowledge a waiter call"""
	call = frappe.get_doc("Waiter Call", call_id)
	call.status = "Acknowledged"
	call.assigned_waiter = frappe.session.user
	call.save()
	return {"success": True, "message": "Call acknowledged"}


@frappe.whitelist()
def resolve_call(call_id, notes=None):
	"""Resolve a waiter call"""
	call = frappe.get_doc("Waiter Call", call_id)
	call.status = "Resolved"
	if notes:
		call.notes = notes
	call.save()
	return {"success": True, "message": "Call resolved"}
