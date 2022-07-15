// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Entry', {
	refresh: function (frm) {
		frm.set_query("credit_account", function () {
			return {
				filters: {
					is_group: 0,
					account_type: ["IN", ["Bank", "Cash", "Receivable"]]
				}
			}
		})
	},
	calculate_total_amount: function (frm) {
		let total = 0;
		for (const item of frm.doc.items) {
			item.amount = Math.max(0, flt(item.amount, 2))
			total += item.amount;
		}
		frm.set_value("total_amount", flt(total, 2))
	}
});


frappe.ui.form.on("Expense Entry Item", {
	items_add: function (frm) {
		frm.events.calculate_total_amount(frm);
	},
	items_remove: function (frm) {
		frm.events.calculate_total_amount(frm);

	},
	amount: function (frm) {
		frm.events.calculate_total_amount(frm);

	}
})