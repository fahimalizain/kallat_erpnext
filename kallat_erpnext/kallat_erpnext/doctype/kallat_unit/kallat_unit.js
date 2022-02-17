// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.provide("kallat");
kallat.unit_statuses = [
  "Empty Plot",
  "Foundation Completed",
  "1st Floor Slab Completed",
  "Structure Completed",
  "Tiling Completed",
  "Hand Over Completed",
];

frappe.ui.form.on("Kallat Unit", {
  refresh(frm) {
    frm.events.add_update_status_button(frm);
  },

  add_update_status_button(frm) {
    frm.add_custom_button("Update Status", () => {
      const d = new frappe.ui.Dialog({
        title: "Update Unit Status",
        fields: [
          {
            label: "New Status",
            fieldtype: "Select",
            fieldname: "new_status",
            options: kallat.unit_statuses.join("\n"),
            default: frm.doc.status,
          },
          {
            label: "Remarks",
            fieldtype: "Small Text",
            fieldname: "remarks",
          },
        ],
        primary_action_label: "Update",
        primary_action(values) {
          frm.call({
            method: "update_status",
            doc: frm.doc,
            args: values,
            callback(r) {
              if (r.exc) {
                frappe.msgprint(
                  "Something went wrong! Please try again or Contact Developer"
                );
              } else {
                frappe.msgprint("Status Updated!");
                d.hide();
              }
            },
          });
        },
      });

      d.show();
    });
  },
});
