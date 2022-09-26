from . import __version__ as app_version  # noqa

app_name = "kallat_erpnext"
app_title = "Kallat Erpnext"
app_publisher = "Fahim Ali Zain"
app_description = "ERPNext Customizations for Kallat Builders"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "fahimalizain@gmail.com"
app_license = "MIT"

doc_events = {
    "*": {
        "validate": "kallat_erpnext.doc_events.format_phonenumbers.format_number"
    },
    "Task": {
        "validate": "kallat_erpnext.doc_events.tasks.validate"
    },
    "Lead": {
        "after_insert": "kallat_erpnext.doc_events.lead.send_lead_created_notification"
    }
}

scheduler_events = {
    "daily": [
        "kallat_erpnext.tasks.daily"
    ],
    "all": [
        "kallat_erpnext.utils.notification_handler.trigger_scheduled_notifications",
    ]
}

boot_session = "kallat_erpnext.boot.boot_session"
write_file = "kallat_erpnext.file.write_file"

fixtures = [
    {"dt": "Property Setter", "filters": [["name", "IN", [
        # The following are for Lead-Quick Entry fields (bold fields are included
        # in QuickEntry form)
        "Lead-main-quick_entry",
        "Lead-lead_name-allow_in_quick_entry",
        "Lead-email_id-allow_in_quick_entry",
        "Lead-source-allow_in_quick_entry",
        "Lead-campaign_name-allow_in_quick_entry",
        "Lead-notes-allow_in_quick_entry",
        "Lead-ends_on-bold",
        "Lead-contact_date-bold",
    ]]]},
    {"dt": "Kallat SMS Template", "filters": [["name", "IN", [
        "lead-created",
        "unit-sale-submitted",
        "unit-sale-payment-receipt",
        "unit-sale-booking-confirmed",
        "unit-sale-agreement-reminder",
        "unit-sale-work-status-updated",
        "unit-sale-land-registration",
        "unit-sale-due-final-reminder",
        "unit-sale-due-overdue-reminder",
        "unit-sale-due-week-1-reminder-1",
        "unit-sale-due-week-1-reminder-2",
        "unit-sale-due-week-1-reminder-3",
    ]]]}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/kallat_erpnext/css/kallat_erpnext.css"
app_include_js = ["/assets/kallat_erpnext/js/utils.js"]

# include js, css files in header of web template
# web_include_css = "/assets/kallat_erpnext/css/kallat_erpnext.css"
# web_include_js = "/assets/kallat_erpnext/js/kallat_erpnext.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kallat_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Unit Sale": [
    "kallat_erpnext/doctype/unit_sale/js/constants.js",
    "kallat_erpnext/doctype/unit_sale/js/form_confirm_booking.js",
    "kallat_erpnext/doctype/unit_sale/js/form_agreement.js",
    "kallat_erpnext/doctype/unit_sale/js/form_extra_work.js",
    "kallat_erpnext/doctype/unit_sale/js/form_hand_over.js",
    "kallat_erpnext/doctype/unit_sale/js/form_payment_receipt.js",
    "kallat_erpnext/doctype/unit_sale/js/form_work_progress.js",
    "kallat_erpnext/doctype/unit_sale/js/render_events.js"
]}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#    "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "kallat_erpnext.install.before_install"
# after_install = "kallat_erpnext.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "kallat_erpnext.uninstall.before_uninstall"
# after_uninstall = "kallat_erpnext.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kallat_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	 "*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#    }
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"kallat_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"kallat_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"kallat_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kallat_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"kallat_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "kallat_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kallat_erpnext.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kallat_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {
        "doctype": "{doctype_4}"
    }
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"kallat_erpnext.auth.validate"
# ]
