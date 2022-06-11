frappe.provide("kallat.unit_sale")

kallat.unit_sale.render_events = function (frm) {
    $(frm.fields_dict["events_html"].wrapper).html(``);
    frm.set_df_property("events_html_sb", "hidden", 1)

    if (frm.doc.docstatus !== 1) {
        return;
    }

    frm.call({
        method: "get_events",
        doc: frm.doc,
        callback(r) {
            if (r.exc) {
                return;
            }
            const events = r.message || [];
            if (!events.length) {
                return
            }
            kallat.unit_sale.make_events_html(frm, r.message);
            frm.set_df_property("events_html_sb", "hidden", 0)
        },
    });
}

kallat.unit_sale.make_events_html = function (frm, events) {
    const getEventTypePill = (event) => {
        let pillClass = "red";
        let pillText = event.type;
        if (event.type === kallat.unit_sale.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
            pillClass = "orange";
            pillText = "Payment";
        } else if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
            if (event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.BOOKED) {
                pillClass = "blue";
                pillText = "Booking Confirmed";
            } else if (
                event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.AGREEMENT_SIGNED
            ) {
                pillClass = "blue";
                pillText = "Agreement Signed";
            } else if (event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.HANDED_OVER) {
                pillClass = "blue";
                pillText = "Handed Over";
            }
        } else if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.WORK_STATUS_UPDATE) {
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
        if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
            return `
        <div class="text-muted">Received: ${format_currency(
                event.amount_received
            )}</div>
        `;
        } else if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
            if (event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.AGREEMENT_SIGNED) {
                const misc = JSON.parse(event.misc);
                return `
          <div class="text-muted">Agreement Price: ${format_currency(
                    misc.agreement_price || misc.final_price // TODO: remove, here for backward compatibility
                )}</div>
        `;
            } else if (event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.HANDED_OVER) {
                return `
          <div class="text-muted">Amount Due: ${format_currency(
                    event.amount_due
                )}</div>
        `;
            }
        } else if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.WORK_STATUS_UPDATE) {
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
}