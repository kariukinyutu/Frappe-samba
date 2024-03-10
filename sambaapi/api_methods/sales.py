import frappe
import requests
import traceback
from datetime import datetime, date
from sambaapi.api_methods.utils import get_samba_url


def get_samba_sales(start, end):
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/saleSearch?start_datetime=" + start + "&end_datetime=" + end )
        data = response.json()
        if data:
            for key, value in data.items():
               
                doc_exists = frappe.db.exists("Sales Invoice", {"custom_samba_id": key})
                # print("*"*80)
                # print(data)
                if not doc_exists:
                    tax_items_list = get_tax_settings()
                    posting_date, posting_time = get_posting_date(key, start, end)
                    
                    try:
                        new_doc = frappe.new_doc("Sales Invoice")
                        new_doc.customer = "POS Customer"
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
                        # print(new_doc.__dict__)
                        new_doc.insert()
                        new_doc.submit()
                        
                        frappe.db.commit()
                    except:
                        # print(traceback.format_exc())
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
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()

def get_sales_customer(ticket_id):
    sales_customer = "POS Customer"
    
    url = get_samba_url()
    
    response = requests.get(url + "/saleCustomerSearch")
    data = response.json()
    
    if data:
        for item in data:
            if str(item.get("Ticket_Id")) == str(ticket_id):
                
                sales_customer = item.get("EntityName")

    
    return sales_customer


def get_posting_date(key, start, end):
    url = get_samba_url()
    posting_date = ""
    posting_time = ""
    
    response = requests.get(url + "/ticketSearch?start_datetime=" + start + "&end_datetime=" + end)
    data = response.json()

    if data:
        for item in data:
            if str(item.get("Id")) == str(key): 
                posting_time_and_date = item.get("Date")
                dt = datetime.strptime(posting_time_and_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                posting_date = dt.strftime("%Y-%m-%d")
                posting_time = dt.strftime("%H:%M:%S")
               
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