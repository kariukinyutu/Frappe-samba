import frappe
import requests
import traceback
from datetime import datetime
from sambaapi.api_methods.utils import get_samba_url


def get_mode_of_payments():
    url = get_samba_url()
    
    try:
        response = requests.get(url + "/mopSearch")
        data = response.json()
        if len(data):
            for item in data:
                print(item.get("Name"))
                doc_exists = frappe.db.exists("Mode of Payment", {"mode_of_payment": item.get("Name")})
                if not doc_exists:
                    try:
                        new_doc = frappe.new_doc("Mode of Payment")
                        new_doc.mode_of_payment = item.get("Name")
                        new_doc.custom_samba_id = item.get("Id")
                        new_doc.insert()
                        
                        frappe.db.commit()
                    except:
                        new_doc = frappe.new_doc("Samba Error Logs")
                        new_doc.doc_type = "Mode of Payment"
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


def get_sales_payments(start_time, end_time):
    url = get_samba_url()
    ticket_id_list = get_pending_tickets()
    
    try:
        response = requests.get(url + "/paymentSearch?start=" + start_time + "&end=" + end_time)
        data = response.json()
        if len(data):
            print(data)
            for item in data:
                ticket_id = str(item.get("TicketId"))
                id = str(item.get("Id"))
                
                dt = datetime.strptime(item.get("Date"), "%a, %d %b %Y %H:%M:%S %Z")
                posting_date = dt.strftime("%Y-%#m-%#d")
                
                if ticket_id in ticket_id_list:
                    doc_exists = frappe.db.exists("Payment Entry", {"custom_samba_id": id, "docstatus":["!=", 2]})
                    if not doc_exists:
                        try:
                            new_doc = frappe.new_doc("Payment Entry")
                            new_doc.payment_type = "Receive"
                            # new_doc.company = get_erp_company(),
                            new_doc.posting_date = posting_date
                            new_doc.mode_of_payment = get_mop(item.get("PaymentTypeId"))
                            new_doc.custom_samba_id = item.get("Id")
                            new_doc.custom_samba_ticket_id = item.get("TicketId")
                            new_doc.party_type = "Customer"
                            new_doc.paid_to = "Cash - S"
                            new_doc.paid_to_account_currency = "KES"
                            new_doc.party = get_invoice_customer(item.get("TicketId"))
                            new_doc.paid_amount = float(item.get("Amount"))
                            new_doc.received_amount = float(item.get("Amount"))
                            new_doc.target_exchange_rate = 1
                            # new_doc.docstatus = 1
                            # print(new_doc.__dict__)
                            new_doc.insert()
                            frappe_doc = frappe.get_doc("Payment Entry", new_doc.name)
                            
                            add_outstanding_sales(frappe_doc)
                            
                            frappe.db.commit()
                        except:
                            new_doc = frappe.new_doc("Samba Error Logs")
                            new_doc.doc_type = "Payment Entry"
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

def get_pending_tickets():
    ticket_id_list = []
    sale_docs_ids = frappe.db.get_all("Sales Invoice", filters={"custom_is_samba_sales":1, "status":["!=", "Paid"]}, fields=["custom_samba_id"])
    if sale_docs_ids:
        for doc in sale_docs_ids:
            if not doc.get("custom_samba_id") in ticket_id_list:
                ticket_id_list.append(str(doc.get("custom_samba_id")))

    return ticket_id_list
    
def get_invoice_customer(ticket_id):
    str_ticket_id = str(ticket_id)
    
    sale_docs_ids = frappe.db.get_all("Sales Invoice", filters={"custom_samba_id": str_ticket_id}, fields=["customer"])
    if sale_docs_ids:
        
        return sale_docs_ids[0].get("customer")
    
def add_outstanding_sales(doc):
    if doc.party and doc.paid_amount:
        if doc.custom_samba_ticket_id:
            invoice = frappe.get_last_doc("Sales Invoice", filters={"custom_samba_id":doc.custom_samba_ticket_id})
            
            if invoice:
                pay_amount = doc.paid_amount
                if invoice.get("grand_total") > pay_amount:
                    invoice_appended = False
                    for item in doc.references:
                        if item.get("reference_name") == invoice.name:
                            item.allocated_amount = pay_amount
                            item.due_date = invoice.due_date
                            invoice_appended = True
                            
                    if not invoice_appended == True:
                        doc.append("references",
                        {
                            "reference_doctype": "Sales Invoice",
                            "reference_name": invoice.name,
                            "allocated_amount": pay_amount,
                            "due_date": invoice.due_date
                        })
                    
                    # doc.save() 
                    # doc.submit()    
                    
                if invoice.get("grand_total") <= pay_amount:
                    invoice_appended = False
                    for item in doc.references:
                        if item.get("reference_name") == invoice.name:
                            item.allocated_amount = invoice.grand_total
                            item.due_date = invoice.due_date
                            invoice_appended = True
                            
                    if not invoice_appended == True:
                        doc.append("references",
                        {
                            "reference_doctype": "Sales Invoice",
                            "reference_name": invoice.name,
                            "allocated_amount": invoice.grand_total,
                            "due_date": invoice.due_date
                        })
            
                doc.save() 
                doc.submit()    
                 
def get_mop(pay_id):
    mop = "Cash"
    pay_type_id = str(pay_id)
    mop_docs = frappe.db.get_all("Mode of Payment", filters={"custom_samba_id": pay_type_id}, fields=["mode_of_payment"])
    
    if mop_docs:
        
        mop = mop_docs[0].get("mode_of_payment")
            
    return mop
            

    