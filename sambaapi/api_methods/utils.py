import frappe
    
def get_company(url):
    settings_doc = frappe.get_doc("Samba Branch Connection", url)
    if settings_doc:
        if settings_doc.company:
            
            return settings_doc.company
        
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