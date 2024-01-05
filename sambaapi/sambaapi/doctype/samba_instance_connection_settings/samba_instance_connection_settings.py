# Copyright (c) 2023, dev@opensource and contributors
# For license information, please see license.txt
import asyncio
import frappe, traceback
from frappe.model.document import Document
from datetime import datetime

from sambaapi.api_methods.stock import get_warehouse, get_menu_item_group, get_menu_item
from sambaapi.api_methods.customer import get_customer_groups, get_customer, get_sales_customer, get_customer_contact
from sambaapi.api_methods.sales import get_samba_sales
from sambaapi.api_methods.payments import get_mode_of_payments, get_sales_payments

class SambaInstanceConnectionSettings(Document):
    @frappe.whitelist()
    def setup_erpnext(self):
        if self.samba_connector_url:
            try:
                get_warehouse()
                get_menu_item_group()
                get_menu_item()
                get_customer_groups()
                # create_pos_customer()
                # get_customer()
                # get_sales_customer()
                # get_customer_contact()
                self.connected = 1
                
            except:
                frappe.throw("Something went wrong")
                
    @frappe.whitelist()
    def get_sales(self):
        start_datetime = self.sales_from_date
        end_datetime = self.sales_to_date
        start_str = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        str_start = datetime.strftime(start_str, "%Y-%m-%dT%H:%M:%S")
        end_str = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
        str_end = datetime.strftime(end_str, "%Y-%m-%dT%H:%M:%S")
        
        print(str_start, str_end)
        if self.sales_from_date and self.sales_to_date:
            try:
                get_samba_sales(start_datetime, end_datetime)
                
            except:
                frappe.throw("Something went wrong")
                
    
    @frappe.whitelist()
    def get_payments(self):
        start_datetime = self.payments_from_date
        end_datetime = self.payments_to_date
        if self.payments_from_date and self.payments_to_date:
            try:
                get_mode_of_payments()
                get_sales_payments(start_datetime, end_datetime)
                
            except:
                frappe.throw("Something went wrong")            
            
def create_pos_customer():
    doc_exists = frappe.db.exists("Customer", {"customer_name": "POS Customer"})
    if not doc_exists:
        try:
            new_doc = frappe.new_doc("Customer")
            new_doc.customer_name = "POS Customer"
            new_doc.customer_type = "Company"
            new_doc.territory = "All Territories"
            new_doc.customer_group = "All Customer Groups"
            
            new_doc.insert()
            
            frappe.db.commit()
        except:
            new_doc = frappe.new_doc("Samba Error Logs")
            new_doc.doc_type = "POS Customer"
            new_doc.error = traceback.format_exc()
            new_doc.log_time = datetime.now()
            new_doc.insert()

            frappe.db.commit()