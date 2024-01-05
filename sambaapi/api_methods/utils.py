import frappe

def get_samba_url():
    url_doc = frappe.get_doc("Samba Instance Connection Settings", "Samba Instance Connection Settings")
    if url_doc:
        if url_doc.samba_connector_url:
            
            return url_doc.samba_connector_url
    
def get_company():
    settings_doc = frappe.get_doc("Samba Instance Connection Settings", "Samba Instance Connection Settings")
    if settings_doc:
        if settings_doc.company:
            
            return settings_doc.company