// Copyright (c) 2025, dev@opensource and contributors
// For license information, please see license.txt

frappe.ui.form.on("Samba Branch Connection Settings", {
	// refresh(frm) {

	// },
    connect: function(frm){
        // call with all options
        frappe.call({
            method: 'setup_erpnext',
            doc: frm.doc,
            // // disable the button until the request is completed
            btn: $('.primary-action'),
            // // freeze the screen until the request is completed
            freeze: true,
            callback: function(r)   {
                refresh_field("connected")
            }
        })

        doc.save()
    },
    get_room_customers: function(frm){
        // call with all options
        frappe.call({
            method: 'get_room_customers',
            doc: frm.doc,
            // // disable the button until the request is completed
            btn: $('.primary-action'),
            // // freeze the screen until the request is completed
            freeze: true,
            callback: function(r)   {
                
                // refresh_field("connected")
            }
        })

        doc.save()
    },
    get_sales: function(frm){
        // call with all options
        frappe.call({
            method: 'get_sales',
            doc: frm.doc,
            // // disable the button until the request is completed
            btn: $('.primary-action'),
            // // freeze the screen until the request is completed
            freeze: true,
            callback: function(r)   {
                // refresh_field("connected")
            }
        })

        doc.save()
    },
    get_payments: function(frm){
        // call with all options
        frappe.call({
            method: 'get_payments',
            doc: frm.doc,
            // // disable the button until the request is completed
            btn: $('.primary-action'),
            // // freeze the screen until the request is completed
            freeze: true,
            callback: function(r)   {
                // refresh_field("connected")
            }
        })

        doc.save()
    }
});
