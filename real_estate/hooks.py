from . import __version__ as app_version

app_name = "real_estate"
app_title = "Real Estate"
app_publisher = "Finesoft"
app_description = "Real Estate Sales"
app_email = "finesoftafrika@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/real_estate/css/real_estate.css"
# app_include_js = "/assets/real_estate/js/real_estate.js"

# include js, css files in header of web template
# web_include_css = "/assets/real_estate/css/real_estate.css"
# web_include_js = "/assets/real_estate/js/real_estate.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "real_estate/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Project" : "public/override/project.js",
              "Sales Order" : "public/override/sales_order.js",
              "Leave Application" : "public/override/leave_application.js"
			 }

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "real_estate.utils.jinja_methods",
#	"filters": "real_estate.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "real_estate.install.before_install"
# after_install = "real_estate.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "real_estate.uninstall.before_uninstall"
# after_uninstall = "real_estate.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "real_estate.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"Sales Invoice": "real_estate.real_estate.api.override.RealEstateSalesInvoice"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }
doc_events = {
	"Sales Order": {
		"on_submit": "real_estate.real_estate.api.sales.update_plots_on_offer_submit",
		"on_cancel": "real_estate.real_estate.api.sales.update_plots_on_offer_cancel",
		"after_insert": "real_estate.real_estate.api.sales.update_plots_on_offer_create",
        "on_change": "real_estate.real_estate.api.sales.update_plots_on_offer_update"
	},
	"Sales Invoice": {
		"on_submit": "real_estate.real_estate.api.sales.update_plots_on_sale_submit"
	},
    "Payment Entry": {
		"on_submit": "real_estate.real_estate.api.util.update_advance_paid",
		"on_cancel": "real_estate.real_estate.api.util.update_advance_paid_on_cancel"  
	},
    "Lead": {
		"before_insert": "real_estate.real_estate.api.clients.validate_lead",
	},
    "Leave Application": {
        "validate": "real_estate.real_estate.api.leave.validate_leave",
        "before_insert": "real_estate.real_estate.api.leave.before_insert",
        "on_update": "real_estate.real_estate.api.leave.on_update"
	}
    
}

jinja = {
	"methods": [
		 "real_estate.real_estate.api.util.date_in_words",
         "real_estate.real_estate.api.util.get_workflow_action_url"
	]
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"real_estate.tasks.all"
#	],
#	"daily": [
#		"real_estate.tasks.daily"
#	],
#	"hourly": [
#		"real_estate.tasks.hourly"
#	],
#	"weekly": [
#		"real_estate.tasks.weekly"
#	],
#	"monthly": [
#		"real_estate.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "real_estate.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "real_estate.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "real_estate.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"real_estate.auth.validate"
# ]
