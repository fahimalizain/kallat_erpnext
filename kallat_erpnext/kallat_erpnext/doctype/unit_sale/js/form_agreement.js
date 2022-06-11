frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_agreement_form = function (frm) {
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
}