// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Kallat Plot", {
  refresh(frm) {
    if (frm.doc.__islocal) {
      return;
    }
    frm.events.add_goto_unit_sale_button(frm);
  },


  add_goto_unit_sale_button(frm) {
    frm.call({
      method: "get_unit_sale",
      doc: frm.doc,
      callback: (r) => {
        if (!r.message) {
          return;
        }
        frm.add_custom_button("Goto Unit Sale", () => {
          frappe.set_route("unit-sale", r.message);
        });
      },
    });
  },
});
