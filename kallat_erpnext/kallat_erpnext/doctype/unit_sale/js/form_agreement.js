frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_agreement_form = function (frm) {

    const fields = [
        {
            label: "Agreement PDF",
            fieldtype: "Attach",
            reqd: kallat.maintenance_mode() ? 0 : 1,
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
    ]

    if (kallat.maintenance_mode()) {
        fields.unshift({
            label: "Date Time",
            fieldtype: "Datetime",
            reqd: 1,
            default: frappe.datetime.now_datetime(),
            fieldname: "event_datetime"
        })
    }

    const d = new frappe.ui.Dialog({
        title: "Upload Agreement PDF",
        fields: fields,
        primary_action_label: "Sign Agreement",
        primary_action(values) {
            if (!values.agreement_file && !kallat.maintenance_mode()) {
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
}