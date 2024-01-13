import frappe
import requests
import traceback
import json
from datetime import datetime, date
from sambaapi.api_methods.utils import get_samba_url


def get_samba_sales(start, end):
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/saleSearch?start=" + start + "&end=" + end )
        data = response.json()
        if data:
            for key, value in data.items():
               
                doc_exists = frappe.db.exists("Sales Invoice", {"custom_samba_id": key})
                if not doc_exists:
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
                        new_doc.append("taxes", {
                            "charge_type": "On Net Total",
                            "account_head": "2301 - VAT - MIR",
                            "rate": 16,
                            "description": "VAT",
                            "included_in_print_rate": 1
                        })
                        
                        new_doc.append("taxes", {
                            "charge_type": "On Net Total",
                            "account_head": "2302 - CTL - MIR",
                            "rate": 2,
                            "description": "CTL",
                            "included_in_print_rate": 1
                        })
                        
                        
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
    
    response = requests.get(url + "/ticketSearch?start=" + start + "&end=" + end)
    data = response.json()
    
    if data:
        for item in data:
            if str(item.get("Id")) == str(key): 
                posting_time_and_date = item.get("Date")
                dt = datetime.strptime(posting_time_and_date, "%a, %d %b %Y %H:%M:%S %Z")
                posting_date = dt.strftime("%Y-%#m-%#d")
                posting_time = dt.strftime("%#H:%#M:%S")
                
    return posting_date, posting_time


        