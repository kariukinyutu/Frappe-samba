import requests
import frappe

@frappe.whitelist(allow_guest=True)
def loanRequest():  
    if not frappe.form_dict.message:
        frappe.throw("Missing 'message' in request data")

    raw_data = frappe.form_dict.message
    data = raw_data.get("data")
    request_url = raw_data.get("url")
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
          "originatorRequestId": data.get("originatorRequestId"),
          "clientId": data.get("clientId"),
          "loanAmount": data.get("loanAmount"),
          "loanTerm":  data.get("loanTerm"),
          "product": data.get("product"),
          "destinationAccount": data.get("destinationAccount"),
          "channel": data.get("channel"),
          "narration": data.get("narration"),
          "callbackUrl": data.get("callbackUrl")
        }

    response = requests.post(url=request_url, json=payload, headers=headers)
    response_json = response.json()
    response_json["status_code"] = response.status_code
    
    return response_json
    
@frappe.whitelist(allow_guest=True)
def creditLimit():
    if not frappe.form_dict.message:
        frappe.throw("Missing 'message' in request data")

    raw_data = frappe.form_dict.message
    data = raw_data.get("data")  
    
    request_url = data.get("url")
   
    response = requests.get(url=request_url)
    response_json = response.json()
    response_json["status_code"] = response.status_code
        
    return response_json
    
@frappe.whitelist(allow_guest=True)
def loanBalance():
    if not frappe.form_dict.message:
        frappe.throw("Missing 'message' in request data")

    raw_data = frappe.form_dict.message
    data = raw_data.get("data")  
    
    request_url = data.get("url") 

    response = requests.get(url=request_url)
    response_json = response.json()
    response_json["status_code"] = response.status_code
    
    return response_json

    
@frappe.whitelist(allow_guest=True)
def loanRepayment():  
    if not frappe.form_dict.message:
        frappe.throw("Missing 'message' in request data")

    raw_data = frappe.form_dict.message
    data = raw_data.get("data")
    
        
    request_url = "http://89.38.97.47:8080/MaishaBankIntegration/onit/loanRepayment"
    headers = {"Content-Type": "application/json"}
    
    payload = {
            "originatorRequestId":"010101010101-AD",
            "sourceAccount":" " ,
            "channel": "ONIT",
            "amount": 0,
            "product": "M001",
            "narration": " ",
            "callbackUrl": "https://0zr6f91g-8000.uks1.devtunnels.ms/api/method/sambaapi.api_methods.api.callback"
        }

    # response = frappe.make_post_request(url=request_url, json=payload, headers=headers)
    response = requests.post(url=request_url, json=payload, headers=headers)
    
    return response.json()
    