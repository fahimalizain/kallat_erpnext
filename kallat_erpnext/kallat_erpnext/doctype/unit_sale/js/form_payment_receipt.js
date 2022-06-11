frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_payment_receipt_form = function (frm) {

    let fileIdx = 0;
    const fields = [
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
    ]

    if (kallat.can_modify_timestamp()) {
        fields.unshift({
            label: "Date Time",
            fieldtype: "Datetime",
            reqd: 1,
            default: frappe.datetime.now_datetime(),
            fieldname: "event_datetime"
        })
    }

    const d = new frappe.ui.Dialog({
        title: "Payment Receipt",
        fields: fields,
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
}