# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate


class SalesByProjectReport(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})

		if not self.filters.get("company"):
			self.filters["company"] = frappe.db.get_single_value("Global Defaults", "default_company")

	def run(self, args):

		columns = self.get_columns()
		data = self.get_data()
		return columns, data


	def get_columns(self):
		columns = [{
				"label": _("Project"),
				"fieldtype": "Link",
				"fieldname": "project",
				"options": "Project",
				"width": 300,
			}, 
			{
				"label": _("Plot"),
				"fieldtype": "Link",
				"options": "Plot",
				"fieldname": "plot",
				"width": 100,
			}, 
			{
				"label": _("Sale"),
				"fieldtype": "Link",
				"options": "Sales Order",
				"fieldname": "sale",
				"width": 200,
			}, 
			{
				"label": _("Sale Executive"),
				"fieldtype": "Data",
				"fieldname": "exec",
				"width": 200,
			}, 
			{
				"label": _("Customer"),
				"fieldtype": "Link",
				"options": "Customer",
				"fieldname": "customer",
				"width": 200,
			}, 
			{
				"label": _("Phone"),
				"fieldtype": "Data",
				"fieldname": "phone",
				"width": 200,
			}, 
			{
				"label": _("Sale Price"),
				"fieldtype": "Currency",
				"fieldname": "price",
				"width": 200,
			},  
			{
				"label": _("Paid Amount"),
				"fieldtype": "Currency",
				"fieldname": "amount",
				"width": 200,
			}, 
			{
				"label": _("Balance"),
				"fieldtype": "Currency",
				"fieldname": "balance",
				"width": 200,
			}, 
		]

		return columns

	def get_data(self):
		out = []
		total_sale = 0
		total_payments = 0

		projects = frappe.get_all("Project", filters = [["status", "=", "Open"]])

		for project in projects:
			project_sale_total = 0
			project_total_payments = 0

			filters = [["project", "=", project.name]]

			if self.filters.get("exec") is not None:
				filters.append(["sales_rep", "=", self.filters.get("exec")])

			sales = frappe.get_all("Sales Order", filters=filters)
			for sale in sales:
				sale = frappe.get_doc("Sales Order", sale.name)
				out.append({
					"project": project.name,
					"plot": frappe.get_value("Plot", sale.plot, "number"),
					"customer": sale.customer,
					"sale": sale.name,
					"exec": frappe.get_value("Employee", sale.sales_rep, "employee_name"),
					"phone": frappe.get_value("Customer", sale.customer, "mobile_no"),
					"price": sale.net_total,
					"amount": sale.advance_paid,
					"balance": sale.net_total - sale.advance_paid
				})

				project_sale_total += sale.net_total
				project_total_payments += sale.advance_paid

			total_sale += project_sale_total
			total_payments += project_total_payments
			out.append({
				"project":  project.name,
				"price":  project_sale_total ,
				"amount":  project_total_payments,
				"balance":   (project_sale_total - project_total_payments),
				"bold": 1
			})
			out.append({

			})


		out.append({
			"project": "Totals",
			"price":  total_sale,
			"amount": total_payments,
			"balance": total_sale - total_payments,
			"bold": 1
		})
			

		return out

def execute(filters=None):
	args = {
	}
	return SalesByProjectReport(filters).run(args)