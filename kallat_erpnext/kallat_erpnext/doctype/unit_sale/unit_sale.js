// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.provide("kallat_erpnext");
kallat_erpnext.UNIT_SALE_TYPE = {
  PAYMENT_RECEIPT: "Payment Receipt",
  UNIT_SALE_UPDATE: "Unit Sale Update",
};

kallat_erpnext.UNIT_SALE_STATUS = {
  BOOKED: "Booked"
}

frappe.ui.form.on("Unit Sale", {
  refresh: function (frm) {
    if (!frm.doc.date_time) {
      // Set now date
      frm.set_value("date_time", frappe.datetime.now_datetime());
    }

    if (frm.doc.docstatus === 1) {
      if (frm.doc.status === "" || !frm.doc.status) {
        frm.add_custom_button("Confirm Booking", () => {
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
                setTimeout(() => {
                  location.reload();
                }, 2000);
              },
            });
          });
        });
      } else if (frm.doc.status === "Booked") {
        frm.add_custom_button("Sign Agreement", () => {
          frm.events.show_agreement_form(frm);
        });
      }

      if (frm.doc.balance_amount > 0) {
        frm.add_custom_button("Make Payment Receipt", () => {
          frm.events.show_payment_receipt_form(frm);
        });
      }

      // make events_html
      frm.call({
        method: "get_events",
        doc: frm.doc,
        callback(r) {
          if (r.exc) {
            return;
          }
          frm.events.make_events_html(frm, r.message);
        },
      });
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
          label: "Final Price",
          fieldtype: "Currency",
          reqd: 1,
          fieldname: "final_price",
          default: frm.doc.suggested_price,
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

  show_payment_receipt_form(frm) {
    const d = new frappe.ui.Dialog({
      title: "Payment Receipt",
      fields: [
        {
          label: "Amount Received",
          fieldtype: "Currency",
          fieldname: "amount_received",
          reqd: 1,
        },
        {
          label: "Remarks",
          fieldtype: "Small Text",
          fieldname: "remarks",
        },
      ],
      primary_action_label: "Make Receipt",
      primary_action(values) {
        if (!values.amount_received) {
          frappe.msgprint("Please specify amount received");
          return;
        }
        frm.call({
          method: "make_payment_receipt",
          doc: frm.doc,
          args: values,
          freeze: true,
          callback(r) {
            if (r.exc) {
              frappe.msgprint(
                "Something went wrong! Please try again or Contact Developer"
              );
            } else {
              frappe.msgprint("Payment Receipt Made!");
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

  make_events_html(frm, events) {
    const getEventTypePill = (event) => {
      let pillClass = "red";
      let pillText = event.type;
      if (event.type === kallat_erpnext.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
        pillClass = "gray";
        pillText = "Payment";
      } else if (event.type == kallat_erpnext.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
        if (event.new_status == kallat_erpnext.UNIT_SALE_STATUS.BOOKED) {
          pillClass = "green"
          pillText = "Booking Confirmed"
        }
      }
      return `
      <div class="indicator-pill whitespace-nowrap ${pillClass}">
        ${pillText}
      </div>
      `;
    };

    const getEventTypeContent = (event) => {
      if (event.type == kallat_erpnext.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
        return `
        <div class="text-muted">Received: ${format_currency(event.amount_received)}</div>
        `;
      }

      return ""
    };

    const timelineItems = [];
    for (const event of events) {
      timelineItems.push(`
      <div class="timeline-item mb-2">
        <div class="timeline-dot"></div>
        <div class="timeline-content p-3" style="background-color: var(--bg-color)">
          <div class="d-flex flex-row">
            ${getEventTypePill(event)}
            <span class="px-2">${moment(event.creation).format(
              "Do MMM YY"
            )}</span>
            <a class="text-muted" href="/app/unit-sale-event/${event.name}">${
        event.name
      }</a>
          </div>
          <div class="flex-row">
            ${getEventTypeContent(event)}
          </div>
        </div>
      </div>
      `);
    }
    $(frm.fields_dict["events_html"].wrapper).html(`
    <div class="new-timeline">
      <h4 style="position: relative; top: -0.5em; left: -1.5em;">Events</h4>
        ${timelineItems.join("\n")}
      </div>
    `);
  },
});
