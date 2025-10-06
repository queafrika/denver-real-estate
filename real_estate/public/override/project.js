

frappe.ui.form.on('Project', {
	
	refresh: function(frm) {
		console.log("hello there")	
		if (!frm.is_new() && frm.doc.plots.length < 1) {
			frm.add_custom_button(
				__("Create Plots"), () => frm.events.create_plots(frm),
			)
		}
	},

	create_plots: function(frm) {
		const fields = [
			{
				"fieldname": "qty",
				"fieldtype": "Int",
				"label": "Number of Plots",
				"reqd": 1
			},
			{
				"fieldname": "cash_price",
				"fieldtype": "Currency",
				"label": "Cash Price",
				"reqd": 1
			},
			{
				"fieldname": "installment_price",
				"fieldtype": "Currency",
				"label": "Installment Price",
				"reqd": 0
			},
			{
				"fieldname": "plot_size",
				"fieldtype": "Data",
				"label": "Plot Size",
				"reqd": 0
			},
			{
				"fieldname": "purchase_invoice",
				"fieldtype": "Link",
				"label": "Purchase Invoice",
				"options": "Purchase Invoice",
				"get_query": function() {
					return {
						"filters": [
							['Project', '=', frm.doc.name],
						]
					}
				},
				"reqd": 1
			},
			{
				"fieldname": "numbering",
				"fieldtype": "Select",
				"label": "Plot Numbers Type",
				"options": "Numeric\n Alphabetic",
				"default": "Numeric",
				"reqd": 1
			},
		];


		frappe.prompt(fields, (values)=>{
			frappe.call({
				method:
				"real_estate.real_estate.api.util.generate_plots",
				args: {
					qty: values.qty,
					cash_price: values.cash_price,
					installment_price: values.installment_price,
					numbering: values.numbering,
					purchase_invoice: values.purchase_invoice,
					plot_size: values.plot_size,
					project: frm.doc.name
				},
				callback: function(data){
					if(!data.exc){
						frm.reload_doc();
					}
				}
			});

		}, __("Generate Plots"), __("Generate"))
	}
});
