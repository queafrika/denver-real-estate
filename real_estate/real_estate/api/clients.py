import frappe

from real_estate.real_estate.data_engine.query import CustomerQuery
from erpnext.crm.doctype.lead.lead import make_opportunity;
from frappe.contacts.doctype.contact.contact import get_contacts_linking_to

@frappe.whitelist()
def get_clients(search_term=None, page_length=None, sort_order=None, start=None):

    # TODO: check the user and update query for sales person and sales supervisor.
    customer_query = CustomerQuery()

    return customer_query.query(search_term=search_term, page_length=page_length, sort_order=sort_order, start=start);   

@frappe.whitelist()
def  create_client(
        customer_type, 
        company_name=None,
        contacts = [],
        first_name = None,
        last_name = None,
        middle_name = None,
        nok_email_id = None,
        nok_first_name = None,
        nok_last_name = None,
        nok_id_no = None,
        nok_is_minor = None,
        nok_mobile_no = None,
        reg_date = None,
        relationship = None,
        reg_no = None,
        opportunity_name = None,
        lead_name = None,
        gender = None,
        country = None,
        county = None,
        location = None,
        ):
    
    if customer_type == 'Individual':

        customer_name = first_name
        if middle_name:
            customer_name = customer_name + " " + middle_name + " " + last_name
        else:
            customer_name = customer_name + " " + last_name

        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_group": "Individual",
            "territory": "Kenya",
            "customer_name": customer_name,
            "customer_type": customer_type,
            "nok_name": nok_first_name + " " + nok_last_name,
            "nok_email": nok_email_id,
            "nok_phone": nok_mobile_no,
            "nok_relationship": relationship,
            "nok_id_no": nok_id_no,
            "nok_is_minor": nok_is_minor,
            "id_or_passport_no_or_reg_number": reg_no,
            "dob_or_reg_date": reg_date,
            "opportunity_name": opportunity_name,
            "lead_name": lead_name,
            "gender": gender,
            "country": country,
            "county": county, 
            "location": location,
            "account_manager": frappe.session.user,
        })

    
        customer.save()

        for contact in contacts:
            cont = make_contact(customer.name, first_name = first_name, last_name = last_name,  mobile_no =contact.get("mobile_no"), email_id = contact.get("email_id"), is_primary_contact=contact.get("contact_default"))
            if contact.get("contact_default"):
                customer.db_set("customer_primary_contact", cont.name)
                customer.db_set("mobile_no", cont.mobile_no)
                customer.db_set("email_id", cont.email_id)


        return customer.name

    else:

        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_type": customer_type,
            "customer_group": "Individual",
            "customer_name": company_name,
            "territory": "Kenya",
            "id_or_passport_no_or_reg_number": reg_no,
            "dob_or_reg_date": reg_date,
            "country": country,
            "county": county, 
            "location": location,
        })

        customer.save()

        for contact in contacts:
            cont = make_contact(customer.name, first_name = contact.get("contact_first_name"), last_name = contact.get("contact_last_name"),  is_signatory=contact.get("signatory"),
                                id_number=contact.get("contact_id_no"), designation=contact.get("designation"),
                                mobile_no = contact.get("mobile_no"), email_id = contact.get("email_id"), is_primary_contact=contact.get("contact_default"))
            if contact.get("contact_default"):
                customer.db_set("customer_primary_contact", cont.name)
                customer.db_set("mobile_no", cont.mobile_no)
                customer.db_set("email_id", cont.email_id)

        return customer.name


def make_contact(customer, first_name, last_name, email_id=None, mobile_no=None, is_primary_contact=1, designation=None, is_signatory=None, id_number=None):
	contact = frappe.get_doc(
		{
			"doctype": "Contact",
			"first_name": first_name,
            "designation": designation,
			"last_name": last_name,
            "is_signatory": is_signatory,
            "id_number": id_number,
			"is_primary_contact": is_primary_contact,
			"links": [{"link_doctype": "Customer", "link_name": customer}],
		}
	)
	if email_id:
		contact.add_email(email_id, is_primary=True)

	if mobile_no:
		contact.add_phone(mobile_no, is_primary_mobile_no=True)
	contact.insert()

	return contact

def validate_lead(doc, method):
    if not doc.mobile_no:
        frappe.throw("Mobile number must be present")

    leads = frappe.get_all("Lead", filters=[["mobile_no", "=", doc.mobile_no]])

    if len(leads) > 0:
        frappe.throw("A lead with the same phone number already exists.")

    import phonenumbers
    from phonenumbers import carrier
    from phonenumbers.phonenumberutil import number_type

    if not carrier._is_mobile(number_type(phonenumbers.parse(doc.mobile_no))):
        frappe.throw("Please provide a valid mobile no for lead")
        
    if doc.email_id:  # This will work only if the email address is provided
        import re
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, doc.email_id):
            frappe.throw("Please provide a valid email address")


@frappe.whitelist()
def get_events():
    events =  frappe.get_list("Event", filters=[["starts_on", ">=", frappe.utils.today()]])

    events_list = []
    for event in events:
        ev = frappe.get_doc("Event", event.name)
        events_list.append(ev)

    return events_list



@frappe.whitelist()
def update_customer( name,customer_name = None, dob_or_reg_date = None, country = None, county = None, location = None, gender = None, id_or_passport_no_or_reg_number = None):
    customer = frappe.get_doc("Customer", name)
    if customer_name != customer.customer_name and customer_name != None:
        customer.customer_name = customer_name

    if dob_or_reg_date != customer.dob_or_reg_date and dob_or_reg_date != None:
        customer.dob_or_reg_date = dob_or_reg_date

    if country != customer.country and country != None:
        customer.country = country
    
    if county != customer.county and county != None:
        customer.county = county
    
    if location != customer.location and location != None:
        customer.location = location

    if gender != customer.gender and gender != None:
        customer.gender  = gender
    
    if id_or_passport_no_or_reg_number != customer.id_or_passport_no_or_reg_number and id_or_passport_no_or_reg_number != None:
        customer.id_or_passport_no_or_reg_number = id_or_passport_no_or_reg_number

    customer.save()
    return customer.name


@frappe.whitelist()
def update_customer_nok(
    name,
    nok_name = None,
    nok_phone = None,
    nok_email = None,
    nok_relationship = None,
    nok_id_no = None,
    nok_is_minor = None,
):
    customer = frappe.get_doc("Customer", name)
    if nok_name != customer.nok_name and nok_name != None:
        customer.nok_name = nok_name

    if nok_phone != customer.nok_phone and nok_phone != None:
        customer.nok_phone = nok_phone

    if nok_email != customer.nok_email and nok_email != None:
        customer.nok_email = nok_email
    
    if nok_relationship != customer.nok_relationship and nok_relationship != None:
        customer.nok_relationship = nok_relationship
    
    if nok_id_no != customer.nok_id_no and nok_id_no != None:
        customer.nok_id_no = nok_id_no

    if nok_is_minor != customer.nok_is_minor and nok_is_minor != None:
        customer.nok_is_minor = nok_is_minor

    customer.save()
    return customer.name

@frappe.whitelist()
def claim_customer(customer):
    user = frappe.session.user
    employee = frappe.get_all("Employee", filters=[["user_id", "=", user]], fields=["name", "employee_name", "branch"])[0]
    
    frappe.db.set_value("Customer", customer, "account_manager", user)
    sales = frappe.get_all("Sales Order", filters=[["customer", "=", customer]], fields=["name"])

    for sale in sales:
        frappe.db.set_value("Sales Order", sale.name, "sales_rep", employee.name)

@frappe.whitelist()
def get_client(customer):
    return frappe.get_doc("Customer", customer)

@frappe.whitelist()
def get_leads():
    user = frappe.session.user
    leads = []
    leads.extend(frappe.get_all("Lead", filters=[["lead_owner", "=", user]], fields=["name","lead_name", "status", "email_id", "mobile_no", "lead_owner", "source"]))
    leads.extend(frappe.get_all("Lead", filters={"lead_owner": ["is", "not set"]}, fields=["name","lead_name", "status", "email_id", "mobile_no", "lead_owner", "source"]))

    return leads

@frappe.whitelist()
def get_opportunities(lead=None):
     if lead:
          return frappe.get_list("Opportunity", filters=[["party_name", "=", lead]], fields=["name","sales_stage", "status", "contact_email", "contact_mobile", "opportunity_owner", "opportunity_from",
                                                   "party_name"])
     
     return frappe.get_list("Opportunity", fields=["name","sales_stage", "title", "status", "contact_email", "contact_mobile", "opportunity_owner", "opportunity_from",
                                                   "party_name"])

@frappe.whitelist()
def take_lead(lead):
    user = frappe.session.user
    frappe.db.set_value("Lead", lead, "lead_owner", user)

@frappe.whitelist()
def get_lead_sources():
     return frappe.get_list("Lead Source", fields=["name"])

@frappe.whitelist()
def create_lead(
     source, firstname, lastname="", middlename="", mobile="", email="", 
):
    doc = frappe.get_doc({
        "doctype": "Lead",
        "source": source,
        "first_name": firstname,
        "middle_name": middlename,
        "last_name": lastname,
        "mobile_no": mobile,
        "email_id": email,
        "status": "Open",
    })

    doc.insert()

    return doc.name

@frappe.whitelist()
def get_lead(name):
     return frappe.get_doc("Lead", name)

@frappe.whitelist()
def get_opportunity(name):
     return frappe.get_doc("Opportunity", name)

@frappe.whitelist()
def claim_lead(name):
     
    lead = frappe.get_doc("Lead", name)
    if lead.lead_owner:
        frappe.throw("This lead already has a owner.")

    user = frappe.session.user
    lead.db_set("lead_owner", user)

    return lead.name;

@frappe.whitelist()
def add_note_to_lead(name, note):
    lead = frappe.get_doc("Lead", name)
    note_doc = lead.append("notes", {
        "added_by":frappe.session.user,
        "note":note,
        "added_on":frappe.utils.now_datetime(),
    })

    lead.save()

    return lead.name 



@frappe.whitelist()
def add_note_to_opportunity(name, note):
    opp = frappe.get_doc("Opportunity", name)
    note_doc = opp.append("notes", {
        "note":note,
    })

    opp.save()

    return opp.name 

@frappe.whitelist()
def create_opportunity_from_lead(lead):
    opportunity = make_opportunity(lead)

    opportunity.insert()
    return opportunity.name

@frappe.whitelist()
def create_opportunity_from_customer(customer):
    cust = frappe.get_doc("Customer", customer)
    opportunity = frappe.get_doc({
         "doctype": "Opportunity",
         "title": cust.name,
         "opportunity_from": "Customer",
         "party_name": cust.name,
         "sales_stage": "Prospecting",
         "status": "Open",
    })

    opportunity.insert()

    return opportunity.name

    
@frappe.whitelist()
def quick_create(customerType=None, firstName=None, middleName=None, lastName=None, registrationNo=None, 
                 phoneNumber=None, email=None, contactPersonFirstName=None, contactPersonLastName=None, 
                 companyName=None, contactPersonPhoneNumber=None, contactPersonEmail=None, groupName=None):
    
    if customerType == "Individual":
        # Create individual customer

        customer_name = firstName
        if middleName:
            customer_name = customer_name + " " + middleName + " " + lastName
        else:
            customer_name = customer_name + " " + lastName

        
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_group": "Individual",
            "customer_name": customer_name,
            "email_id": email,
            "mobile_no": phoneNumber,
            "account_manager": frappe.session.user,
            "id_or_passport_no_or_reg_number": registrationNo,
            "territory": "Kenya", #TODO: get territory from user
        })

        customer.insert()
    elif customerType == "Company":
        # Create company customer
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_group": "Individual",
            "customer_type": "Company",
            "customer_name": companyName,
            "account_manager": frappe.session.user,
            "territory": "Kenya", #TODO: get territory from user
            # Add other fields specific to company customer
        })

        customer.insert()
        make_contact(customer.name, contactPersonFirstName, contactPersonLastName, contactPersonEmail, contactPersonPhoneNumber, is_primary_contact=1, is_signatory=1)
    elif customerType == "Group":
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_group": "Individual",
            "customer_type": "Group",
            "customer_name": groupName,
            "account_manager": frappe.session.user,
            "territory": "Kenya", #TODO: get territory from user
            # Add other fields specific to company customer
        })

        customer.insert()
        make_contact(customer.name, contactPersonFirstName, contactPersonLastName, contactPersonEmail, contactPersonPhoneNumber, is_primary_contact=1, is_signatory=1)

    return customer.name


@frappe.whitelist()
def get_countries(search_term=None):
    search = "%{}%".format(search_term)
    if search_term != None:
        return frappe.get_list("Country", filters=[["name", "like", search]],  fields=["name"])
    else:
        return frappe.get_list("Country",  fields=["name"])


@frappe.whitelist()
def get_counties(search_term=None):
    search = "%{}%".format(search_term)

    if search_term != None:
        return frappe.get_list("County", filters=[["name", "like", search]], fields=["name"])
    else:
        return frappe.get_list("County",  fields=["name"])

@frappe.whitelist()
def get_genders():
     return frappe.get_list("Gender", fields=["name"])

@frappe.whitelist()
def close_lead(lead):
    lead = frappe.get_doc("Lead", lead)
    lead.status = "Closed"
    lead.save()

@frappe.whitelist()
def upload_file(**kwargs):

    files = frappe.request.files

    if "file" in files:
        file = files["file"]
        customer = frappe.get_doc("Customer", kwargs["customer"])
        filename = kwargs["filename"]

        upload = customer.append("files", {})

        file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": "Customer",
				"attached_to_name": customer.name,
				"folder": "Home",
				"file_name": file.filename,
				"is_private": 1,
				"content": file.stream.read(),
			}
		).save(ignore_permissions=True)

        upload.save_name = file_doc.file_name 
        upload.filename = filename
        upload.file = file_doc.file_url

        customer.save(ignore_permissions=True)

        return customer.name

@frappe.whitelist()
def update_lead(details, lead_name):
    lead = frappe.get_doc("Lead", lead_name)

    
    lead.budget = details.get("budget")
    lead.need = details.get("need")
    lead.authority = details.get("authority")
    lead.time_needed = details.get("timeNeeded")
    lead.sites_visited = []

    for site in details.get("projectsVisited"):
         lead.append("sites_visited",{
              "project": site 
         })
    lead.save()
    
@frappe.whitelist()
def create_event_for_lead(event, lead_name):
    lead = frappe.get_doc("Lead", lead_name)


    user = frappe.get_doc("User", frappe.session.user)
    employee = frappe.get_all("Employee", filters=[["user_id", "=", user.name]], fields=["name", "employee_name"])[0]

    event = frappe.get_doc({
        "doctype": "Event",
        "subject": event["subject"],
        "starts_on": event["due_date"],
        "description": event["description"],
        "event_type":  "Public" if event["public"] else "Private",
        "event_category": event["category"],
        "status": "Open",
        "event_participants": [
            {
                "reference_doctype": "Lead",
                "reference_docname": lead.name,
            },
            {
                "reference_doctype": "Employee",
                "reference_docname": employee.name,
            }
        ],
    })

    event.insert()

    return event.name


@frappe.whitelist()
def get_contacts(customer):
    customer = frappe.get_doc("Customer", customer)
    
    contacts = []

    for cont_name in get_contacts_linking_to("Customer", customer.name):
        contact = {}
        cont = frappe.get_doc("Contact", cont_name.name)
        contact["name"] = cont.name
        contact["first_name"] = cont.first_name
        contact["middle_name"] = cont.middle_name
        contact["last_name"] = cont.last_name
        contact["phone"] = cont.mobile_no
        contact["full_name"] = cont.first_name + " " + cont.last_name
        contact["email"] = cont.email_id
        contact["designation"] = cont.designation
        contact["id_number"] = cont.id_number
        contact["is_signatory"] =  True if cont.is_signatory == 1 else False
        contact["for_individual"] = customer.customer_type == "Individual" 
        contact["is_default"] = True if cont.is_primary_contact == 1 else False


        if (customer.customer_type == "Individual"):
            if len(cont.email_ids) > 1 or len(cont.phone_nos) > 1:
                
                length = max(len(cont.phone_nos), len(cont.email_ids))

                for i in range(length):
                    
                    contact = {}
                    contact["name"] = cont.name
                    contact["first_name"] = cont.first_name
                    contact["middle_name"] = cont.middle_name
                    contact["last_name"] = cont.last_name
                    if (i < len(cont.phone_nos)):
                        contact["phone"] = cont.phone_nos[i].phone
                    contact["full_name"] = cont.first_name + " " + cont.last_name
                    if (i < len(cont.email_ids)):
                        contact["email"] = cont.email_ids[i].email_id
                    contact["designation"] = cont.designation
                    contact["id_number"] = cont.id_number
                    contact["is_signatory"] =  True if cont.is_signatory == 1 else False
                    contact["for_individual"] = customer.customer_type == "Individual" 
                    contact["is_default"] = True if cont.is_primary_contact == 1 else False
                    contact["Secondary"] = True

                    contacts.append(contact)

            else:
                contacts.append(contact)
        else:
            contacts.append(contact)
            

    return {"contacts": contacts}


@frappe.whitelist()
def get_contact(name):
        contact = {}
        cont = frappe.get_doc("Contact", name)
        for_individual = False
        for link in cont.links:
            if link.link_doctype == "Customer":
                for_individual = frappe.get_value("Customer", link.link_name, "customer_type") == "Individual"

        contact["name"] = cont.name
        contact["first_name"] = cont.first_name
        contact["middle_name"] = cont.middle_name
        contact["last_name"] = cont.last_name
        contact["phone"] = cont.mobile_no
        contact["full_name"] = cont.first_name + " " + cont.last_name
        contact["email"] = cont.email_id
        contact["designation"] = cont.designation
        contact["id_number"] = cont.id_number
        contact["is_signatory"] =  True if cont.is_signatory == 1 else False
        contact["for_individual"] = for_individual
        contact["is_default"] = True if cont.is_primary_contact == 1 else False


        return contact

@frappe.whitelist()
def save_contact(mode, first_name = None, middle_name = None, last_name = None, phone = None, email = None, designation = None, is_signatory = None, link_name = None, 
                 link_type = None, name = None, id_number = None):
    
    link_type = "individual"
    if link_name != None and link_name != "" and link_type == "Customer":
        link_type = frappe.get_value("link_type", link_name, "customer_type")


    if (name != None and name != ""):
        contact = frappe.get_doc("Contact", name)

    if contact != None and link_type == "Individual":
        contact_name = get_contacts_linking_to(link_type, link_name)[0].name
        contact = frappe.get_doc("Contact", contact_name)

    if contact == None:
        contact = frappe.new_doc("Contact")

    if first_name != None and first_name != "":
        contact.first_name = first_name

    if middle_name != None and middle_name != "":
        contact.middle_name = middle_name

    if last_name != None and last_name != "":
        contact.last_name = last_name

    if first_name != None and first_name != "":
        contact.first_name = first_name

    if designation != None and designation != "":
        contact.designation = designation

    if is_signatory != None and is_signatory != "":
        contact.is_signatory = is_signatory

    if id_number != None and id_number != "":
        contact.id_number = id_number

    if phone != None and phone != "":
        contact.append("phone_nos", {
            "phone": phone
        })

    if email != None and email != "":
        contact.append("email_ids", {
            "email_id": email
        })

    if link_name != None and link_name != "":
        if not contact.has_link(link_type, link_name):
            contact.append("links", {
                "link_doctype": link_type,
                "link_name": link_name
            })
              
    contact.save()
    return contact.name

@frappe.whitelist()
def get_approval_comment(sales_order):
    sales_order = frappe.get_doc("Sales Order", sales_order)
    comment = ""
    
    if sales_order.custom_discount_approved == 0:
        comment = "The sales order discount requires executive approval."
    
    if sales_order.custom_installments_approved == 0:
        comment += "<br> The sales order installments require approval from the executive"
    
    if comment != "":
        return comment
    else:
        return None

