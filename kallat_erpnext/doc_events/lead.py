import frappe
from kallat_erpnext.utils.notification_handler import (
    NotificationChannel, NotificationRecipientItem, _schedule_notification)


LEAD_CREATED = "lead-created"


def send_lead_created_notification(doc, method=None):

    frappe.enqueue(
        _schedule_notification,
        enqueue_after_commit=True,
        template_key=LEAD_CREATED,
        context=dict(
            lead=doc.name,
            email_id=doc.email_id,
            lead_name=doc.lead_name,
            title=doc.title,
        ),
        recipients=get_lead_recipients(doc),
        days=0,
        hours=0.25,
    )


def get_lead_recipients(doc):
    return [
        NotificationRecipientItem(
            channel=NotificationChannel.SMS,
            channel_id=doc.mobile_no or doc.phone,
            user_identifier="Lead:{}".format(doc.name)
        )
    ]
