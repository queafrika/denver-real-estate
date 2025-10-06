import frappe;

@frappe.whitelist()
def get_requisitions(search_term=None, pageSize=None, start=None):
    reqs = frappe.get_list("Expense Entry", fields=["name", "posting_date", "total", "mode_of_payment", "status", "payment_to", "real_estate_project"])
    return reqs

@frappe.whitelist()
def get_beneficiaries():
    reqs = frappe.get_list("Beneficiary", fields=["name", "payment_mode"])
    return reqs

@frappe.whitelist()
def get_expense_types():
    reqs = frappe.get_list("Expense Entry Type", fields=["name", "expense_type"])
    return reqs

@frappe.whitelist()
def save_requisition(beneficiary, expenses, paymentMethod, remarks, project=None, ):
    req = frappe.new_doc("Expense Entry")
    req.company = frappe.defaults.get_user_default("company")
    req.posting_date = frappe.utils.today()
    req.required_by = frappe.utils.now()    
    req.payment_to = beneficiary
    req.default_cost_center = frappe.get_value("Company", req.company, "cost_center")
    req.real_estate_project = project
    req.remarks = remarks
    req.mode_of_payment = paymentMethod
    req.total = 0
    req.quantity = 0

    for expense in expenses:
        req.append("expenses", {
            "expense_account": expense["expenseType"],
            "amount": expense["amount"],
            "description": expense["description"]
        })

        req.total += expense["amount"]
        req.quantity += 1

    req.insert()
    return req.name