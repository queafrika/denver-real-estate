import frappe

@frappe.whitelist()
def get_projects():
    project_names = frappe.get_list("Project")

    projects = []
    for proj in project_names:

        project = frappe.get_doc("Project", proj.name)

        vacant_plot_counts = frappe.db.count("Project Plot Detail", {"parent": proj.name, "status": "VACANT"})
        total_plots = frappe.db.count("Project Plot Detail", filters=[["parent", "=", proj.name]])
        banner_image = ""

        if proj.banner_image:
            banner_image = frappe.utils.get_url() + "/" + project.banner_image

        projects.append({
            "name": project.name,
            "id": project.name,
            "status": project.status,
            "banner_image": "",
            "short_description": project.notes,
            "location": project.location,
            "launch_date":  frappe.utils.formatdate(project.get_formatted('expected_start_date'), "dd MMM yyyy"),
            "vacant_plots_count": vacant_plot_counts,
            "plots_count": total_plots,
            "stats": get_sales_project_statistics(project)
        })

    return projects


@frappe.whitelist()
def get_project_statuses():
    return frappe.get_list("Real Estate Project Status", fields=["name", "description"])


@frappe.whitelist()
def get_project(name):
    project =  frappe.get_doc("Project", name)
    vacant_plot_counts = frappe.db.count("Project Plot Detail", {"parent": project.name, "status": "VACANT"})
    total_plots = frappe.db.count("Project Plot Detail", filters=[["parent", "=", project.name]])
    banner_image = ""

    if project.banner_image:
        banner_image = frappe.utils.get_url() + "/" + project.banner_image

    return {
            "name": project.name,
            "id": project.name,
            "status": project.status,
            "banner_image": "",
            "short_description": project.notes,
            "location": project.location,
            "start_date":  frappe.utils.formatdate(project.get_formatted('expected_start_date'), "dd MMM yyyy"),
            "launch_date":  frappe.utils.formatdate(project.get_formatted('expected_start_date'), "dd MMM yyyy"),
            "vacant_plots_count": vacant_plot_counts,
            "plots_count": total_plots,
            "stats": get_sales_project_statistics(project)
    }


@frappe.whitelist()
def get_plots(projectName, status=None, search_term=None):

    filters = []

    plots = frappe.get_doc("Project", projectName).plots

    if status is not None:
        plots = list(filter(lambda d: d.status.upper() == status.upper() , plots))

    if search_term is not None:
        plots = list(filter(lambda d: search_term in d.name , plots))


    return plots


def get_sales_project_statistics(project):
    stats = {}
    user = frappe.session.user
    try:
        employee = frappe.get_all("Employee", filters=[["user_id", "=", user]], fields=["name", "employee_name", "branch"])[0]
    except: 
        frappe.throw("You are not a sales person. Please contact your administrator")
        

    stats["vacant_plot_count"] = frappe.db.count("Project Plot Detail", {"parent": project.name, "status": "VACANT"})
    stats["total_plots"] = frappe.db.count("Project Plot Detail", filters=[["parent", "=", project.name]])
    stats["sold_plots"] = frappe.db.count("Project Plot Detail", filters=[["parent", "=", project.name], ["sales_rep", "=", employee.name]])
    stats["sold_plots_amount"] = frappe.db.sql("""
                    SELECT SUM(so.grand_total) as value from `tabSales Order` so WHERE project = %(proj)s AND sales_rep = %(emp)s
                                               """, values={"proj": project.name, "emp": employee.name}, as_dict=True)[0].value
    stats["sold_plots_amount"] = stats["sold_plots_amount"] if stats["sold_plots_amount"] else 0.0   
    stats["total_collection"] = frappe.db.sql("""
                    SELECT SUM(so.advance_paid) as value from `tabSales Order` so WHERE project = %(proj)s AND sales_rep = %(emp)s
                                               """, values={"proj": project.name, "emp": employee.name}, as_dict=True)[0].value

    stats["total_collection"] = stats["total_collection"] if stats["total_collection"] else 0.0
    stats["balance_collection"] = stats["sold_plots_amount"] - stats["total_collection"]

    return stats;






