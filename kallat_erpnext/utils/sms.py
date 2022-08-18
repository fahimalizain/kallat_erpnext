from typing import List

import frappe


def send_sms(
    template_key: str,
    context: dict,
    recipients: List[str],
):
    if not len(recipients):
        return

    contents = _render_template(template_key, context)
    frappe.log_error(
        title="SMS Sent",
        message="To: {}\n\n{}".format(", ".join(recipients), contents)
    )


def _render_template(template_key: str, context: dict):
    template = frappe.db.get_value("Kallat SMS Template", template_key, "template")
    if not template:
        frappe.throw("SMS Template {} not found".format(template_key))

    return frappe.render_template(template, context) or ""
