// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.provide("kallat.unit_sale")

kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP = "Update";

frappe.ui.form.on("Unit Sale", {
  refresh: function (frm) {
    if (!frm.doc.date_time) {
      // Set now date
      frm.set_value("date_time", frappe.datetime.now_datetime());
    }

    $(frm.fields_dict["events_html"].wrapper).html(``);

    if (frm.doc.docstatus !== 1) {
      return;
    }

    frm.events.add_custom_buttons(frm);

    // make events_html
    frm.call({
      method: "get_events",
      doc: frm.doc,
      callback(r) {
        if (r.exc) {
          return;
        }
        kallat.unit_sale.make_events_html(frm, r.message);
      },
    });
  },

  add_custom_buttons(frm) {
    // Confirm
    if (frm.doc.status === "" || !frm.doc.status) {
      frm.add_custom_button(
        "Confirm Booking",
        () => {
          frappe.confirm("Are you sure to confirm the Booking ?", () => {
            frm.call({
              method: "confirm_booking",
              doc: frm.doc,
              freeze: true,
              callback(r) {
                if (r.exc) {
                  return;
                }
                frappe.msgprint("Booking Confirmed!");
                frm.reload_doc();
              },
            });
          });
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Sign Agreement
    else if (frm.doc.status === kallat.unit_sale.UNIT_SALE_STATUS.BOOKED) {
      frm.add_custom_button(
        "Sign Agreement",
        () => {
          kallat.unit_sale.show_agreement_form(frm);
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Work Progress Updates
    else if (
      frm.doc.status == kallat.unit_sale.UNIT_SALE_STATUS.WIP &&
      frm.doc.work_status != kallat.unit_sale.WORK_STATUS.TILING_COMPLETED
    ) {
      frm.add_custom_button(
        "Work Progress",
        () => {
          kallat.unit_sale.show_work_progress_form(frm);
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Handover
    else if (
      frm.doc.work_status == kallat.unit_sale.WORK_STATUS.TILING_COMPLETED &&
      frm.doc.status == kallat.unit_sale.UNIT_SALE_STATUS.WIP
    ) {
      frm.add_custom_button(
        "Hand Over Unit",
        () => {
          kallat.unit_sale.show_hand_over_form(frm);
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }

    // Payment Receipt
    if (frm.doc.total_balance > 0) {
      frm.add_custom_button(
        "Make Payment Receipt",
        () => {
          kallat.unit_sale.show_payment_receipt_form(frm);
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }

    // Extra Work
    if (frm.doc.status !== kallat.unit_sale.UNIT_SALE_STATUS.COMPLETED) {
      frm.add_custom_button(
        "Add Extra Work",
        () => {
          kallat.unit_sale.show_extra_work_form(frm);
        },
        kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
      );
    }
  },
});
