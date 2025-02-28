import frappe, requests, traceback
from datetime import datetime
from sambaapi.api_methods.utils import get_company

def get_warehouse(url):
    
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
                        new_doc.custom_samba_id = item.get("Id")
                        new_doc.company = get_company(url)
                      
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
                    warehouse_doc = frappe.get_doc("Warehouse", doc_exists)
                    warehouse_doc.custom_samba_id = item.get("Id")
                    
                    warehouse_doc.save()
                    frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()


def get_menu_item_group(url):
    
    try:
        response = requests.get(url + "/menuItemSearch")
        data = response.json()
        if len(data):
            for item in data:
                if item.get("GroupCode"):
                    doc_exists = frappe.db.exists("Item Group", {"item_group_name": item.get("GroupCode")})
                    if not doc_exists:
                        try:
                            new_doc = frappe.new_doc("Item Group")
                            new_doc.item_group_name = item.get("GroupCode")
                            new_doc.custom_samba_id = item.get("Id")
                            
                            new_doc.insert()
                            
                            frappe.db.commit()
                        except:
                            new_doc = frappe.new_doc("Samba Error Logs")
                            new_doc.doc_type = "Item Group"
                            new_doc.samba_id = item.get("Id")
                            new_doc.error = traceback.format_exc()
                            new_doc.log_time = datetime.now()
                            new_doc.insert()

                            frappe.db.commit()
                    else:
                        item_grp_doc = frappe.get_doc("Item Group", doc_exists)
                        item_grp_doc.custom_samba_id = item.get("Id")
                        
                        item_grp_doc.save()
                        frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()
    
    
def get_menu_item1(url):
    
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
                        new_doc.item_group = item.get("GroupCode") or "Products"
                        # new_doc.stock_uom = "Nos"
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Item"
                        new_doc.samba_id = item.get("Id")
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    item_doc = frappe.get_doc("Item", doc_exists)
                    item_doc.custom_samba_id = item.get("Id")
                    
                    item_doc.save()
                    frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()


def log_error(doc_type, samba_id=None, error_message=None):
    """Helper function to log errors."""
    error_log = frappe.new_doc("Samba Error Logs")
    error_log.doc_type = doc_type
    error_log.samba_id = samba_id
    error_log.error = error_message or traceback.format_exc()
    error_log.log_time = datetime.now()
    error_log.insert()
    frappe.db.commit()

def create_or_update_item(item):
    """Helper function to create or update an Item document."""
    doc_exists = frappe.db.exists("Item", {"item_code": item.get("Name")})
    uom_exists = frappe.db.exists("UOM", {"name": item.get("UOM")})
    
    if not uom_exists:
        new_uom = frappe.new_doc("UOM")
        new_uom.uom_name = item.get("UOM")
   
        new_uom.save()
        frappe.db.commit() 
    
    if not doc_exists:
        # Create a new Item
        new_doc = frappe.new_doc("Item")
        new_doc.item_code = item.get("Name")
        new_doc.item_name = item.get("Name")
        new_doc.stock_uom = item.get("UOM")
        new_doc.custom_samba_id = str(item.get("Id"))
        new_doc.item_group = item.get("GroupCode") or "Products"
        try:
            new_doc.save()
            frappe.db.commit()
        except:
            log_error("Item", item.get("Id"))
    else:
        # Update the existing Item
        item_doc = frappe.get_doc("Item", doc_exists)
        if not item_doc.custom_samba_id == str(item.get("Id")):
            item_doc.custom_samba_id = item.get("Id")
            item_doc.UOM = item.get("UOM")
            item_doc.save()
            frappe.db.commit()

def get_menu_item(url):
    """Fetch menu items from the given URL and update Frappe records."""
    try:
        response = requests.get(f"{url}/menuItemSearch")
        response.raise_for_status()
        data = response.json()
        
        if data:
            for item in data:
                create_or_update_item(item)
    except requests.RequestException:
        log_error("Connection", error_message="Connection Error")