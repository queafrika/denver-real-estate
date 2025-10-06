import frappe


@frappe.whitelist() 
def get_sales_rep_dashboard(start_date , end_date):
    user = frappe.session.user

    employee = frappe.get_all("Employee", filters=[["user_id", "=", user]], fields=["name", "employee_name", "branch"])[0]

    params = {"start_date": start_date, "end_date": end_date, "employee": employee.name}
    dashboard = {}
    stats = []
    try :
        commissions = frappe.db.sql("""
                                select sum(sc.commission) - sum(sc.total_paid) - sum(sc.total_earned) as count from `tabSale Commission` sc
                                where sc.exec = %(employee)s
                                 """, values = params, as_dict=1)[0].count

        comm_payable = frappe.db.sql("""
                                select sum(sc.total_earned) as count from `tabSale Commission` sc
                                where sc.exec = %(employee)s
                                 """, values = params, as_dict=1)[0].count
    except :
        commissions = 0
        comm_payable = 0

    total_sales = frappe.db.sql("""select sum(si.grand_total) as count from `tabSales Invoice` si 
    where si.sales_rep = %(employee)s and si.docstatus = 1 and si.posting_date between %(start_date)s and  %(end_date)s""", values=params, as_dict=1)[0].count

    plots_sold = frappe.db.sql("""
        select count(distinct p.name) as count from `tabProject Plot Detail` p
        left join `tabSales Order` so on so.plot = p.name
        where p.sales_rep = %(employee)s
        and p.status <> 'VACANT'
        and so.transaction_date between %(start_date)s and  %(end_date)s
     """, values=params, as_dict=1)[0].count

    payments_collected = frappe.db.sql("""
        select sum(per.allocated_amount) as count from `tabPayment Entry Reference` per
        left join `tabPayment Entry` pe on pe.name = per.parent
        left join `tabSales Invoice` si on si.name = per.reference_name and per.reference_doctype = 'Sales Invoice'
        left join `tabSales Order` so on so.name = per.reference_name and per.reference_doctype = 'Sales Order'
        where pe.docstatus = 1 and (si.sales_rep = %(employee)s or so.sales_rep = %(employee)s) and  %(start_date)s and  %(end_date)s
     """, values=params, as_dict=1)[0].count

    open_offers = frappe.db.sql( """
        select count(distinct so.name) as count from `tabSales Order` so where so.sales_rep = %(employee)s and so.status <> 'Completed' and so.docstatus <> 2
    """, values=params, as_dict=1)[0].count

    stats.append({"title": "Total Sales", "value": frappe.utils.fmt_money(total_sales, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Total Collection", "value": frappe.utils.fmt_money(payments_collected, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Plots Sold", "value": str(plots_sold), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Open Offers", "value": str(open_offers), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Sales Commissions(Not Earned)", "value": frappe.utils.fmt_money(commissions, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Payable Commissions(Earned)", "value": frappe.utils.fmt_money(comm_payable, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    dashboard["stats"] = stats
    
    return dashboard


@frappe.whitelist() 
def get_app_dashboard():
    user = frappe.session.user

    employee = frappe.get_all("Employee", filters=[["user_id", "=", user]], fields=["name", "employee_name", "branch"])[0]

    params = {"employee": employee.name}
    stats = []
    try :
        commissions = frappe.db.sql("""
                                select sum(sc.commission) - sum(sc.total_paid) - sum(sc.total_earned) as count from `tabSale Commission` sc
                                where sc.exec = %(employee)s
                                 """, values = params, as_dict=1)[0].count

        comm_payable = frappe.db.sql("""
                                select sum(sc.total_earned) as count from `tabSale Commission` sc
                                where sc.exec = %(employee)s
                                 """, values = params, as_dict=1)[0].count
    except :
        commissions = 0
        comm_payable = 0


    stats.append({"title": "Sales Commissions(Not Earned)", "value": frappe.utils.fmt_money(commissions, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    stats.append({"title": "Payable Commissions(Earned)", "value": frappe.utils.fmt_money(comm_payable, currency='KES'), "icon": "bx-dollar-circle", "percentage": "10", "profit": "up"})
    
    
    return {
        "Sales Commissions(Not Earned)": frappe.utils.fmt_money(commissions, currency='KES'),
        "Payable Commissions(Earned)": frappe.utils.fmt_money(comm_payable, currency='KES')
    }



@frappe.whitelist()
def get_smp_greeting():
    return frappe.db.get_single_value("View Settings", "staff_smp_greeting")