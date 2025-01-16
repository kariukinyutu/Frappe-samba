import frappe
import requests
import traceback
from datetime import datetime, date
from sambaapi.api_methods.utils import get_samba_url

def get_samba_sales(start, end):
    url = get_samba_url()
    
    settings_doc = frappe.get_doc("Samba Branch Connection Settings", "Samba001-Soulbreeze Restaurant")
    try:
        response = requests.get(url + "/saleSearch?start_datetime=" + start + "&end_datetime=" + end )
    
        data = response.json()

        if data:
            for key, value in data.items():
                add_missing_items(value)
               
                doc_exists = frappe.db.exists("Sales Invoice", {"custom_samba_id": key})
        
                if not doc_exists:

                    tax_items_list = get_tax_settings()
                    
                    try:
                        posting_date, posting_time = get_posting_date(key)
                     
                    except:
                        print("failing")
                    
                    try:
                        new_doc = frappe.new_doc("Sales Invoice")
                        ticket_customer = get_sales_customer(key)
                        new_doc.customer = ticket_customer
                        new_doc.company = settings_doc.get("company")
                        new_doc.branch = settings_doc.get("branch")
                        new_doc.custom_samba_id = key
                        new_doc.set_posting_time = 1
                        new_doc.custom_is_samba_sales = 1
                        new_doc.posting_date = posting_date
                        new_doc.posting_time = posting_time
                        new_doc.due_date = posting_date
                        new_doc.selling_price_list = "Standard Selling"
                        
                        if len(tax_items_list):
                            for item in tax_items_list:
                                new_doc.append("taxes", item)
                        
                        for item_data in value:
                            new_doc.append("items",{
                                "item_code": item_data.get("item_code"), 
                                "item_name": item_data.get("item_code"),
                                "qty": item_data.get("qty"),
                                "rate": item_data.get("rate")
                            })
                        new_doc.insert()
                        new_doc.submit()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Sales Invoice"
                        new_doc.samba_id = key
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    print("exists")#add lofgic for update
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = traceback.format_exc()
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()

def get_sales_customer(ticket_id):
    sales_customer = "POS Customer"
    settings_doc = frappe.get_doc("Samba Branch Connection Settings", "Samba001-Soulbreeze Restaurant")
    skip_list = settings_doc.get("customer_group_skip_list")
    url = get_samba_url()
    
    response = requests.get(url + "/saleCustomerSearch?invoice_id=" + ticket_id)
    try:
        data = response.json()
        
        if not data:
            sales_customer = "POS Customer"
        # print(skip_list, data[0].get("EntityTypeId"), ticket_id, data[0].get("EntityName"))
        
        if not data[0].get("EntityTypeId") in skip_list:
            doc_exists = frappe.db.exists("Customer", {"customer_name": data[0].get("EntityName")})
            if doc_exists:
                sales_customer = data[0].get("EntityName")
            else:
                sales_customer = create_missing_sales_customer(data)   
    except:
        sales_customer = "POS Customer"
            
    return sales_customer

def create_missing_sales_customer(data):
    if not data[0].get("EntityName") in ["Customer", "Customers"]:
        try:
            new_doc = frappe.new_doc("Customer")
            new_doc.customer_name = data[0].get("EntityName")
            new_doc.customer_type = "Individual"
            new_doc.custom_samba_id = data[0].get("EntityId")
            new_doc.territory = "All Territories"
            new_doc.customer_group = "Samba Customer"
            
            new_doc.insert()
            
            frappe.db.commit()
        except:
            new_doc = frappe.new_doc("Samba Error Logs")
            new_doc.doc_type = "Customer"
            new_doc.samba_id = data[0].get("EntityId")
            new_doc.error = traceback.format_exc()
            new_doc.log_time = datetime.now()
            new_doc.insert()

            frappe.db.commit()
        
        return data[0].get("EntityName")

def add_missing_items(value):
    for item in value:
        doc_exists = frappe.db.exists("Item", {"item_code": item.get("item_code")})
        
        if not doc_exists:
            try:
                new_doc = frappe.new_doc("Item")
                new_doc.item_code = item.get("item_code")
                new_doc.item_name = item.get("item_code")
                new_doc.item_group = "Products"
                new_doc.stock_uom = "Nos"
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

def get_posting_date(key):
    url = get_samba_url()
    
    posting_date = ""
    posting_time = ""
    
    response = requests.get(url + "/ticketSearch?ticket_id=" + key)
    
    data = response.json()

    if data:
        try:
            posting_time_and_date = data[0].get("Date")
            dt = datetime.strptime(posting_time_and_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            posting_date = dt.strftime("%Y-%m-%d")
            posting_time = dt.strftime("%H:%M:%S")
        except:
            today = date.today()
            posting_date = today.strftime("%Y-%m-%d")
            posting_time = "00:00:00"
            
    return posting_date, posting_time

def get_tax_settings():
    tax_items_list = []
    settings_doc = frappe.get_doc("Samba Instance Connection Settings", "Samba Instance Connection Settings")
    if settings_doc.sales_taxes_and_charges:
        for item in settings_doc.sales_taxes_and_charges:
            tax_dict = {
                "charge_type": item.get("charge_type"),
                "account_head": item.get("account_head"),
                "rate": item.get("rate"),
                "description": item.get("description"),
                "included_in_print_rate": 1
            }
            
            if not tax_dict in tax_items_list:
                tax_items_list.append(tax_dict)
        
    return tax_items_list