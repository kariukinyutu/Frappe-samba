frappe.ui.form.on("Customer",{
    onload:function(frm){
        console.log("loading----1")
        frm.page.add_action_item('Update Samba', () => updateSambaCustomer(frm), true)

    },
    // refresh:function(frm){
    //     console.log("loading----2")
    //     page.add_action_item('Delete', () => delete_items())

    // }


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
            if (response.message) {
                frappe.msgprint(__('Samba updated successfully!'));
            }
        },
        error: function (error) {
            frappe.msgprint(__('Failed to update Samba: ' + error.message));
        },
    });
}