from datetime import datetime, time, timedelta
import traceback

import frappe

from sambaapi.api_methods.sales import get_samba_sales
from sambaapi.api_methods.payments import get_sales_payments

def get_connection_details():
    settings = frappe.get_doc("Samba API Settings", "Samba API Settings")
    connection_dict = {}
    con_list = []
    
    if settings.get("allow_cron_jobs") == 1:
        connection_dict["allow_cron_jobs"] = 1
        if settings.get("configs"):
            
            for config in settings.get("configs"):
                if config.get("active") == 1:
                    if not config.get("connection_record") in con_list:
                        con_list.append(config.get("connection_record"))
                        
            connection_dict["connections"] = con_list
                    
    return connection_dict
      
def get_sales():
    connections = get_connection_details()
    if connections.get("allow_cron_jobs") == 1:
        if connections.get("connections"):
            for url in connections.get("connections"):
                start_of_day = datetime.combine(datetime.now().date(), time(00, 00, 00))
                start_of_daytime = datetime.combine(start_of_day,  time(00, 00, 00))
                end_of_day = start_of_day + timedelta(days=1)
  
                str_date_start = datetime.strftime(start_of_daytime, "%Y-%m-%d %H:%M:%S")
                str_date_end = datetime.strftime(end_of_day, "%Y-%m-%d %H:%M:%S")

                try:
                    frappe.enqueue(get_samba_sales, queue = 'long', is_async=True, start = str_date_start, end = str_date_end, url = url)
                except:
                    print("not enquing....")
                    new_doc = frappe.new_doc("Samba Error Logs")
                    new_doc.doc_type = "Sales Invoice Cron"
                    new_doc.error = traceback.format_exc()
                    new_doc.log_time = datetime.now()
                    new_doc.insert()

                    frappe.db.commit()
        
def get_payments():
    connections = get_connection_details()
    
    if connections.get("allow_cron_jobs") == 1:
        if connections.get("connections"):
            for url in connections.get("connections"):
                start_of_day = datetime.combine(datetime.now().date(), time(00, 00, 00))
                start_of_daytime = datetime.combine(start_of_day,  time(00, 00, 00))
                end_of_day = start_of_day + timedelta(days=1)
                
                str_start = datetime.strftime(start_of_daytime, "%Y-%m-%d %H:%M:%S")
                str_end = datetime.strftime(end_of_day, "%Y-%m-%d %H:%M:%S")

                try:
                    frappe.enqueue(get_sales_payments, queue = 'long', is_async=True, start_time = str_start, end_time = str_end, url = url)
                except:
                    new_doc = frappe.new_doc("Samba Error Logs")
                    new_doc.doc_type = "Payment Entry Cron"
                    new_doc.error = traceback.format_exc()
                    new_doc.log_time = datetime.now()
                    new_doc.insert()

                    frappe.db.commit()
                