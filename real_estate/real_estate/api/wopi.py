import frappe;
from frappe.translate import print_language
from frappe.www.printview import validate_print_permission

@frappe.whitelist(allow_guest=True)
def files(*args, **kwargs):

    if frappe.request.method == "GET":
        if str.__contains__(frappe.request.url, "/contents"):
            name="example.pdf"
            content = load_file(name)
            if content:
                frappe.response["headers"] = {
                "Content-Disposition": f'attachment;filename="{name.encode("ISO-8859-1").decode("utf-8")}"',
                "Content-Length": len(content)
                }

                frappe.response["filecontent"]=content
                frappe.response["filename"]="example.pdf"
                frappe.response["type"] = "binary"
            else:
                return "File not found"
        else:            
            import os
            import hashlib
            name = "example.pdf"
            file_path = "/tmp/" + name

            # Create the JSON object with the file details
            frappe.response["BaseFileName"] = name
            frappe.response["Size"] = os.path.getsize(file_path)
            frappe.response["OwnerId"] = "admin"
            frappe.response["UserId"] = 1
            frappe.response["Version"] = os.path.getmtime(file_path)
            frappe.response["LastModifiedTime"] = os.path.getmtime(file_path)

            try:
                # Calculate SHA256 checksum
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(65536)  # Read in 64k chunks
                        if not data:
                            break
                        sha256_hash.update(data)
                frappe.response["Sha256"] = sha256_hash.hexdigest()
            except (FileNotFoundError, IOError, hashlib.HashError) as e:
                return e

            frappe.response["UserCanWrite"] = True
    else:
        pass

@frappe.whitelist()
def get_html(doc_name):
    doc = doc or frappe.get_doc("Sales Order", doc_name)
    return frappe.get_print(
        "Sales Order", doc_name, format, doc=doc, as_pdf=False, letterhead=None, no_letterhead=1
    )



def get_docx_file(
    doctype, name, format=None, doc=None, no_letterhead=0, language=None, letterhead=None
):
    doc = doc or frappe.get_doc(doctype, name)
    validate_print_permission(doc)

    with print_language(language):
        from frappe.utils import scrub_urls
        file = scrub_urls(frappe.get_print(
            doctype, name, format, doc=doc, as_pdf=False, letterhead=letterhead, no_letterhead=no_letterhead
        )).encode("utf-8")
        from htmldocx import HtmlToDocx

        new_parser = HtmlToDocx()
        docx = new_parser.parse_html_string(file)

        return docx


@frappe.whitelist()
def download_docx(
    doctype, name, format=None, doc=None, no_letterhead=0, language=None, letterhead=None
):
    
    file = get_docx_file(doctype, name, format, doc, no_letterhead, language, letterhead) 

    import io
    bio = io.BytesIO()
    file.save(bio)  # save to memory stream
    bio.seek(0)
    
    frappe.local.response.filename = "{name}.docx".format(
        name=name.replace(" ", "-").replace("/", "-")
    )
    frappe.local.response.filecontent = bio.getvalue()
    frappe.local.response.type = "binary"

def load_file(name):
    path = "/tmp/" + name
    buffer = None
    try:
        with open(path, 'rb') as file:
            buffer = file.read()
    except FileNotFoundError as ex:
        return None
    
    return buffer

