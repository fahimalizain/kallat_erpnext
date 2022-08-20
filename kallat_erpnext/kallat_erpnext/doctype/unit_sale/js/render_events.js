frappe.provide("kallat.unit_sale");

kallat.unit_sale.EVENTS_GROUP_PAYMENTS = 1;
kallat.unit_sale.EVENTS_SHOW_NOTIFICATIONS = 0;

kallat.unit_sale.render_events = function (frm) {
  $(frm.fields_dict["events_html"].wrapper).html(``);
  frm.set_df_property("events_html_sb", "hidden", 1);

  if (frm.doc.docstatus !== 1) {
    return;
  }

  frm.call({
    method: "get_events",
    args: {
      group_payments: kallat.unit_sale.EVENTS_GROUP_PAYMENTS,
      show_notifications: kallat.unit_sale.EVENTS_SHOW_NOTIFICATIONS,
    },
    doc: frm.doc,
    callback(r) {
      if (r.exc) {
        return;
      }
      const data = r.message || [];
      if (!data.events && !data.scheduled_notifications) {
        return;
      }
      kallat.unit_sale.make_events_html(frm, data);
      frm.set_df_property("events_html_sb", "hidden", 0);
    },
  });
};

kallat.unit_sale.make_events_html = function (frm, data) {
  const getEventTypePill = (event) => {
    let pillClass = "red";
    let pillText = event.type;
    if (event.type === kallat.unit_sale.UNIT_SALE_TYPE.PAYMENT_RECEIPT) {
      pillClass = "orange";
      pillText = "Payment";
      if (event.grouped_payments) {
        pillText = event.grouped_payments.length + " Payments";
      }
    } else if (event.type == kallat.unit_sale.UNIT_SALE_TYPE.UNIT_SALE_UPDATE) {
      if (event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.BOOKED) {
        pillClass = "blue";
        pillText = "Booking Confirmed";
      } else if (
        event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.AGREEMENT_SIGNED
      ) {
        pillClass = "blue";
        pillText = "Agreement Signed";
      } else if (
        event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.HANDED_OVER
      ) {
        pillClass = "blue";
        pillText = "Handed Over";
      }
    } else if (
      event.type == kallat.unit_sale.UNIT_SALE_TYPE.WORK_STATUS_UPDATE
    ) {
      pillClass = "gray";
      pillText = event.new_status;
    } else if (event.type == "Notification") {
      pillClass = "green";
      pillText = (event.channels || []).join(" | ");
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
      if (
        event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.AGREEMENT_SIGNED
      ) {
        const misc = JSON.parse(event.misc);
        return `
          <div class="text-muted">Agreement Price: ${format_currency(
            misc.agreement_price || misc.final_price // TODO: remove, here for backward compatibility
          )}</div>
        `;
      } else if (
        event.new_status == kallat.unit_sale.UNIT_SALE_STATUS.HANDED_OVER
      ) {
        return `
          <div class="text-muted">Amount Due: ${format_currency(
            event.amount_due
          )}</div>
        `;
      }
    } else if (
      event.type == kallat.unit_sale.UNIT_SALE_TYPE.WORK_STATUS_UPDATE
    ) {
      return `
        <div class="text-muted">
          Amount Due: ${format_currency(event.amount_due)}
        </div>`;
    } else if (event.type == "Notification") {
      return `
            <div class="text-muted">
                Template: ${event.template_key}
            </div>
            `;
    }

    return "";
  };

  const getEventTypeLink = (event) => {
    if (event.type == "Notification") {
      return `
            <a class="text-muted" href="/app/kallat-notification-schedule/${event.name}">
                Notification Log
            </a>`;
    }

    return `
        <a class="text-muted" href="/app/unit-sale-event/${event.name}">${event.name}</a>`;
  };

  const timelineItems = [];
  for (const event of data.events || []) {
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
              <span class="px-2 flex-grow-1">${moment(event.date_time).format(
                "Do MMM YY"
              )}</span>
              ${getEventTypeLink(event)}
            </div>
          </div>
        </div>
      </div>
      `);
  }

  const scheduledNotificationItems = [];
  for (const notif of data.scheduled_notifications || []) {
    scheduledNotificationItems.push(`
    <div class="timeline-item mb-2">
      <div class="timeline-dot"></div>
      <div class="timeline-content p-3" style="background-color: var(--bg-color)">
        <div class="d-flex flex-row">
          <div class="flex-column flex-grow-1 align-items-start justify-content-center">
            ${getEventTypePill(notif)}
            ${getEventTypeSubtitle(notif)}
          </div>

          <div class="flex-column">
            <span class="px-2 flex-grow-1">${moment(notif.date_time).fromNow()}</span>
            ${getEventTypeLink(notif)}
          </div>
        </div>
      </div>
    </div>
    `);
  }

  let _html = "";
  if (scheduledNotificationItems.length) {
    _html += `
    <div class="new-timeline">
        <div
            class="scheduled-notif-heading-group d-flex flex-column flex-md-row"
            style="position: relative; top: -0.5em; left: -1.5em;"
        >
            <h4>Scheduled Notifications</h4>
        </div>
        ${scheduledNotificationItems.join("\n")}
    </div>
    `;
  }

  if (timelineItems.length) {
    _html += `
     <div class="new-timeline">
         <div
             class="events-heading-group d-flex flex-column flex-md-row"
             style="position: relative; top: -0.5em; left: -1.5em;"
         >
             <h4>Events</h4>
         </div>
         ${timelineItems.join("\n")}
     </div>
     `;
  }

  $(frm.fields_dict["events_html"].wrapper).html(_html);

  if (timelineItems.length) {
    kallat.unit_sale.make_events_group_payments_checkbox(frm);
    kallat.unit_sale.make_events_show_notifications_checkbox(frm);
  }
};

/**
 * Makes the 'Group Payments' Checkbox near the 'Events' header
 */
kallat.unit_sale.make_events_group_payments_checkbox = function (frm) {
  const render = frappe.utils.debounce(
    kallat.unit_sale.render_events,
    1000,
    true
  );
  const control = frappe.ui.form.make_control({
    df: {
      fieldtype: "Check",
      label: "Group Payments",
      fieldname: "group_payments",
      onchange: (e) => {
        kallat.unit_sale.EVENTS_GROUP_PAYMENTS = control.get_value();
        render(frm);
      },
    },
    parent: $(".events-heading-group"),
  });
  control.toggle(true);
  control.set_input(kallat.unit_sale.EVENTS_GROUP_PAYMENTS);
  control.$wrapper.addClass("ml-5 ml-md-3");
};

/**
 * Makes the 'Show Notifications' Checkbox near the 'Events' header
 */
kallat.unit_sale.make_events_show_notifications_checkbox = function (frm) {
  const render = frappe.utils.debounce(
    kallat.unit_sale.render_events,
    1000,
    true
  );
  const control = frappe.ui.form.make_control({
    df: {
      fieldtype: "Check",
      label: "Show Notifications",
      fieldname: "show_notifications",
      onchange: (e) => {
        kallat.unit_sale.EVENTS_SHOW_NOTIFICATIONS = control.get_value();
        render(frm);
      },
    },
    parent: $(".events-heading-group"),
  });
  control.toggle(true);
  control.set_input(kallat.unit_sale.EVENTS_SHOW_NOTIFICATIONS);
  control.$wrapper.addClass("ml-5 ml-md-3");
};
