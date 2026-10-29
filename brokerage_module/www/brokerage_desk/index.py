import os
import time
import frappe
from frappe import _
from brokerage_module.brokerage_module.api import get_boot

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/brokerage-desk"
        raise frappe.Redirect

    frappe.db.commit()
    boot_data = get_boot()
    context["boot"] = boot_data
    if hasattr(context, "boot"):
        try:
            context.boot = boot_data
        except Exception:
            pass

    # Asset cache-buster to prevent stale browser caching
    asset_file = frappe.get_app_path("brokerage_module", "public", "frontend", "assets", "index.js")
    if os.path.exists(asset_file):
        build_ver = str(int(os.path.getmtime(asset_file)))
    else:
        build_ver = str(int(time.time()))

    context["build_version"] = build_ver
    if hasattr(context, "build_version"):
        try:
            context.build_version = build_ver
        except Exception:
            pass

    return context

