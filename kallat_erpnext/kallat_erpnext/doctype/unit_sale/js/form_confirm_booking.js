frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_confirm_booking_form = function (frm) {
    if (kallat.can_modify_timestamp()) {
        kallat.unit_sale._show_confirm_booking_form(frm);
        return;
    }

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
}

/**
 * This is a temporary wrapper function
 * To show a Dialog Window to set Event Date Time
 * @param {Form} frm 
 */
kallat.unit_sale._show_confirm_booking_form = function (frm) {
    const fields = [{
        label: "Date Time",
        fieldtype: "Datetime",
        reqd: 1,
        default: frappe.datetime.now_datetime(),
        fieldname: "event_datetime"
    }]

    const d = new frappe.ui.Dialog({
        title: "Confirm Booking",
        fields: fields,
        primary_action_label: "Confirm",
        primary_action(values) {
            console.log(values, "CONFIRMMM")
            frm.call({
                method: "confirm_booking",
                doc: frm.doc,
                freeze: true,
                args: {
                    ...values,
                },
                callback(r) {
                    if (r.exc) {
                        frappe.msgprint(
                            "Something went wrong! Please try again or Contact Developer"
                        );
                    } else {
                        frappe.msgprint("Booking Confirmed!");
                        frm.reload_doc();
                        d.hide();
                    }
                },
            });
        },
    });

    d.show();
}