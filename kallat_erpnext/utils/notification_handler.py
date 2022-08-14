from enum import Enum
from typing import List


import frappe

from frappe.model.document import Document


class NotificationChannel(Enum):
    EMAIL = "Email"
    SMS = "SMS"


class NotificationRecipientItem(frappe._dict):
    channel: NotificationChannel
    channel_id: str
    user_identifier: str


def send_notification(
    template_key: str,
    context: dict,
    recipients: List[NotificationRecipientItem]
):
    pass


class NotificationHandler(Document):
    @staticmethod
    def send_notification(
            template_key: str,
            context: dict,
            recipients: List[NotificationRecipientItem],
            schedule_notification=False,
            days=0,
            hours=0):
        pass

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
