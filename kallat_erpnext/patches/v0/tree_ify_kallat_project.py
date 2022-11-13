import frappe


def execute():
    # kallat_project.json already has is_root: 1 set
    frappe.reload_doctype("Kallat Project")

    root = add_root_project()
    update_parents(root.name)


def add_root_project():
    return frappe.get_doc(dict(
        doctype="Kallat Project", title="All Kallat Project")).insert()


def update_parents(root):
    for project in frappe.get_all("Kallat Project"):
        if project.name == root:
            continue
        frappe.set_value(
            "Kallat Project",
            project.name,
            frappe.scrub("Parent Kallat Project"),
            root)
