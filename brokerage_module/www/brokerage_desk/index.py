import frappe
from frappe import _
from brokerage_module.brokerage_module.api import get_boot

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/brokerage-desk"
        raise frappe.Redirect

    frappe.db.commit()
    context.boot = get_boot()
    return context
