// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unit Sale', {
	refresh: function (frm) {
		if (!frm.doc.date_time) {
			// Set now date
			frm.set_value("date_time", new Date())
		}
	}
});
