frappe.ui.form.on("Customer",{
    custom_create_in_sambapos:function(frm){
        if(!frm.doc.custom_created_in_sambapos == 1){
            updateSambaCustomer(frm)
        }
        else{
            frappe.msgprint("Customer Is Already Registered!")
        }
    }
})

// Define the delete_items function
function updateSambaCustomer(frm) {
    frappe.call({
        method: "sambaapi.api_methods.customer.create_customer", // Update this to your actual Python method path
        args: {
            message:{
                data:{
                    customer: frm.doc.name, // Pass any arguments needed by your Python method
                }
            }
        },
        callback: function (response) {
            frm.set_value("custom_created_in_sambapos", 1); // Properly update the field
        
            frm.save().then(() => {
                frappe.msgprint(__('Samba updated successfully!'));
                frm.refresh_field("custom_created_in_sambapos"); // Refresh the field after saving
            });

            // console.log(response)
            // if (response.status_code == 200) {
            //     frm.set_value("custom_created_in_sambapos", 1); // Properly update the field
        
            //     frm.save().then(() => {
            //         frappe.msgprint(__('Samba updated successfully!'));
            //         frm.refresh_field("custom_created_in_sambapos"); // Refresh the field after saving
            //     });
            // }
            
        },
        error: function (error) {
            frappe.msgprint(__('Failed to update Samba: ' + error.message));
        },
    });
}