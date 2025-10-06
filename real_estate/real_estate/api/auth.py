from tokenize import Ignore
from warnings import filters
import frappe
from erpnext.accounts.party import get_dashboard_info
from frappe.core.doctype.user.user import update_password
from frappe.exceptions import DuplicateEntryError
from redis import AuthenticationError

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager() 
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": "0",
            "error": "Authentication Error. Username and password provided are incorrect."
        }
        return

    user = frappe.get_doc("User", frappe.session.user)
    employee = frappe.get_all("Employee", filters=[["user_id", "=", user.name]], fields=["name", "employee_name"])[0]
    if user.user_type != 'System User' or not employee:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": "0",
            "error": "Authentication Error. User is not a registered employee."
        }

        return 
    
    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc("User", frappe.session.user)

    frappe.local.response["message"] = {
        "success_key": "1",
        "employee": employee.employee_name,
        "employee_id": employee.id,
        "user": user.name,
        "image": user.user_image,
        "firstname": user.first_name,
        "role": user.role_profile_name,
        "lastname": user.last_name,
        "sid": frappe.session.sid,
        "api_key": user.api_key,
        "api_secret": api_generate
    }

def generate_keys(user_name):
    user = frappe.get_doc("User", user_name)
    api_secret = frappe.generate_hash(length=15)
    
    if not user.api_key:
        api_key = frappe.generate_hash(length=15)
        user.api_key = api_key

    user.api_secret = api_secret
    user.save(ignore_permissions=True)

    return api_secret