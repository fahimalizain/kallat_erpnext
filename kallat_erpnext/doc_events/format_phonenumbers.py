
from kallat_erpnext.utils.phonenumbers import format_number as _format_number


PHONENUMBERS_MAP = {
    "Lead": ["phone", "mobile_no"],
    "Customer": ["mobile_no"],
    "Contact": ["mobile_no", "phone"]
}


def format_number(doc, method=None):
    phonenumber_fields = PHONENUMBERS_MAP.get(doc.doctype) or []
    if not len(phonenumber_fields):
        return

    for df in phonenumber_fields:
        doc.set(df, _format_number(doc.get(df)))
