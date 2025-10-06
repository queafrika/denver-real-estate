import frappe
import math
import datetime

@frappe.whitelist()
def update_employee(customer, employee):
	customer_doc = frappe.get_doc("Customer", customer)
	employee_doc = frappe.get_doc("Employee", employee)

	customer_doc.account_manager = employee_doc.user_id
	customer_doc.save()

	sales = frappe.get_all("Sales Order", filters=[["customer", "=", customer_doc.name]])

	for sale in sales:
		sale_doc = frappe.get_doc("Sales Order", sale.name)

		if sale_doc.docstatus != 2:
			sale_doc.sales_rep = employee
			sale_doc.save()

			if sale_doc.sale_commission is not None:
				sale_commission = frappe.get_doc("Sale Commission", sale_doc.sale_commission)
				sale_commission.exec = employee
				sale_commission.save()
		
	frappe.msgprint(msg = "Customer Manager updated successfully", title="Update Success", indicator="green")

@frappe.whitelist()
def reassign_all_customers(old_employee, new_employee):
    try:
        old_employee_doc = frappe.get_doc("Employee", old_employee)
        new_employee_doc = frappe.get_doc("Employee", new_employee)
        
        customers = frappe.get_all("Customer", filters={"account_manager": old_employee_doc.user_id}, fields=["name"])
        
        if not customers:
            frappe.throw("No customers found for the given employee.")
        
        for customer in customers:
            customer_doc = frappe.get_doc("Customer", customer.name)
            customer_doc.account_manager = new_employee_doc.user_id
            customer_doc.save()
            
            sales = frappe.get_all("Sales Order", filters={"customer": customer_doc.name}, fields=["name", "docstatus", "sale_commission"])
            
            for sale in sales:
                sale_doc = frappe.get_doc("Sales Order", sale.name)
                
                if sale_doc.docstatus != 2:
                    sale_doc.sales_rep = new_employee
                    sale_doc.save()
                    
                    if sale_doc.sale_commission:
                        sale_commission = frappe.get_doc("Sale Commission", sale_doc.sale_commission)
                        sale_commission.exec = new_employee
                        sale_commission.save()
        
        frappe.msgprint(msg="Customers reassigned successfully", title="Update Success", indicator="green")
    except frappe.DoesNotExistError:
        frappe.throw("One or more records do not exist. Please check the provided IDs.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer Reassignment Error")
        frappe.throw(f"An error occurred while reassigning customers: {str(e)}")

def update_advance_paid(doc, method=None):
	for ref in doc.references:
		if ref.reference_doctype == 'Sales Order':
			order = frappe.get_doc("Sales Order", ref.reference_name)
			advance_paid = frappe.db.sql(""" Select ifnull(sum(per.allocated_amount), 0) as val from `tabPayment Entry Reference` per
										  left join `tabPayment Entry` pe on pe.name = per.parent 
											where per.reference_name = %(order)s and pe.docstatus  = 1""", values={"order":order.name}, as_dict=1)[0].val
			
			frappe.db.set_value("Sales Order", ref.reference_name, "advance_paid", advance_paid)
		


def update_advance_paid_on_cancel(doc, method=None):
	for ref in doc.references:
		if ref.reference_doctype == 'Sales Order':
			order = frappe.get_doc("Sales Order", ref.reference_name)
			advance_paid = frappe.db.sql(""" Select ifnull(sum(per.allocated_amount), 0) as val from `tabPayment Entry Reference` per
										  left join `tabPayment Entry` pe on pe.name = per.parent 
											where per.reference_name = %(order)s and pe.docstatus  = 1""", values={"order":order.name}, as_dict=1)[0].val
			frappe.db.set_value("Sales Order", ref.reference_name, "advance_paid", advance_paid)

@frappe.whitelist()
def generate_plots(project, qty, cash_price, numbering, purchase_invoice, installment_price = None, plot_size = None):
	qty = int(qty)

	alphabets = [chr(i) for i in range(ord('A'), ord('Z')+1) if chr(i) not in ['I', 'O']]
	
	stock_entry = frappe.new_doc("Stock Entry")

	stock_entry.stock_entry_type = "Repack"
	stock_entry.project = project
	plots = []

	if (frappe.db.get_single_value('Real Estate Settings', 'default_warehouse') in (None, "") or
		frappe.db.get_single_value('Real Estate Settings', 'default_plot_item') in (None, "") or
		frappe.db.get_single_value('Real Estate Settings', 'default_land_item') in (None, "")):
		frappe.throw("Please set Default Warehouse, Default Land Item and Default Plot Item in Real Estate Settings.")

	
	stock_entry.append("items", {
		"s_warehouse": frappe.db.get_single_value('Real Estate Settings', 'default_warehouse'),
		"item_code": frappe.db.get_single_value('Real Estate Settings', 'default_land_item'),
		"qty": 1,
		"item_name": project,
		"uom": "Nos",
		"serial_no": project,
	})

	for i in range(qty):
		plot_number = ""

		if numbering == "Numeric":
			plot_number = str(i + 1)
		else:
			level = str(math.floor(i/24))
			if level == "0":
				level = ""
				
			idx = i % 24
			plot_number = alphabets[idx] + level

		plot_name = project + "-" + plot_number

		stock_entry.append("items", {
			"t_warehouse": frappe.db.get_single_value('Real Estate Settings', 'default_warehouse'),
			"item_code": frappe.db.get_single_value('Real Estate Settings', 'default_plot_item'),
			"qty": 1,
			"item_name": plot_name,
			"uom": "Nos",
			"serial_no": plot_name,
		})

		plots.append({
			"plot": plot_name,
			"number": plot_number,
			"status": "VACANT",
			"size": plot_size,
			"cash_price": cash_price,
			"installment_price": installment_price,
		})

	stock_entry.save()
	stock_entry.submit()

	project = frappe.get_doc("Project", project)

	for plot in plots:
		project.append("plots", plot)

	project.save()
		

		
def create_invoices():

	sales = frappe.get_all("Sales Order", filters={"status": "To Bill"}, fields=["name", "advance_paid", "net_total"])

	for sale in sales:
		if sale.advance_paid == sale.net_total:
			try :
				sale = frappe.get_doc("Sales Order", sale.name)
				from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
				sales_inv = frappe.new_doc("Sales Invoice")

				make_sales_invoice(source_name = sale.name, target_doc=sales_inv, ignore_permissions=True)

				sales_inv.payment_schedule = []
				sales_inv.update_stock = 1
				sales_inv.project = sale.project

				for item in sales_inv.items:
					item.serial_no = sale.plot
					

				sales_inv.sales_rep = sale.sales_rep
				sales_inv.plot = sale.plot
				sales_inv.set_advances()
				sales_inv.set_posting_time = 1
				sales_inv.posting_date = frappe.utils.add_to_date(sale.transaction_date, days=20)

				for pay in sales_inv.advances:
					pay = frappe.get_doc(pay.reference_type, pay.reference_name)
					pay_date = frappe.utils.add_to_date(pay.posting_date, days=20)
					if pay_date > sales_inv.posting_date:
						sales_inv.posting_date == pay_date
					
				sales_inv.insert()
				sales_inv.submit()
			except :
				import traceback 
	
				traceback.print_exc()
				err = frappe.new_doc("Error Log")
				err.method = "Unable to Invoice Sale: " + sale.name,
				err.error = traceback.format_exc()

				err.save()
				
@frappe.whitelist()
def date_in_words(date):
	from num2words import num2words

	"""
	Converts a date in the format '03 August 2025' to the format 
	'third day of August Two Thousand and Twenty Five'.
	"""
	# Parse the input date string
	try:
		date_obj = datetime.datetime.strptime(date, "%d %B %Y")
	except ValueError:
		return "Invalid date format. Please use 'DD Month YYYY'."
	
	# Extract components
	day = date_obj.day
	month = date_obj.strftime("%B")
	year = date_obj.year
	
	# Convert day and year to words
	day_in_words = num2words(day, to="ordinal").capitalize()
	year_in_words = num2words(year).capitalize()
	
	# Format the date in words
	
	date_in_words = f"{day_in_words} day of {month} {year_in_words}"
	return date_in_words

@frappe.whitelist()
def get_workflow_action_url(action, docname, doctype, current_state, user, modified):
	from frappe.utils.verified_command import get_signed_params
	apply_action_method = "/api/method/frappe.workflow.doctype.workflow_action.workflow_action.apply_action"

	params = {
		"doctype": doctype,
		"docname": docname,
		"action": action,
		"current_state": current_state,
		"user": user,
		"last_modified": modified,
	}
	return frappe.utils.get_url(apply_action_method + "?" + get_signed_params(params))

