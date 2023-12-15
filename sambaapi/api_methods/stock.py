import frappe, requests, traceback
from datetime import datetime
from sambaapi.api_methods.utils import get_samba_url

def get_warehouse():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/warehouseSearch")
        data = response.json()
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Warehouse", {"warehouse_name": item.get("Name")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Warehouse")
                        new_doc.warehouse_name = item.get("Name")
                      
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Warehouse"
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    print("exists")#add lofgic for update
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()


def get_menu_item_group():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/menuItemSearch")
        data = response.json()
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Item Group", {"item_group_name": item.get("GroupCode")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Item Group")
                        new_doc.item_group_name = item.get("GroupCode")
                        
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Item Group"
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    print("exists")
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()
    
    
def get_menu_item():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/menuItemSearch")
        data = response.json()
        if len(data):
            for item in data:
                doc_exists = frappe.db.exists("Item", {"item_code": item.get("Name")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Item")
                        new_doc.item_code = item.get("Name")
                        new_doc.item_name = item.get("Name")
                        new_doc.custom_samba_id = item.get("Id")
                        new_doc.item_group = "Products"
                        new_doc.stock_uom = "Nos"
                        # print(new_doc.__dict__)
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Item"
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    print("exists")
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()

