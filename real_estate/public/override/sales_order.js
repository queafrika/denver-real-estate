// Copyright (c) 2023, Finesoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order', {
    onload: function(frm) {
        if (frm.doc.status === "Draft") {
            frm.page.set_indicator(__("Draft"), "orange");
        }
        else if (frm.doc.status === "Awaiting Offer Approval") {
            frm.page.set_indicator(__("Awaiting Offer Approval"), "blue");
        }
        else if (frm.doc.status === "Offer") {
            frm.page.set_indicator(__("Offer"), "blue");
        }
        else if (frm.doc.status === "Under Payment") {
            frm.page.set_indicator(__("Under Payment"), "blue");
        }
    },

    refresh: function(frm) {
        frappe.call({
            method: 'real_estate.real_estate.api.clients.get_approval_comment',
            args: {
                sales_order: frm.doc.name
            },
            callback: function(response) {
                if (response.message) {
                    frm.dashboard.add_comment(response.message, "orange", true);
                }
            }
        });

        if (frm.doc.sale_state == "Waiting Sale Approval" || frm.doc.sale_state == "Waiting Managers Approval") {
            frm.add_custom_button(__('Edit Agreement'), function() {
                
                    const url = '/agreement_editor/?sale=' + encodeURIComponent(frm.doc.name);
                    // Open the page. Use window.open to launch in a new tab, or window.location.href for the same tab
                    window.open(url, '_blank');
                
            });
        }

        if (frm.doc.sale_state == "Waiting Agreement Upload" || frm.doc.sale_state == "Waiting Sale Approval") {
            frm.add_custom_button(__('Agreement PDF'), function() {
                
                    const url = '/api/method/real_estate.real_estate.api.sales.download_agreement/?doc_name=' + encodeURIComponent(frm.doc.name);
                    // Open the page. Use window.open to launch in a new tab, or window.location.href for the same tab
                    window.open(url, '_blank');
                
            }, "Download");

            frm.add_custom_button(__('Agreement Docx'), function() {
                
                const url = '/api/method/real_estate.real_estate.api.sales.download_word_document/?doc_name=' + encodeURIComponent(frm.doc.name);
                // Open the page. Use window.open to launch in a new tab, or window.location.href for the same tab
                window.open(url, '_blank');
                
            }, "Download");
        }

        // Check if the Sales Order has a specific status or any custom logic to show the indicator
        if (frm.doc.status === "Draft") {
            frm.page.set_indicator(__("Draft"), "orange");
        }
        else if (frm.doc.status === "Under Payment") {
            frm.page.set_indicator(__("Under Payment"), "blue");
        }
    }
});
