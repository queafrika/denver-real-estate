frappe.ui.form.on("Employee", {
    refresh: function(frm) {
        frm.add_custom_button("Reassign Customers", function() {
            frappe.prompt([
                {
                    fieldname: "old_employee",
                    label: "Old Employee",
                    fieldtype: "Link",
                    options: "Employee",
                    reqd: 1,
                    default: frm.doc.name
                },
                {
                    fieldname: "new_employee",
                    label: "New Employee",
                    fieldtype: "Link",
                    options: "Employee",
                    reqd: 1
                }
            ],
            function(values) {
                frappe.call({
                    method: "real_estate.real_estate.util.reassign_all_customers",
                    args: {
                        old_employee: values.old_employee,
                        new_employee: values.new_employee
                    },
                    callback: function(response) {
                        if (!response.exc) {
                            frappe.msgprint({
                                title: __("Success"),
                                message: __("Customers reassigned successfully!"),
                                indicator: "green"
                            });
                            frm.reload_doc();
                        }
                    }
                });
            },
            __("Reassign Customers"),
            __("Submit"));
        }).addClass("btn-primary"); 
    }
});
