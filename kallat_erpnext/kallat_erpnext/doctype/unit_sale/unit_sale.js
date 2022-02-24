// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Unit Sale", {
  refresh: function (frm) {
    if (!frm.doc.date_time) {
      // Set now date
      frm.set_value("date_time", frappe.datetime.now_datetime());
    }

    if (frm.doc.docstatus === 1) {
      frm.add_custom_button("Goto Unit", () => {
        frappe.set_route("kallat-unit", frm.doc.unit);
      });

      if (frm.doc.status === "Booked") {
        frm.add_custom_button("Sign Agreement", () => {
          frm.events.show_agreement_form(frm);
        });
      }
    }
  },

  show_agreement_form(frm) {
    const d = new frappe.ui.Dialog({
      title: "Upload Agreement PDF",
      fields: [
        {
          label: "Agreement PDF",
          fieldtype: "Attach",
          reqd: 1,
          fieldname: "agreement_file",
        },
        {
          label: "Remarks",
          fieldtype: "Small Text",
          fieldname: "remarks",
        },
      ],
      primary_action_label: "Sign Agreement",
      primary_action(values) {
        if (!values.agreement_file) {
          frappe.msgprint("Please upload agreement file");
          return;
        }
        frm.call({
          method: "sign_agreement",
          doc: frm.doc,
          args: values,
          freeze: true,
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
  },
});
