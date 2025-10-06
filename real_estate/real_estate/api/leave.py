import frappe
from frappe.utils import getdate, add_days, today

def validate_leave(self, method):
    user_roles = frappe.get_roles(frappe.session.user)
    
    if self.status == "Open":
        leave_start_date = getdate(self.from_date)
        min_application_date = add_days(getdate(today()), 2)

        if (
            not self.half_day and 
            self.leave_type != 'Sick Leave' and 
            leave_start_date < min_application_date and 
            not set(user_roles).intersection({"HR Manager", "System Manager"})
        ):
            frappe.throw("KINDLY NOTE! Leave Has To Be Applied Three Days In Advance.", title="Leave Policy")

    if self.status == "Rejected" and not self.custom_rejection_reason:
        frappe.msgprint("Please provide a reason for rejecting this leave application.", title="Rejection Policy")


def before_insert(self, method):
    self.add_comment("Comment", f"Leave Applied by {frappe.session.user}.")

def on_update(self, method):
    """ Add a comment based on workflow status updates of the leave application."""
    
    if self.status == "HR Approve":  
        self.add_comment("Comment", f"Updated to HR Approve by Leave Approver ({frappe.session.user}).")

    elif self.status == "Approved":  
        self.add_comment("Comment", f"Approved by HR Manager ({frappe.session.user}).")

    elif self.status == "Rejected":  
        self.add_comment("Comment", f"Rejected by {frappe.session.user}.")
    

