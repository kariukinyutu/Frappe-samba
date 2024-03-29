from datetime import datetime, time, timedelta
import traceback

import frappe

from sambaapi.api_methods.sales import get_samba_sales
from sambaapi.api_methods.payments import get_mode_of_payments, get_sales_payments

def get_sales():
    start_of_day = datetime.combine(datetime.now().date(), time(00, 00, 00))
    start_of_daytime = datetime.combine(start_of_day,  time(00, 00, 00))
    end_of_day = start_of_day + timedelta(days=1)
    
    str_start = datetime.strftime(start_of_daytime, "%Y-%m-%d %H:%M:%S")
    str_end = datetime.strftime(end_of_day, "%Y-%m-%d %H:%M:%S")

    try:
        get_samba_sales(str_start, str_end)
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Sales Invoice Cron"
        new_doc.error = traceback.format_exc()
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()
        
# def get_payments():
#     start_of_day = datetime.combine(datetime.now().date(), time(00, 00, 00))
#     start_of_daytime = datetime.combine(start_of_day,  time(00, 00, 00))
#     end_of_day = start_of_day + timedelta(days=1)
    
#     str_start = datetime.strftime(start_of_daytime, "%Y-%m-%d %H:%M:%S")
#     str_end = datetime.strftime(end_of_day, "%Y-%m-%d %H:%M:%S")

#     try:
#         get_samba_sales(str_start, str_end)
#     except:
#         new_doc = frappe.new_doc("Samba Error Logs")
#         new_doc.doc_type = "Sales Invoice Cron"
#         new_doc.error = traceback.format_exc()
#         new_doc.log_time = datetime.now()
#         new_doc.insert()

#         frappe.db.commit()
    