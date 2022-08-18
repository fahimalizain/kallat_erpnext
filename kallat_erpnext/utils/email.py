from typing import List


def send_email(
    template_key: str,
    context: dict,
    recipients: List[str],
):
    if not len(recipients):
        return
