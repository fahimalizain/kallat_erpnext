// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Type', {
	setup: function(frm) {
		frm.set_query("expense_account", function() {
			return {
				filters: {
					is_group: 0,
					root_type: "Expense"
				}
			}
		})
	}
});
