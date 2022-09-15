frappe.provide("kallat.unit_sale")

/**
 * Add ExtraWorkItem related Buttons if applicable.
 * This will add the following Buttons if conditions are met:
 * - Add Extra Work
 * - Make Payment for Extra Work
 * - Complete Extra Work
 * @param {FrappeForm} frm 
 */
kallat.unit_sale.extra_work_setup = function (frm) {
    // Add Extra Work
    if (frm.doc.status !== kallat.unit_sale.UNIT_SALE_STATUS.COMPLETED) {
        frm.add_custom_button(
            "Add Extra Work",
            () => {
                kallat.unit_sale.extra_work_show_add_new_form(frm);
            },
            kallat.unit_sale.UNIT_SALE_FRM_BTN_GRP
        );
    }

    if (!frm.doc.extra_work) {
        return;
    }

    const currentStatuses = frm.doc.extra_work.map(x => x.status);
    const EXTRA_WORK_STATUS = kallat.unit_sale.EXTRA_WORK_STATUS;

    if (currentStatuses.indexOf(EXTRA_WORK_STATUS.PENDING) >= 0) {
        kallat.unit_sale.extra_work_make_btn({
            frm,
            label: "Make Payment for Extra Work",
            filter_statuses: [EXTRA_WORK_STATUS.PENDING],
            handler: kallat.unit_sale.extra_work_make_payment_form
        })
    }

    if (currentStatuses.indexOf(EXTRA_WORK_STATUS.PAYMENT_RECEIVED) >= 0) {
        kallat.unit_sale.extra_work_make_btn({
            frm,
            label: "Start Work",
            filter_statuses: [EXTRA_WORK_STATUS.PAYMENT_RECEIVED],
            handler: kallat.unit_sale.extra_work_start_work_form
        })
    }

    if (currentStatuses.indexOf(EXTRA_WORK_STATUS.WORK_IN_PROGRESS) >= 0) {
        kallat.unit_sale.extra_work_make_btn({
            frm,
            label: "Complete Work",
            filter_statuses: [EXTRA_WORK_STATUS.WORK_IN_PROGRESS],
            handler: kallat.unit_sale.extra_work_complete_work_form
        })
    }
}

/**
 * Show a Form to Add a new ExtraWorkItem
 * @param {FrappeForm} frm 
 */
kallat.unit_sale.extra_work_show_add_new_form = function (frm) {
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

/**
 * Show a Form to make ExtraWork Payment
 * @param {FrappeForm} frm 
 * @param {String} extra_work_row name of ExtraWorkItem Row
 */
kallat.unit_sale.extra_work_make_payment_form = function (frm, extra_work_row) {

    extra_work_row = frm.doc.extra_work.find(x => x.name == extra_work_row);

    const fields = [
        {
            label: "Extra Work Amount",
            fieldtype: "Currency",
            fieldname: "extra_work_amount",
            read_only: 1,
            default: extra_work_row.amount,
        },
        {
            label: "Total Received",
            fieldtype: "Currency",
            fieldname: "total_received",
            read_only: 1,
            default: "0",
        },
        {
            label: "Amount",
            fieldtype: "Currency",
            fieldname: "amount",
        },
        {
            label: "Remarks",
            fieldtype: "Small Text",
            fieldname: "remarks",
        },
    ];
    const d = new frappe.ui.Dialog({
        title: "Make Extra Work Payment",
        fields,
        primary_action_label: "Make Payment",
        primary_action(values) {
            frm.call({
                method: "update_extra_work",
                doc: frm.doc,
                freeze: true,
                args: {
                    remarks: values.remarks,
                    amount: values.amount,
                    event_datetime: values.event_datetime,
                    extra_work_row: extra_work_row.name,
                    update_type: "PAYMENT_RECEIPT"
                },
                callback(r) {
                    if (r.exc) {
                        frappe.msgprint(
                            "Something went wrong! Please try again or Contact Developer"
                        );
                    } else {
                        frappe.msgprint("Extra Work Payment Received!");
                        frm.reload_doc();
                        d.hide();
                    }
                },
            });
        }
    });

    d.show();
}

/**
 * Get Confirmation from User to StartWork on ExtraWorkItem
 * @param {FrappeForm} frm 
 * @param {String} extra_work_row name of ExtraWorkItem Row
 */
kallat.unit_sale.extra_work_start_work_form = function (frm, extra_work_row) {
    extra_work_row = frm.doc.extra_work.find(x => x.name == extra_work_row);
    frappe.confirm(`Are you sure to Start the work on ${extra_work_row.title}?`, () => {
        console.log("Start!")
        frm.call({
            method: "update_extra_work",
            doc: frm.doc,
            freeze: true,
            args: {
                event_datetime: values.event_datetime,
                extra_work_row: extra_work_row.name,
                update_type: "START_WORK"
            },
            callback(r) {
                if (r.exc) {
                    frappe.msgprint(
                        "Something went wrong! Please try again or Contact Developer"
                    );
                } else {
                    frappe.msgprint("Extra Work Started!");
                    frm.reload_doc();
                    d.hide();
                }
            },
        });
    })
}

/**
 * Get Confirmation from User to Complete work on ExtraWorkItem
 * @param {FrappeForm} frm 
 * @param {String} extra_work_row name of ExtraWorkItem Row
 */
kallat.unit_sale.extra_work_complete_work_form = function (frm, extra_work_row) {
    extra_work_row = frm.doc.extra_work.find(x => x.name == extra_work_row);
    frappe.confirm(`Are you sure to Complete the work on ${extra_work_row.title}?`, () => {
        frm.call({
            method: "update_extra_work",
            doc: frm.doc,
            freeze: true,
            args: {
                event_datetime: values.event_datetime,
                extra_work_row: extra_work_row.name,
                update_type: "COMPLETE_WORK"
            },
            callback(r) {
                if (r.exc) {
                    frappe.msgprint(
                        "Something went wrong! Please try again or Contact Developer"
                    );
                } else {
                    frappe.msgprint("Extra Work Completed!");
                    frm.reload_doc();
                    d.hide();
                }
            },
        });
    })
}

/**
 * Show a form to let the User select an ExtraWorkItem for them to work on.
 * Sets kallat.unit_sale.EXTRA_WORK_SELECTED_ROW on selection.
 * @param {FrappeForm} frm 
 * @param {string[]} statuses A list of statuses to filter by
 */
kallat.unit_sale.extra_work_select_form = function (frm, statuses) {
    if (!statuses) {
        // No filter provided. So allow ALL
        statuses = Object.values(kallat.unit_sale.EXTRA_WORK_STATUS);
    }
    kallat.unit_sale.EXTRA_WORK_SELECTED_ROW = null;

    // Make an Obj where the
    //      key     => ExtraWorkItem.title
    //      value   => ExtraWorkItem.name
    const extra_work_map = frm.doc.extra_work
        .filter(x => statuses.indexOf(x.status) >= 0)
        .reduce((map, row) => {
            let k = row.title;
            while (Object.keys(map).indexOf(k) >= 0) {
                k += " - 1"
            }

            map[k] = row.name;
            return map;
        }, {});

    const fields = [
        {
            label: "Extra Work",
            fieldtype: "Select",
            options: Object.keys(extra_work_map).join("\n"),
            reqd: 1,
            default: Object.keys(extra_work_map)[0],
            fieldname: "extra_work_title",
        }
    ];

    const d = new frappe.ui.Dialog({
        title: "Select ExtraWork to Update",
        fields: fields,
        primary_action_label: "Proceed",
        primary_action(values) {
            const selectedRow = extra_work_map[values.extra_work_title];
            kallat.unit_sale.EXTRA_WORK_SELECTED_ROW = selectedRow;
            d.hide();
        }
    });

    d.show();
    return d;
}


/**
 * Adds a Button to ExtraWork Button Group
 * On clicking, a form to select ExtraWork will be shown before actually
 * showing target Form
 * @param {Object} args ExtraWorkBtn Args
 * @param {FrappeForm} args.frm Frappe Form
 * @param {String} args.label Button Label
 * @param {String[]} args.filter_statuses The statuses by which to filter the selection of ExtraWorkItems
 * @param {Function} args.handler The function which will be invoked by handler(frm, extra_work_row_name)
 */
kallat.unit_sale.extra_work_make_btn = function (args) {
    const frm = args.frm;
    frm.add_custom_button(
        args.label,
        () => {
            const d = kallat.unit_sale.extra_work_select_form(frm,);

            // On Hide after Selection, Open the form
            d.on_hide = () => {
                if (!kallat.unit_sale.EXTRA_WORK_SELECTED_ROW) {
                    return;
                }
                args.handler(
                    frm, kallat.unit_sale.EXTRA_WORK_SELECTED_ROW
                )
            };
        },
        "Extra Work",
    );
}