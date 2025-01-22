import frappe
    
def get_company(url):
    settings_doc = frappe.get_doc("Samba Branch Connection", url)
    if settings_doc:
        if settings_doc.company:
            
            return settings_doc.company