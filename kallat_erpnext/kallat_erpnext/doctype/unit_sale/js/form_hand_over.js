frappe.provide("kallat.unit_sale")

kallat.unit_sale.show_hand_over_form = function (frm) {
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
}