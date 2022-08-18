from datetime import datetime

from kallat_erpnext.utils.notification_handler import NotificationHandler, NotificationChannel


class UnitSaleNotificationHandler(NotificationHandler):
    DEFAULT_CHANNELS = [NotificationChannel.SMS]

    # Template Keys
    UNIT_SALE_SUBMITTED = "unit-sale-submitted"
    UNIT_SALE_PAYMENT_RECEIPT = "unit-sale-payment-receipt"
    UNIT_SALE_BOOKING_CONFIRMED = "unit-sale-booking-confirmed"
    UNIT_SALE_AGREEMENT_REMINDER = "unit-sale-agreement-reminder"
    UNIT_SALE_WORK_STATUS_UPDATED = "unit-sale-work-status-updated"
    UNIT_SALE_LAND_REGISTRATION = "unit-sale-land-registration"
    UNIT_SALE_DUE_WEEK_1_REMINDER_1 = "unit-sale-due-week-1-reminder-1"
    UNIT_SALE_DUE_WEEK_1_REMINDER_2 = "unit-sale-due-week-1-reminder-2"
    UNIT_SALE_DUE_WEEK_1_REMINDER_3 = "unit-sale-due-week-1-reminder-3"
    UNIT_SALE_OVERDUE_REMINDER = "unit-sale-due-overdue-reminder"
    UNIT_SALE_DUE_FINAL_REMINDER = "unit-sale-due-final-reminder"

    def get_context(self):
        return dict(
            unit_sale=self.name,
            customer=self.customer,
            project=self.project,
            plot=self.plot,
            unit_type=self.unit_type,
            status=self.status,
            work_status=self.work_status,
        )

    def on_submit(self):
        self.send_notification(
            template_key=self.UNIT_SALE_SUBMITTED,
            context=self.get_context(),
            recipients=self.get_customer_recipients(channels=self.DEFAULT_CHANNELS),
            schedule_notification=True,
            hours=2)

    def trigger_due_amount_notification(
            self,
            days_since_last_event: int,
            days_since_last_fine: datetime):
        """
            days_since_last_event: No. of days since last Event that made a `Due`
            days_since_last_fine: No. of days since last time he was charged

            Trigger Conditions
            No-Fine-Week: 1st Week.
            - On 3rd day of No-Fine-Week send UNIT_SALE_DUE_WEEK_1_REMINDER_1
            - On 5th day of No-Fine-Week send UNIT_SALE_DUE_WEEK_1_REMINDER_2
            - On 6th day of No-Fine-Week send UNIT_SALE_DUE_WEEK_1_REMINDER_3
            - On every 3 days from last_fine_date send UNIT_SALE_OVERDUE_REMINDER
            - On 60th Day from days_since_last_event send UNIT_SALE_DUE_FINAL_REMINDER
            - Nothing to be sent as a reminder after the last one

            This function will be executed every Day if the UnitSale has balance_due > 0
        """
        schedule_in_days = 0
        template = None

        if days_since_last_event == 1:
            schedule_in_days = 2
            template = self.UNIT_SALE_DUE_WEEK_1_REMINDER_1
        elif days_since_last_event == 3:
            schedule_in_days = 2
            template = self.UNIT_SALE_DUE_WEEK_1_REMINDER_2
        elif days_since_last_event == 4:
            schedule_in_days = 3
            template = self.UNIT_SALE_DUE_WEEK_1_REMINDER_3
        elif days_since_last_event == 55:
            template = self.UNIT_SALE_DUE_FINAL_REMINDER
            schedule_in_days = 5
        elif days_since_last_event > 55:

            # No more SMS.
            # Final Reminder Sent
            return
        elif days_since_last_fine % 3 == 1:
            # Every 3 days from last fine, send SMS
            # But, % 3 == 1 since we are triggering it 2 days in advance
            schedule_in_days = 2
            template = self.UNIT_SALE_OVERDUE_REMINDER

        if not template:
            # Nothing to send today
            return

        self.send_notification(
            template_key=self.UNIT_SALE_DUE_WEEK_1_REMINDER_1,
            context=self.get_context(),
            recipients=self.get_customer_recipients(),
            schedule_notification=schedule_in_days > 0,
            days=schedule_in_days,
        )
