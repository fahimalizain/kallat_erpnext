import frappe
from frappe.core.doctype.file.file import File


def write_file(doc: File):
    ALLOWED_TYPES = ('image/png', 'image/jpeg', 'application/pdf')
    if doc.content_type not in ALLOWED_TYPES:
        frappe.throw("Only images (jpg, png) & PDFs are allowed to be uploaded")

    return doc.save_file_on_filesystem()
