frappe.ui.form.on('Leave Application', {
    onload: function(frm) {
        console.log('Leave Application onload triggered');

        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('reject_reason') === 'true') {
            console.log('Reject reason detected in URL');

            setTimeout(() => {
                if (!frm.doc || !frm.doc.name) {
                    console.log('Form data not yet available');
                    return;
                }

                // Unhide the rejection reason field for input
                frm.set_df_property("custom_rejection_reason", "hidden", 0);
                frm.refresh_field("custom_rejection_reason");

                // Just to check if already rejected
                if (frm.doc.status === "Rejected") {
                    frappe.msgprint("The status of the leave has been updated to Rejected.");
                    return;
                }

                // Should show a prompt for rejection reason
                frappe.prompt(
                    [
                        {
                            label: "Rejection Reason",
                            fieldname: "custom_rejection_reason",
                            fieldtype: "Small Text",
                            reqd: 1
                        }
                    ],
                    (values) => {
                        console.log('Rejection reason values:', values);

                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Leave Application",
                                name: frm.doc.name,
                                fieldname: {
                                    "custom_rejection_reason": values.custom_rejection_reason,
                                    "status": "Rejected"
                                }
                            },
                            callback: function(response) {
                                if (!response.exc) {
                                    frappe.show_alert({
                                        message: "Your rejection reason has been submitted successfully. The leave status has been updated to Rejected.",
                                        indicator: "red"
                                    });

                                    localStorage.setItem(`leave_${frm.doc.name}_rejected`, "true");
                                    
                                    // Hide the field after providing the reason
                                    frm.set_df_property("custom_rejection_reason", "hidden", 1);
                                    frm.refresh_field("custom_rejection_reason");

                                    setTimeout(() => {
                                        const allowedHosts = [
                                            "amcco.co.ke"
                                        ];
                                        if (allowedHosts.includes(window.location.hostname)) {
                                            window.close();
                                        }
                                    }, 2000);
                                }
                            }
                        });
                    },
                    "Reject Leave",
                    "Submit Reason"
                );
            }, 500);
        }
    },
    validate: function(frm) {
        if (frm.doc.status === "Rejected" && !frm.doc.custom_rejection_reason) {
            frappe.throw(__("Please provide a rejection reason before rejecting the leave."));
        }
        let today = frappe.datetime.get_today(); 
        let leave_start_date = frm.doc.from_date;
        
        if (leave_start_date && !frm.doc.half_day) {
            let min_application_date = frappe.datetime.add_days(today, 2); // Calculate min-application date needed 

            if (leave_start_date <= min_application_date) {
                frappe.throw({
                    title: __(' Leave Policy'),
                    indicator: 'green',
                    message: __('KINDLY NOTE! You Must Apply For a Leave Three Days In Advance.')
                });
                frappe.validated = false; // This action prevents the leave form being saved
            }
        }
    }
});
