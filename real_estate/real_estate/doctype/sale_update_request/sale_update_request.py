# Copyright (c) 2023, Finesoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SaleUpdateRequest(Document):
	
	def on_submit(self):
		if self.type == "Sale Cancel":
			if self.status == 'Approved':
				sale = frappe.get_doc("Sales Order", self.source)
				sale.flags.ignore_links = True
				sale.cancel()
				frappe.db.commit()
		else:
			if self.status == 'Approved':
				sale = frappe.get_doc("Sales Order", self.source)
				sale.flags.ignore_links = True
				sale.cancel()

				new_sale = frappe.get_doc("Sales Order", self.output)
				new_sale.submit()
				# TODO: equalize payments for old order to new order:...........

				new_sale.save()
