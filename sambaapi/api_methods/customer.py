import frappe, requests, traceback, json
from datetime import datetime
from sambaapi.api_methods.utils import get_samba_url


def get_customer_groups():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/customerGroupSearch")
        data = response.json()
    
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Customer Group", {"customer_group_name": item.get("EntityName")})
                if item.get("EntityName") in ["Customer", "Customers"]:
                    item["EntityName"] = "Walkin Customer"
                if not doc_exists:
                    if not item.get("EntityName") in ["Customer", "Customers"]:
                        try:
                            new_doc = frappe.new_doc("Customer Group")
                            new_doc.customer_group_name = item.get("EntityName")
                            new_doc.custom_samba_id = item.get("Id")
                            new_doc.parent_customer_group = "All Customer Groups"
                            new_doc.insert()
                            
                            frappe.db.commit()
                        except:
                            new_doc = frappe.new_doc("Samba Error Logs")
                            new_doc.doc_type = "Customer Group"
                            new_doc.samba_id = item.get("Id")
                            new_doc.error = traceback.format_exc()
                            new_doc.log_time = datetime.now()
                            new_doc.insert()

                            frappe.db.commit()
                else:
                    cust_group_doc = frappe.get_doc("Customer Group", doc_exists)
                    cust_group_doc.custom_samba_id = item.get("Id")
                    
                    cust_group_doc.save()
                    frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()

def get_customer(customer_type_id, start_from):
    url = get_samba_url()

    try:
        response = requests.get(url + "/customerSearch?entity_typeid=" + customer_type_id + "&from_time=" + start_from)
        data = response.json()
        
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Customer", {"customer_name": item.get("Name")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Customer")
                        new_doc.customer_name = str(item.get("Name"))
                        new_doc.customer_type = "Individual"
                        new_doc.custom_samba_id = item.get("Id")
                        new_doc.territory = "All Territories"
                        new_doc.customer_group = get_group_for_customer(item.get("EntityTypeId")) or "Samba Customer"
                        
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Customer"
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Customer"
        new_doc.error = traceback.format_exc()
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()
        
def get_customer_contact():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/contactSearch")
        data = response.json()
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Contact", {"first_name": item.get("Id")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Contact")
                        new_doc.first_name = item.get("Id")
                        new_doc.is_primary_contact = 1
                        if item.get("CustomData"):
                            contact_list = get_details(item.get("CustomData"))
                            for contact in contact_list:
                                if contact.get("Name") == "Email" and contact.get("Value"):
                                    new_doc.append("email_ids", {
                                        "email_id": contact.get("Value"),
                                        "is_primary": 1
                                    })
                                if contact.get("Name") == "Phone" and contact.get("Value"):
                                    new_doc.append("phone_nos", {
                                        "phone": contact.get("Value"),
                                        "is_primary_phone": 1,
                                        "is_primary_mobile_no": 1
                                    })
                        new_doc.append("links", {
                                    "link_doctype": "Customer",
                                    "link_name": item.get("Name")
                                })
                            
                        new_doc.insert()
                      
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Contact"
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()
        
def get_group_for_customer(id):
    group_doc = frappe.db.get_all("Customer Group", filters={"custom_samba_id": id}, fields=["name"])
    
    if group_doc:
        return group_doc[0].get("name")
    

def get_details(customData):
    if customData:
        list_of_dicts  = json.loads(customData)
    
        return list_of_dicts