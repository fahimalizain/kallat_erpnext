// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.provide("kallat");
kallat.UNIT_SALE_TYPE = {
  PAYMENT_RECEIPT: "Payment Receipt",
  UNIT_SALE_UPDATE: "Unit Sale Update",
};

kallat.UNIT_SALE_STATUS = {
  BOOKED: "Booked",
  AGREEMENT_SIGNED: "Agreement Signed",
};

kallat.WORK_STATUSES = [
  "Not Started",
  "Foundation Completed",
  "1st Floor Slab Completed",
  "Structure Completed",
  "Tiling Completed",
  "Hand Over Completed",
];

frappe.ui.form.on("Unit Sale", {
  refresh: function (frm) {
    if (!frm.doc.date_time) {
      // Set now date
      frm.set_value("date_time", frappe.datetime.now_datetime());
    }

    if (frm.doc.docstatus === 1) {
      // Confirm
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
      }
      // Sign Agreement
      else if (frm.doc.status === "Booked") {
        frm.add_custom_button("Sign Agreement", () => {
          frm.events.show_agreement_form(frm);
        });
      }
      // Work Progress Updates
      else if (frm.doc.status == "Work In Progress") {
        frm.add_custom_button("Update Work Progress", () => {
          frm.events.show_work_progress_form(frm);
        });
      }

      // Payment Receipt
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

  show_work_progress_form(frm) {
    const statusIdx = kallat.WORK_STATUSES.indexOf(frm.doc.work_status);
    if (statusIdx + 1 >= kallat.WORK_STATUSES.length) {
      console.log("At final status now");
      return;
    }
    const nextStatus = kallat.WORK_STATUSES[statusIdx + 1];
    let fileIdx = 0;

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
        {
          label: "Add File",
          fieldtype: "Button",
          click: () => {
            fileIdx++;

            const fieldName = "file-" + fileIdx;
            d.make_field({
              label: "File-" + fileIdx,
              fieldname: fieldName,
              fieldtype: "Attach",
              reqd: 1,
            });
            d.fields_dict[fieldName].refresh();
          },
        },
      ],
      primary_action_label: "Update",
      primary_action(values) {
        frm.call({
          method: "update_work_status",
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
    console.log(d);
  },

  make_events_html(frm, events) {
    const getEventTypePill = (event) => {
      let pillClass = "red";
      let pillText = event.type;
      if (event.type === kallat.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
        pillClass = "gray";
        pillText = "Payment";
      } else if (event.type == kallat.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
        if (event.new_status == kallat.UNIT_SALE_STATUS.BOOKED) {
          pillClass = "green";
          pillText = "Booking Confirmed";
        } else if (
          event.new_status == kallat.UNIT_SALE_STATUS.AGREEMENT_SIGNED
        ) {
          pillClass = "lightblue";
          pillText = "Agreement Signed";
        }
      }
      return `
      <div class="indicator-pill whitespace-nowrap ${pillClass}">
        ${pillText}
      </div>
      `;
    };

    const getEventTypeContent = (event) => {
      if (event.type == kallat.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
        return `
        <div class="text-muted">Received: ${format_currency(
          event.amount_received
        )}</div>
        `;
      } else if (event.type == kallat.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
        if (event.new_status == kallat.UNIT_SALE_STATUS.AGREEMENT_SIGNED) {
          const misc = JSON.parse(event.misc);
          return `
          <div class="text-muted">Final Price: ${format_currency(
            misc.final_price
          )}</div>
        `;
        }
      }

      return "";
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
