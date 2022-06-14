frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_extra_work_form = function (frm) {
    // Clone fields
    const extra_work_fields = JSON.parse(
        JSON.stringify(frappe.get_meta("Extra Work Item").fields)
    );

    const fields = [
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
        title: "Add Extra Work",
        fields: fields,
        primary_action_label: "Add",
        primary_action(values) {
            frm.call({
                method: "add_extra_work",
                doc: frm.doc,
                freeze: true,
                args: {
                    remarks: values.remarks,
                    extra_work: values.extra_work,
                    event_datetime: values.event_datetime,
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
}