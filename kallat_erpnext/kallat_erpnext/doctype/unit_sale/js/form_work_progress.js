frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_work_progress_form = function (frm) {
    const statusIdx = kallat.unit_sale.WORK_STATUSES.indexOf(frm.doc.work_status);
    if (statusIdx + 1 >= kallat.unit_sale.WORK_STATUSES.length) {
        console.log("At final status now");
        return;
    }
    const nextStatus = kallat.unit_sale.WORK_STATUSES[statusIdx + 1];
    let fileIdx = 0;

    const fields = [
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
        title: "Update Unit Status",
        fields: fields,
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
}