import frappe
from real_estate.real_estate.api.sales import PrintFormatGenerator
from frappe.translate import print_language
from frappe.utils.weasyprint import download_pdf


@frappe.whitelist(allow_guest=True)
def download_offer_template(ref):
	sale = frappe.get_all("Sales Order", filters={"custom_link_code": ref})[0]
	doc = frappe.get_doc("Sales Order", sale.name)
	doc.flags.ignore_permissions = 1

	with print_language(None):
		pdf = frappe.get_print(
			"Sales Order", doc.name, print_format="Default Offer Letter", doc=doc, as_pdf=True, letterhead="Default Letter Head", no_letterhead=1
		)


	# generator = PrintFormatGenerator("Sale Statement", doc, "Default Letter Head")
	# pdf = generator.render_pdf()

	frappe.local.response.filename = "{name}.pdf".format(
		name=doc.name.replace(" ", "-").replace("/", "-")
	)
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"


@frappe.whitelist(allow_guest=True)
def download_agreement_template(ref):
	sale = frappe.get_all("Sales Order", filters={"custom_link_code": ref})[0]
	doc = frappe.get_doc("Sales Order", sale.name)
	doc.flags.ignore_permissions = 1

	if doc.agreement is not None and doc.agreement != '':

		generator = PrintFormatGenerator(doc.agreement_template, doc, "NO letter head")
		pdf_file = generator.render_pdf_with_main_html(doc.agreement)

		frappe.local.response.filename = "{name}.pdf".format(
			name=doc.name.replace(" ", "-").replace("/", "-")
		)
		frappe.local.response.filecontent = pdf_file
		frappe.local.response.type = "pdf"
	else:
		doc = frappe.get_doc("Sales Order", doc.name)
		generator = PrintFormatGenerator("Default Agreement", doc, "NO letter head")
		pdf = generator.render_pdf()

		frappe.local.response.filename = "{name}.pdf".format(name=doc.name.replace(" ", "-").replace("/", "-"))
		frappe.local.response.filecontent = pdf
		frappe.local.response.type = "pdf"


@frappe.whitelist(allow_guest=True)
def download_statement(ref):
	sale = frappe.get_all("Sales Order", filters={"custom_link_code": ref})[0]
	doc = frappe.get_doc("Sales Order", sale.name)
	doc.flags.ignore_permissions = 1

	generator = PrintFormatGenerator("Sale Statement", doc, letterhead='Latest Letter Head')
	pdf = generator.render_pdf()

	frappe.local.response.filename = "{name}.pdf".format(
		name=doc.name.replace(" ", "-").replace("/", "-")
	)
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"

@frappe.whitelist(allow_guest=True)
def download_signed_offer(ref):
	sale = frappe.get_all("Sales Order", filters={"custom_link_code": ref})[0]
	doc = frappe.get_doc("Sales Order", sale.name)
	doc.flags.ignore_permissions = 1

	for f in doc.files:

		if f.filename == "Signed Offer Letter":

			file = frappe.get_all("File", filters ={"file_url": f.file})[0]
			file_doc = frappe.get_doc("File", file.name)


			frappe.local.response.filename = file_doc.file_name
			frappe.local.response.type = file_doc.file_type.lower()

			file_path = frappe.utils.get_site_path("", file_doc.file_url.lstrip("/"))
			with open(file_path, "rb") as file_content:
				frappe.local.response.filecontent = file_content.read()

@frappe.whitelist(allow_guest=True)
def download_signed_agreement(ref):
	sale = frappe.get_all("Sales Order", filters={"custom_link_code": ref})[0]
	doc = frappe.get_doc("Sales Order", sale.name)
	doc.flags.ignore_permissions = 1

	for f in doc.files:

		if f.filename == "Signed Agreement":

			file = frappe.get_all("File", filters ={"file_url": f.file})[0]
			file_doc = frappe.get_doc("File", file.name)


			frappe.local.response.filename = file_doc.file_name
			frappe.local.response.type = 'download'

			file_path = frappe.utils.get_site_path("", file_doc.file_url.lstrip("/"))
			with open(file_path, "rb") as file_content:
				frappe.local.response.filecontent = file_content.read()