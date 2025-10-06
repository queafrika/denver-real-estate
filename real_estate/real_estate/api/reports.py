import frappe;

@frappe.whitelist()
def get_report(report_name): 
    if report_name == 'my-sales':
        rows = []

        user = frappe.session.user

        employee = frappe.get_all("Employee", filters=[["user_id", "=", user]], fields=["name", "employee_name", "branch"])[0]
        
        sales = frappe.get_all("Sales Order", filters=[["docstatus", "=", 1], ["sales_rep", "=", employee.name]])

        for s in sales:
            sale = frappe.get_doc("Sales Order", s)
            row = []
            row.append(sale.customer_name)
            row.append(sale.plot)
            row.append(frappe.utils.fmt_money(sale.grand_total)) 
            row.append(frappe.utils.fmt_money(sale.advance_paid)) 
            row.append(frappe.utils.fmt_money(sale.grand_total - sale.advance_paid))

            rows.append(row)

        headers = ["Client Name", "Plot", "Sale Amount", "Amount paid", "Balance"]

        return {"headers": headers, "rows": rows}


