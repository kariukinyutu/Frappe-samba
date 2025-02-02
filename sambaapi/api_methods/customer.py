import frappe, requests, traceback, json
from urllib.parse import urlencode

from datetime import datetime

from sambaapi.api_methods.utils import get_connection_details

def get_customer_groups(url):
    
    try:
        response = requests.get(url + "/customerGroupSearch")
        data = response.json()
    
        if len(data):
            for item in data:
                if item.get("EntityName") in ["Customer", "Customers"]:
                    item["EntityName"] = "Walkin Customer"
                    
                doc_exists = frappe.db.exists("Customer Group", {"customer_group_name": item.get("EntityName")})
                    
                if not doc_exists:
                    if not item.get("EntityName") in ["Customer", "Customers"]:
                        try:
                            new_doc = frappe.new_doc("Customer Group")
                            new_doc.customer_group_name = item.get("EntityName")
                            new_doc.custom_samba_id = item.get("Id")
                            # new_doc.parent_customer_group = "All Customer Groups"
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

def get_customer(customer_type_id, start_from, url):

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
        
def get_customer_contact(url):
    
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
    
    
@frappe.whitelist()
def create_customer():
    if not frappe.form_dict.message:
        frappe.throw("Missing 'message' in request data")

    raw_data = frappe.form_dict.message

    if isinstance(raw_data, str):
        raw_data = json.loads(raw_data)

    data = raw_data.get("data")

    if not data or not data.get("customer"):
        frappe.throw("Missing 'customer' field in the request data")

    customer_id = data.get("customer")
    
    # SQL query to fetch customer details 
    query = """
        SELECT
            customer.customer_name AS customer_name,
            customer_group.custom_samba_id AS entity_type_id,
            customer.modified as last_update_time,
            customer.email_id AS email,
            customer.custom_idpassport AS passport_id,
            customer.mobile_no AS mobile_no
        FROM 
            `tabCustomer` AS customer
        LEFT JOIN
            `tabCustomer Group` AS customer_group
        ON
            customer_group.name = customer.customer_group
        WHERE 
            customer.name = %s
    """

    results = frappe.db.sql(query, customer_id, as_dict=True)

    processed_data = process_results(results)
    
    send_customer_info(processed_data)

def process_results(results):
    if results:
        if results[0].get("last_update_time"):
           update_datetime_str = datetime.strftime(results[0].get("last_update_time"), "%Y-%M-%d %H:%M:%S")
           
           results[0]["last_update_time"] = update_datetime_str
           
    return results
                   
def send_customer_info(data):
    if len(data):
        connections = get_connection_details()
        if connections.get("allow_cron_jobs") == 1:
            if connections.get("connections"):
                for url in connections.get("connections"):                  
                    # Step 1: Replace single quotes with double quotes to make it JSON-compatible
                    data_string = json.dumps(data[0], indent=4)

                    json_compatible_string = data_string.replace("'", '"')

                    # Step 2: Parse the JSON-compatible string into a Python dictionary
                    data_dict = json.loads(json_compatible_string)

                    # Step 3: Convert the Python dictionary back to a JSON string (formatted)
                    json_string = json.dumps(data_dict, indent=4)
                                        
                    try:
                        # Send the request
                        response = requests.post(f"{url}/addCustomer?data={json_string}")

                        # Check response status
                        if response.status_code == 200:
                            print("Customer created successfully!")
                        else:
                            print(f"Failed to create customer. Response: {response.text}")

                    except requests.exceptions.RequestException as e:
                        print(f"Error occurred: {e}")
                        frappe.throw("Customer Not Created")