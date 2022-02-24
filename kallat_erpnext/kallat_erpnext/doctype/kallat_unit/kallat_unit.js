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
    if (frm.doc.__islocal) {
      return;
    }
    frm.events.add_update_status_button(frm);
    frm.events.add_goto_unit_sale_button(frm);
  },

  add_update_status_button(frm) {
    const statusIdx = kallat.unit_statuses.indexOf(frm.doc.status);
    if (statusIdx + 1 >= kallat.unit_statuses.length) {
      console.log("At final status now");
      return;
    }
    const nextStatus = kallat.unit_statuses[statusIdx + 1];

    frm.add_custom_button("Update Status", () => {
      const d = new frappe.ui.Dialog({
        title: "Update Unit Status",
        fields: [
          {
            label: "Next Status",
            fieldtype: "Data",
            read_only: 1,
            fieldname: "new_status",
            default: nextStatus,
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
            freeze: true,
            args: values,
            callback(r) {
              if (r.exc) {
                frappe.msgprint(
                  "Something went wrong! Please try again or Contact Developer"
                );
              } else {
                frappe.msgprint("Status Updated!");
                setTimeout(() => {
                  location.reload();
                }, 2000);
                d.hide();
              }
            },
          });
        },
      });

      d.show();
    });
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
