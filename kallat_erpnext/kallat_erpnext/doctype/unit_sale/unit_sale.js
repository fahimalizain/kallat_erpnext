// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt

frappe.provide("kallat");
kallat.UNIT_SALE_TYPE = {
  PAYMENT_RECEIPT: "Payment Receipt",
  UNIT_SALE_UPDATE: "Unit Sale Update",
  WORK_STATUS_UPDATE: "Work Status Update",
};

kallat.UNIT_SALE_STATUS = {
  BOOKED: "Booked",
  AGREEMENT_SIGNED: "Agreement Signed",
  WIP: "Work In Progress",
  HANDED_OVER: "Handed Over",
  COMPLETED: "Completed",
};

kallat.WORK_STATUS = {
  NOT_STARTED: "Not Started",
  FOUNDATION_COMPLETED: "Foundation Completed",
  FIRST_FLOOR_SLAB_COMPLETED: "1st Floor Slab Completed",
  STRUCTURE_COMPLETED: "Structure Completed",
  TILING_COMPLETED: "Tiling Completed",
  HAND_OVER_COMPLETED: "Hand Over Completed",
};

kallat.WORK_STATUSES = Object.values(kallat.WORK_STATUS);
kallat.UNIT_SALE_FRM_BTN_GRP = "Update";

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
        frm.events.make_events_html(frm, r.message);
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
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Sign Agreement
    else if (frm.doc.status === kallat.UNIT_SALE_STATUS.BOOKED) {
      frm.add_custom_button(
        "Sign Agreement",
        () => {
          frm.events.show_agreement_form(frm);
        },
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Work Progress Updates
    else if (
      frm.doc.status == kallat.UNIT_SALE_STATUS.WIP &&
      frm.doc.work_status != kallat.WORK_STATUS.TILING_COMPLETED
    ) {
      frm.add_custom_button(
        "Work Progress",
        () => {
          frm.events.show_work_progress_form(frm);
        },
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
    }
    // Handover
    else if (
      frm.doc.work_status == kallat.WORK_STATUS.TILING_COMPLETED &&
      frm.doc.status == kallat.UNIT_SALE_STATUS.WIP
    ) {
      frm.add_custom_button(
        "Hand Over Unit",
        () => {
          frm.events.show_hand_over_form(frm);
        },
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
    }

    // Payment Receipt
    if (frm.doc.total_balance > 0) {
      frm.add_custom_button(
        "Make Payment Receipt",
        () => {
          frm.events.show_payment_receipt_form(frm);
        },
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
    }

    // Extra Work
    if (frm.doc.status !== kallat.UNIT_SALE_STATUS.COMPLETED) {
      frm.add_custom_button(
        "Add Extra Work",
        () => {
          frm.events.show_extra_work_form(frm);
        },
        kallat.UNIT_SALE_FRM_BTN_GRP
      );
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
          label: "Agreement Price",
          fieldtype: "Currency",
          reqd: 1,
          fieldname: "agreement_price",
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
              frm.reload_doc();
              d.hide();
            }
          },
        });
      },
    });

    d.show();
  },

  show_payment_receipt_form(frm) {

    let fileIdx = 0;

    const d = new frappe.ui.Dialog({
      title: "Payment Receipt",
      fields: [
        {
          label: "Amount Received",
          fieldtype: "Currency",
          fieldname: "amount_received",
          reqd: 1,
          default: frm.doc.balance_due,
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

            const fieldName = "file_" + fileIdx;
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
      primary_action_label: "Make Receipt",
      primary_action(values) {
        if (!values.amount_received) {
          frappe.msgprint("Please specify amount received");
          return;
        }
        frm.call({
          method: "make_payment_receipt",
          doc: frm.doc,
          args: {
            ...values, num_files: fileIdx
          },
          freeze: true,
          callback(r) {
            if (r.exc) {
              frappe.msgprint(
                "Something went wrong! Please try again or Contact Developer"
              );
            } else {
              frappe.msgprint("Payment Receipt Made!");
              frm.reload_doc();
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

            const fieldName = "file_" + fileIdx;
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
          args: { ...values, num_files: fileIdx },
          callback(r) {
            if (r.exc) {
              frappe.msgprint(
                "Something went wrong! Please try again or Contact Developer"
              );
            } else {
              frappe.msgprint("Status Updated!");
              frm.reload_doc();
              d.hide();
            }
          },
        });
      },
    });

    d.show();
  },

  show_hand_over_form(frm) {
    let fileIdx = 0;
    const d = new frappe.ui.Dialog({
      title: "Hand Over Unit",
      fields: [
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

            // if (fileIdx % 2 === 0) {
            //   // Add Column Break
            //   let df = "files_col_b_" + fileIdx
            //   d.make_field({
            //     fieldname: df,
            //     fieldtype: "Column Break"
            //   });
            //   d.fields_dict[df].refresh();
            // }

            const fieldName = "file_" + fileIdx;
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
          method: "hand_over_unit",
          doc: frm.doc,
          freeze: true,
          args: { ...values, num_files: fileIdx },
          callback(r) {
            if (r.exc) {
              frappe.msgprint(
                "Something went wrong! Please try again or Contact Developer"
              );
            } else {
              frappe.msgprint("Hand Over Done!");
              frm.reload_doc();
              d.hide();
            }
          },
        });
      },
    });

    d.show();
  },

  show_extra_work_form(frm) {
    // Clone fields
    const extra_work_fields = JSON.parse(
      JSON.stringify(frappe.get_meta("Extra Work Item").fields)
    );

    const d = new frappe.ui.Dialog({
      title: "Add Extra Work",
      fields: [
        {
          label: "Remarks",
          fieldtype: "Small Text",
          fieldname: "remarks",
        },
        {
          label: "Extra Works",
          fieldtype: "Table",
          fieldname: "extra_work",
          fields: extra_work_fields,
        },
        {
          label: "Total Additional Cost",
          fieldtype: "Currency",
          fieldname: "total",
          read_only: 1,
          default: 0,
        },
      ],
      primary_action_label: "Add",
      primary_action(values) {
        frm.call({
          method: "add_extra_work",
          doc: frm.doc,
          freeze: true,
          args: {
            remarks: values.remarks,
            extra_work: values.extra_work,
          },
          callback(r) {
            if (r.exc) {
              frappe.msgprint(
                "Something went wrong! Please try again or Contact Developer"
              );
            } else {
              frappe.msgprint("Extra Work Registered!");
              frm.reload_doc();
              d.hide();
            }
          },
        });
      },
    });

    const update_amounts = () => {
      // This function will update the amount & total on the dialog
      let total = 0;
      const grid = d.fields_dict["extra_work"].grid;
      for (const row of grid.data) {
        row.amount = flt(row.qty * row.rate, 2) || 0;
        total += row.amount;
      }
      d.set_value("total", total);
      grid.refresh();
    };

    // Attach update_amount handler
    for (const df of ["qty", "rate"]) {
      extra_work_fields.find((x) => x.fieldname == df).onchange = () =>
        update_amounts();
    }

    d.show();
  },

  make_events_html(frm, events) {
    const getEventTypePill = (event) => {
      let pillClass = "red";
      let pillText = event.type;
      if (event.type === kallat.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
        pillClass = "orange";
        pillText = "Payment";
      } else if (event.type == kallat.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
        if (event.new_status == kallat.UNIT_SALE_STATUS.BOOKED) {
          pillClass = "blue";
          pillText = "Booking Confirmed";
        } else if (
          event.new_status == kallat.UNIT_SALE_STATUS.AGREEMENT_SIGNED
        ) {
          pillClass = "blue";
          pillText = "Agreement Signed";
        } else if (event.new_status == kallat.UNIT_SALE_STATUS.HANDED_OVER) {
          pillClass = "blue";
          pillText = "Handed Over";
        }
      } else if (event.type == kallat.UNIT_SALE_TYPE.WORK_STATUS_UPDATE) {
        pillClass = "gray";
        pillText = event.new_status;
      }
      return `
      <div class="indicator-pill whitespace-nowrap ${pillClass} mb-2">
        ${pillText}
      </div>
      `;
    };

    const getEventTypeSubtitle = (event) => {
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
          <div class="text-muted">Agreement Price: ${format_currency(
            misc.agreement_price || misc.final_price // TODO: remove, here for backward compatibility
          )}</div>
        `;
        } else if (event.new_status == kallat.UNIT_SALE_STATUS.HANDED_OVER) {
          return `
          <div class="text-muted">Amount Due: ${format_currency(
            event.amount_due
          )}</div>
        `;
        }
      } else if (event.type == kallat.UNIT_SALE_TYPE.WORK_STATUS_UPDATE) {
        return `
        <div class="text-muted">
          Amount Due: ${format_currency(event.amount_due)}
        </div>`;
      }

      return "";
    };

    const timelineItems = [];
    for (const event of (events || [])) {
      timelineItems.push(`
      <div class="timeline-item mb-2">
        <div class="timeline-dot"></div>
        <div class="timeline-content p-3" style="background-color: var(--bg-color)">
          <div class="d-flex flex-row">
            <div class="flex-column flex-grow-1 align-items-start justify-content-center">
              ${getEventTypePill(event)}
              ${getEventTypeSubtitle(event)}
            </div>

            <div class="flex-column">
              <span class="px-2 flex-grow-1">${moment(event.creation).format(
        "Do MMM YY"
      )}</span>
              <a class="text-muted" href="/app/unit-sale-event/${event.name}">${event.name
        }</a>
            </div>
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
