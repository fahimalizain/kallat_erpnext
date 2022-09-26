from enum import Enum

import frappe
from erpnext.projects.doctype.task.task import Task


class TaskStatus(Enum):
    OPEN = "Open"
    WORKING = "Working"
    PENDING_REVIEW = "Pending Review"
    OVERDUE = "Overdue"
    TEMPLATE = "Template"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


def validate(doc, method=None):
    validate_status_change(doc)


def validate_status_change(task: Task):
    """
    - Open to Working
    - Working to Ready for Review
    """
    old_task = task.get_doc_before_save()
    if not old_task:
        return

    if old_task.status == task.status:
        return

    if frappe.session.user == task.owner:
        # Task Owner has all the Perms!
        return

    # Non-Owners can only change status to the following
    if task.status not in (
        TaskStatus.OPEN.value,
        TaskStatus.WORKING.value,
        TaskStatus.PENDING_REVIEW.value,
    ):
        frappe.throw("Only {} can update the status to {}".format(
            frappe.get_doc("User", task.owner).get_fullname(),
            task.status
        ))
