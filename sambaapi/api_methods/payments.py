import frappe
import requests
import traceback
from datetime import datetime

def get_mode_of_payments(url):
    
    try:
        response = requests.get(url + "/mopSearch")
        data = response.json()
        if len(data):
            for item in data:
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
                        new_doc.samba_id = item.get("Id")
                        new_doc.error = traceback.format_exc()
                        new_doc.log_time = datetime.now()
                        new_doc.insert()

                        frappe.db.commit()
                else:
                    mop_doc = frappe.get_doc("Mode of Payment", item.get("Name"))
                    if not mop_doc.custom_samba_id:
                        mop_doc.custom_samba_id = item.get("Id")
                        
                        mop_doc.save()
                        frappe.db.commit()
    except:
        new_doc = frappe.new_doc("Samba Error Logs")
        new_doc.doc_type = "Connection"
        new_doc.error = "Connection Error"
        new_doc.log_time = datetime.now()
        new_doc.insert()

        frappe.db.commit()


def get_sales_payments(start_time, end_time, url):
    ticket_id_list = get_pending_tickets()
    settings_doc = frappe.get_doc("Samba Branch Connection", url)
    
    try:
        response = requests.get(url + "/paymentSearch?start_datetime=" + start_time + "&end_datetime=" + end_time)
        data = response.json()

        if len(data):
            for item in data:
                ticket_id = str(item.get("TicketId"))
                id = str(item.get("Id"))
            
                dt = datetime.strptime(item.get("Date"), "%Y-%m-%dT%H:%M:%S.%fZ")
                posting_date = dt.strftime("%Y-%#m-%#d")
            
                if ticket_id in ticket_id_list:
                    payment_info = get_payment_account(item.get("PaymentTypeId"), id, item.get("Date"), url)
                    
                    if payment_info.get("paid_to"):
                    
                        doc_exists = frappe.db.exists("Payment Entry", {"custom_samba_id": id, "docstatus":["!=", 2]})
                        if not doc_exists:
                            try:
                                new_doc = frappe.new_doc("Payment Entry")
                                new_doc.payment_type = "Receive"
                                # new_doc.company = get_erp_company(),
                                new_doc.posting_date = posting_date
                                new_doc.mode_of_payment = get_mop(item.get("PaymentTypeId")) or "Cash"
                                new_doc.custom_samba_id = item.get("Id")
                                new_doc.custom_samba_ticket_id = item.get("TicketId")
                                new_doc.party_type = "Customer"
                                new_doc.company = settings_doc.get("company")
                                new_doc.paid_to = payment_info.get("paid_to")
                                new_doc.reference_no = payment_info.get("reference_no")
                                new_doc.reference_date = payment_info.get("reference_date")
                                new_doc.paid_to_account_currency = "KES"
                                new_doc.party = get_invoice_customer(item.get("TicketId"))
                                new_doc.paid_amount = float(item.get("Amount"))
                                new_doc.received_amount = float(item.get("Amount"))
                                new_doc.target_exchange_rate = 1
                                # new_doc.docstatus = 1
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
                if pay_amount >= invoice.get("grand_total"):
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
                else:
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
                    doc.save() 
                    doc.submit()    
                 
def get_mop(pay_id):
    mop = "Cash"
    pay_type_id = str(pay_id)
    mop_docs = frappe.db.get_all("Mode of Payment", filters={"custom_samba_id": pay_type_id}, fields=["mode_of_payment"])
    
    if mop_docs:
        
        mop = mop_docs[0].get("mode_of_payment")
            
    return mop

def get_payment_account(pay_id, payment_id, cheque_date, url):
    payment_info = {}
    mop = ""
    pay_type_id = str(pay_id)
    mop_docs = frappe.db.get_all("Mode of Payment", filters={"custom_samba_id": pay_type_id}, fields=["mode_of_payment"])
    
    dt = datetime.strptime(cheque_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    posting_date = dt.strftime("%Y-%#m-%#d")
                
    if mop_docs:
        mop = mop_docs[0].get("mode_of_payment")
        
        settings_doc = frappe.get_doc("Samba Branch Connection", url)
        
        if mop in ["Cheque", "Credit Card", "Wire Transfer", "Bank Draft", "Visa"]:
            payment_info["paid_to"] = settings_doc.get("bank_account") #***********************************need change*************************************
            payment_info["reference_no"] = payment_id
            payment_info["reference_date"] = posting_date
        
        elif mop in ["Mpesa"]:
            payment_info["paid_to"] =  settings_doc.get("mpesa_account")#***********************************need change*************************************
            payment_info["reference_no"] = payment_id
            payment_info["reference_date"] = posting_date
        
        elif mop in ["Customer Account"]:
            payment_info["paid_to"] =  "" #***********************************need change*************************************
            payment_info["reference_no"] = ""
            payment_info["reference_date"] = ""
        
        else:
            payment_info["paid_to"] = settings_doc.get("cash_account") #***********************************need change*************************************
            payment_info["reference_no"] = ""
            payment_info["reference_date"] = ""

    return payment_info
    