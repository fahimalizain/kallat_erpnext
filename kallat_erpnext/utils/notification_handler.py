from enum import Enum
from typing import List


import frappe
from frappe.utils import add_to_date, get_datetime
from frappe.model.document import Document


class NotificationChannel(Enum):
    EMAIL = "Email"
    SMS = "SMS"


class NotificationRecipientItem(frappe._dict):
    channel: NotificationChannel
    channel_id: str
    user_identifier: str


class NotificationScheduleStatus(Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    SENT = "Sent"


def _send_notification(
    template_key: str,
    context: dict,
    recipients: List[NotificationRecipientItem],
    *args, **kwargs
):
    """
    Send a Notification
    """
    from .sms import send_sms
    from .email import send_email

    for recipient in recipients:
        if recipient.channel == NotificationChannel.SMS:
            send_sms()
        elif recipient.channel == NotificationChannel.EMAIL:
            send_email()


def _schedule_notification(
    template_key: str,
    context: dict,
    recipients: List[NotificationRecipientItem],
    days=0,
    hours=0,
    *args, **kwargs
):
    """
    Schedule a Notification to be sent at a later date time
    """
    send_on = add_to_date(get_datetime, days=days, hours=hours)

    frappe.get_doc(dict(
        doctype="Kallat Notification Schedule",
        template_key=template_key,
        status=NotificationScheduleStatus.SCHEDULED.value,
        context=frappe.as_json(context or dict()),
        recipients=frappe.as_json(recipients or list()),
        send_on=send_on,
    )).insert()


def trigger_scheduled_notifications():
    scheduled_notifications = frappe.get_all(
        "Notification Schedule",
        fields=["template_key", "context", "recipients", "send_on"],
        filters=dict(
            status=NotificationScheduleStatus.SCHEDULED.value,
            send_on=["<=", get_datetime()]
        )
    )

    for notif in scheduled_notifications:
        recipients = frappe.parse_json(notif.get("recipients") or "[]")
        recipients = [
            NotificationRecipientItem(
                channel=NotificationChannel(x.get("channel")),
                channel_id=x.get("channel_id"),
                user_identifier=x.get("user_identifier"),
            )
            for x in recipients
        ]
        _send_notification(
            template_key=notif.get("template_key"),
            context=frappe.parse_json(notif.get("context") or "{}"),
            recipients=recipients)


class NotificationHandler(Document):
    @staticmethod
    def send_notification(
            template_key: str,
            context: dict,
            recipients: List[NotificationRecipientItem],
            schedule_notification=False,
            days=0,
            hours=0):

        if schedule_notification:
            method = _schedule_notification
        else:
            method = _send_notification

        frappe.enqueue(
            method,
            enqueue_after_commit=True,
            template_key=template_key,
            context=context,
            recipients=recipients,
            days=days,
            hours=hours,
        )

    def get_customer_recipients(self, channels: List[NotificationChannel]):
        """
        Gets a list of NotificationRecipientItem for a Customer on specified Channels
        """
        recipients = []
        customer = self.get_customer()
        user_identifier = "Customer:{}".format(customer)
        _info = frappe.db.get_value("Customer", customer, ("mobile_no", "email_id"), as_dict=1)

        if NotificationChannel.SMS in channels:
            recipients.append(NotificationRecipientItem(
                channel=NotificationChannel.SMS,
                channel_id=_info.get("mobile_no"),
                user_identifier=user_identifier,
            ))

        if NotificationChannel.EMAIL in channels:
            recipients.append(NotificationRecipientItem(
                channel=NotificationChannel.SMS,
                channel_id=_info.get("email_id"),
                user_identifier=user_identifier,
            ))

        return recipients

    def get_customer(self):
        """
        Override this method if you have custom Customer resolution
        """
        return self.get("customer")
