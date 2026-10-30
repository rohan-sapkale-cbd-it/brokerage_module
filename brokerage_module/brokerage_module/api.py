import json
import frappe
import frappe.sessions
from frappe import _
from frappe.utils import flt, nowdate, getdate, now, cstr


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def ensure_stock_group_setup():
    """
    Ensures:
    1. Custom fields 'stock_group' and 'gst_rate' exist on 'Item' doctype.
    2. Default Stock Group 'Sugar' exists.
    3. Existing items are backfilled with default Stock Group ('Sugar') and GST rate (5.0%).
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    custom_fields = {
        "Item": [
            {
                "fieldname": "stock_group",
                "label": "Stock Group",
                "fieldtype": "Link",
                "options": "Stock Group",
                "insert_after": "item_group",
                "in_list_view": 1,
                "in_standard_filter": 1,
            },
            {
                "fieldname": "gst_rate",
                "label": "GST Rate (%)",
                "fieldtype": "Percent",
                "default": "5.0",
                "insert_after": "stock_group",
                "in_list_view": 1,
            },
        ]
    }
    if frappe.db.exists("DocType", "Item"):
        meta = frappe.get_meta("Item")
        cfields = []
        for cf in custom_fields.get("Item", []):
            if not meta.has_field(cf["fieldname"]):
                cfields.append(cf)
        if cfields:
            create_custom_fields({"Item": cfields}, update=True)

    # Ensure default Stock Group 'Sugar' exists
    if not frappe.db.exists("Stock Group", "Sugar"):
        sg = frappe.get_doc({
            "doctype": "Stock Group",
            "stock_group_name": "Sugar",
            "default_gst_rate": 5.0,
            "is_active": 1,
            "description": "Standard Sugar Commodity Stock Group",
        })
        sg.insert(ignore_permissions=True)

    if not frappe.db.exists("Stock Group", "Edible Oil"):
        sg2 = frappe.get_doc({
            "doctype": "Stock Group",
            "stock_group_name": "Edible Oil",
            "default_gst_rate": 5.0,
            "is_active": 1,
            "description": "Edible Oil and Fats Stock Group",
        })
        sg2.insert(ignore_permissions=True)

    if not frappe.db.exists("Stock Group", "Grains"):
        sg3 = frappe.get_doc({
            "doctype": "Stock Group",
            "stock_group_name": "Grains",
            "default_gst_rate": 5.0,
            "is_active": 1,
            "description": "Grains and Pulses Stock Group",
        })
        sg3.insert(ignore_permissions=True)

    # Backfill items where stock_group is NULL or empty
    items_updated = 0
    if frappe.db.exists("DocType", "Item"):
        items = frappe.get_all("Item", fields=["name", "stock_group", "gst_rate"])
        for it in items:
            to_update = {}
            if not it.get("stock_group"):
                to_update["stock_group"] = "Sugar"
            if it.get("gst_rate") is None or flt(it.get("gst_rate")) == 0:
                to_update["gst_rate"] = 5.0
            if to_update:
                frappe.db.set_value("Item", it["name"], to_update, update_modified=False)
                items_updated += 1

    frappe.db.commit()
    return {"status": "success", "items_updated": items_updated}


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_stock_groups(query=None, limit=100):
    """
    Returns active Stock Groups with their default GST rate and item counts.
    """
    query = (query if query is not None else (frappe.form_dict.get("query") or "")).strip()
    limit = int(limit or frappe.form_dict.get("limit") or 100)
    filters = {"is_active": 1}
    or_filters = []
    if query:
        or_filters = [
            ["stock_group_name", "like", f"%{query}%"],
            ["name", "like", f"%{query}%"],
        ]
    records = frappe.get_all(
        "Stock Group",
        filters=filters,
        or_filters=or_filters if query else None,
        fields=["name", "stock_group_name", "default_gst_rate", "is_active", "description"],
        order_by="stock_group_name asc",
        limit=limit,
    )
    for r in records:
        r["item_count"] = frappe.db.count("Item", {"stock_group": r.name})
    return records


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_stock_group(data=None):
    """
    Creates or updates a Stock Group master.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    name = payload.get("name") or payload.get("stock_group_name")
    if not name:
        frappe.throw(_("Stock Group Name is required."))

    if frappe.db.exists("Stock Group", name):
        doc = frappe.get_doc("Stock Group", name)
    else:
        doc = frappe.new_doc("Stock Group")
        doc.stock_group_name = payload.get("stock_group_name") or name

    doc.default_gst_rate = flt(payload.get("default_gst_rate") or 5.0)
    doc.is_active = 1 if payload.get("is_active") in (1, "1", True, None) else 0
    doc.description = payload.get("description") or ""

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_items(query=None, stock_group=None, limit=100):
    """
    Returns items with stock_group, gst_rate, and stock_uom.
    """
    query = (query if query is not None else (frappe.form_dict.get("query") or "")).strip()
    stock_group = stock_group or frappe.form_dict.get("stock_group")
    limit = int(limit or frappe.form_dict.get("limit") or 100)

    filters = {"disabled": 0}
    if stock_group:
        filters["stock_group"] = stock_group

    or_filters = []
    if query:
        or_filters = [
            ["item_name", "like", f"%{query}%"],
            ["item_code", "like", f"%{query}%"],
            ["name", "like", f"%{query}%"],
        ]

    fields = ["name", "item_code", "item_name", "item_group", "stock_uom", "stock_group", "gst_rate", "standard_rate", "description"]
    records = frappe.get_all(
        "Item",
        filters=filters,
        or_filters=or_filters if query else None,
        fields=fields,
        order_by="item_name asc",
        limit=limit,
    )
    for r in records:
        if not r.get("stock_group"):
            r["stock_group"] = "Sugar"
        if r.get("gst_rate") is None:
            r["gst_rate"] = 5.0
    return records


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_item(data=None):
    """
    Creates or updates an Item master with stock_group, gst_rate, stock_uom, and standard_rate.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    item_code = payload.get("item_code") or payload.get("name") or payload.get("item_name")
    if not item_code:
        frappe.throw(_("Item Name / Code is required."))

    if frappe.db.exists("Item", item_code):
        doc = frappe.get_doc("Item", item_code)
    else:
        doc = frappe.new_doc("Item")
        doc.item_code = item_code

    doc.item_name = payload.get("item_name") or item_code
    doc.stock_uom = payload.get("stock_uom") or "Quintal"

    # Stock Group Assignment
    stock_group = payload.get("stock_group") or "Sugar"
    if not frappe.db.exists("Stock Group", stock_group):
        sg = frappe.get_doc({
            "doctype": "Stock Group",
            "stock_group_name": stock_group,
            "default_gst_rate": flt(payload.get("gst_rate") or 5.0),
            "is_active": 1,
        })
        sg.insert(ignore_permissions=True)
    doc.stock_group = stock_group

    # GST Rate
    if payload.get("gst_rate") is not None and str(payload.get("gst_rate")).strip() != "":
        doc.gst_rate = flt(payload.get("gst_rate"))
    else:
        default_gst = frappe.db.get_value("Stock Group", stock_group, "default_gst_rate")
        doc.gst_rate = flt(default_gst) if default_gst is not None else 5.0

    if payload.get("standard_rate"):
        doc.standard_rate = flt(payload.get("standard_rate"))

    if payload.get("description"):
        doc.description = payload.get("description")

    # Item group fallback for ERPNext Item validation
    if not doc.item_group and frappe.db.exists("DocType", "Item Group"):
        default_ig = frappe.db.get_value("Item Group", "Products", "name") or frappe.db.get_value("Item Group", "All Item Groups", "name")
        if not default_ig:
            default_ig = frappe.get_all("Item Group", pluck="name", limit=1)
            default_ig = default_ig[0] if default_ig else "All Item Groups"
        doc.item_group = default_ig

    doc.flags.ignore_permissions = True
    doc.save()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_boot():
    """
    Returns initial boot information for the Brokerage Desk Vue app.
    """
    try:
        ensure_stock_group_setup()
    except Exception as e:
        frappe.log_error(f"ensure_stock_group_setup error: {e}", "Brokerage Module Setup")

    user = frappe.session.user
    user_info = frappe.db.get_value(
        "User", user, ["full_name", "user_image", "email"], as_dict=True
    ) or {}

    roles = frappe.get_roles(user)
    companies = frappe.get_all(
        "Company", fields=["name", "company_name", "default_currency"], ignore_permissions=True
    ) if frappe.db.exists("DocType", "Company") else []
    default_company = frappe.defaults.get_user_default("company") or (companies[0].name if companies else "")

    try:
        csrf_token = frappe.sessions.get_csrf_token()
    except Exception:
        csrf_token = getattr(frappe.session, "csrf_token", "") or ""

    return {
        "user": user,
        "full_name": user_info.get("full_name") or user,
        "user_image": user_info.get("user_image"),
        "roles": roles,
        "companies": companies,
        "default_company": default_company,
        "csrf_token": csrf_token,
        "today": nowdate(),
    }


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def search_entities(doctype=None, query=None, limit=30, for_purchase=None, for_sales=None, **kwargs):
    """
    Typeahead search for Broker, Supplier, Customer, Item.
    Supports filtering brokers by applicable_for_purchase or applicable_for_sales.
    """
    doctype = doctype or frappe.form_dict.get("doctype") or kwargs.get("doctype")
    query = (query if query is not None else (frappe.form_dict.get("query") or kwargs.get("query") or "")).strip()
    limit = int(limit or frappe.form_dict.get("limit") or kwargs.get("limit") or 30)

    if for_purchase is None:
        for_purchase = frappe.form_dict.get("for_purchase")
    if for_purchase is None and "for_purchase" in kwargs:
        for_purchase = kwargs.get("for_purchase")

    if for_sales is None:
        for_sales = frappe.form_dict.get("for_sales")
    if for_sales is None and "for_sales" in kwargs:
        for_sales = kwargs.get("for_sales")

    if not doctype:
        return []

    if doctype not in ("Broker", "Brokers") and not frappe.db.exists("DocType", doctype):
        return []

    filters = {}
    if doctype in ("Broker", "Brokers"):
        target_doctype = "Brokers" if frappe.db.exists("DocType", "Brokers") else "Broker"
        filters["status"] = "Active"
        if for_purchase in (1, "1", True, "true"):
            filters["applicable_for_purchase"] = 1
        elif for_purchase in (0, "0", False, "false"):
            filters["applicable_for_purchase"] = 0

        if for_sales in (1, "1", True, "true"):
            filters["applicable_for_sales"] = 1
        elif for_sales in (0, "0", False, "false"):
            filters["applicable_for_sales"] = 0

        fields = ["name", "broker_name", "mobile_no", "city", "applicable_for_purchase", "applicable_for_sales"]
        or_filters = []
        if query:
            or_filters = [
                ["broker_name", "like", f"%{query}%"],
                ["name", "like", f"%{query}%"],
                ["mobile_no", "like", f"%{query}%"],
                ["city", "like", f"%{query}%"],
            ]

        records = frappe.get_all(
            target_doctype,
            filters=filters,
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by="broker_name asc",
        )
        return [
            {
                "id": r.name,
                "name": r.name,
                "label": r.broker_name or r.name,
                "sub": f"{r.city or ''} {r.mobile_no or ''}".strip(),
                "applicable_for_purchase": r.applicable_for_purchase,
                "applicable_for_sales": r.applicable_for_sales,
            }
            for r in records
        ]

    elif doctype == "Supplier":
        fields = ["name", "supplier_name", "supplier_group"]
        or_filters = []
        if query:
            or_filters = [
                ["supplier_name", "like", f"%{query}%"],
                ["name", "like", f"%{query}%"],
            ]
        records = frappe.get_all(
            "Supplier",
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by="supplier_name asc",
        )
        return [
            {
                "id": r.name,
                "name": r.name,
                "label": r.supplier_name or r.name,
                "sub": r.supplier_group or "",
            }
            for r in records
        ]

    elif doctype == "Customer":
        fields = ["name", "customer_name", "customer_group"]
        or_filters = []
        if query:
            or_filters = [
                ["customer_name", "like", f"%{query}%"],
                ["name", "like", f"%{query}%"],
            ]
        records = frappe.get_all(
            "Customer",
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by="customer_name asc",
        )
        return [
            {
                "id": r.name,
                "name": r.name,
                "label": r.customer_name or r.name,
                "sub": r.customer_group or "",
            }
            for r in records
        ]

    elif doctype in ("Stock Group", "stock_group"):
        fields = ["name", "stock_group_name", "default_gst_rate", "description"]
        or_filters = []
        if query:
            or_filters = [
                ["stock_group_name", "like", f"%{query}%"],
                ["name", "like", f"%{query}%"],
            ]
        records = frappe.get_all(
            "Stock Group",
            filters={"is_active": 1},
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by="stock_group_name asc",
        )
        return [
            {
                "id": r.name,
                "name": r.name,
                "label": r.stock_group_name or r.name,
                "sub": f"Default GST: {flt(r.default_gst_rate or 5.0)}%",
                "default_gst_rate": flt(r.default_gst_rate or 5.0),
            }
            for r in records
        ]

    elif doctype == "Item":
        fields = ["name", "item_name", "item_group", "stock_uom", "stock_group", "gst_rate"]
        or_filters = []
        if query:
            or_filters = [
                ["item_name", "like", f"%{query}%"],
                ["name", "like", f"%{query}%"],
            ]
        records = frappe.get_all(
            "Item",
            filters={"disabled": 0},
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by="item_name asc",
        )
        return [
            {
                "id": r.name,
                "name": r.name,
                "label": r.item_name or r.name,
                "sub": f"Group: {r.stock_group or 'Sugar'} | {r.stock_uom or 'Qtl'} | GST: {flt(r.gst_rate if r.gst_rate is not None else 5.0)}%",
                "uom": r.stock_uom or "Quintal",
                "stock_group": r.stock_group or "Sugar",
                "gst_rate": flt(r.gst_rate if r.gst_rate is not None else 5.0),
            }
            for r in records
        ]

    return []


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_broker_details(broker=None):
    """
    Returns broker info including purchase_brokerage_rules and sales_brokerage_rules child rows.
    """
    broker_id = broker or frappe.form_dict.get("broker")
    if not broker_id:
        frappe.throw(_("Broker identifier is required."))

    target_dt = "Brokers" if (frappe.db.exists("Brokers", broker_id) or not frappe.db.exists("DocType", "Broker")) else "Broker"
    doc = frappe.get_doc(target_dt, broker_id)
    return {
        "name": doc.name,
        "broker_name": doc.broker_name,
        "mobile_no": doc.mobile_no,
        "city": doc.city,
        "state": doc.state,
        "status": doc.status,
        "applicable_for_purchase": getattr(doc, "applicable_for_purchase", 1),
        "applicable_for_sales": getattr(doc, "applicable_for_sales", 1),
        "purchase_brokerage_rules": [
            {
                "stock_group": r.stock_group,
                "stock_group_name": r.stock_group_name or (frappe.db.get_value("Stock Group", r.stock_group, "stock_group_name") if r.stock_group else "") or r.stock_group,
                "item": r.item,
                "item_name": r.item_name,
                "brokerage_method": r.brokerage_method,
                "percentage": flt(r.percentage),
                "per_bag": flt(r.per_bag),
                "per_quintal": flt(r.per_quintal),
                "remarks": r.remarks,
            }
            for r in doc.get("purchase_brokerage_rules", [])
        ],
        "sales_brokerage_rules": [
            {
                "stock_group": r.stock_group,
                "stock_group_name": r.stock_group_name or (frappe.db.get_value("Stock Group", r.stock_group, "stock_group_name") if r.stock_group else "") or r.stock_group,
                "item": r.item,
                "item_name": r.item_name,
                "brokerage_method": r.brokerage_method,
                "percentage": flt(r.percentage),
                "per_bag": flt(r.per_bag),
                "per_quintal": flt(r.per_quintal),
                "remarks": r.remarks,
            }
            for r in doc.get("sales_brokerage_rules", [])
        ],
    }


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_broker(data=None):
    """
    Creates or updates a Broker master in the dedicated Brokers doctype (Brokerage Module).
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    name = payload.get("name")
    if name and frappe.db.exists("Brokers", name):
        doc = frappe.get_doc("Brokers", name)
    elif name and frappe.db.exists("Broker", name):
        doc = frappe.get_doc("Broker", name)
    else:
        doc = frappe.new_doc("Brokers")

    doc.broker_name = payload.get("broker_name")
    doc.mobile_no = payload.get("mobile_no")
    doc.city = payload.get("city")
    doc.state = payload.get("state")
    doc.status = payload.get("status") or "Active"
    doc.applicable_for_purchase = 1 if payload.get("applicable_for_purchase") in (1, "1", True) else 0
    doc.applicable_for_sales = 1 if payload.get("applicable_for_sales") in (1, "1", True) else 0

    # Sync child tables
    doc.set("purchase_brokerage_rules", [])
    if doc.applicable_for_purchase:
        for r in payload.get("purchase_brokerage_rules", []):
            stk_grp = r.get("stock_group")
            itm = r.get("item")
            if not stk_grp and not itm:
                continue
            if not stk_grp and itm:
                stk_grp = frappe.db.get_value("Item", itm, "stock_group") or "Sugar"

            stk_grp_name = r.get("stock_group_name")
            if stk_grp and not stk_grp_name:
                stk_grp_name = frappe.db.get_value("Stock Group", stk_grp, "stock_group_name") or stk_grp

            method = r.get("brokerage_method") or "Percentage"
            pct = flt(r.get("percentage") or 0)
            bag = flt(r.get("per_bag") or 0)
            qtl = flt(r.get("per_quintal") or 0)
            # Enforce mutual exclusivity
            if method == "Percentage":
                bag, qtl = 0, 0
            elif method == "Per Bag":
                pct, qtl = 0, 0
            elif method == "Per Quintal":
                pct, bag = 0, 0

            doc.append("purchase_brokerage_rules", {
                "stock_group": stk_grp,
                "stock_group_name": stk_grp_name,
                "item": itm,
                "item_name": r.get("item_name") or (frappe.db.get_value("Item", itm, "item_name") if itm else ""),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.set("sales_brokerage_rules", [])
    if doc.applicable_for_sales:
        for r in payload.get("sales_brokerage_rules", []):
            stk_grp = r.get("stock_group")
            itm = r.get("item")
            if not stk_grp and not itm:
                continue
            if not stk_grp and itm:
                stk_grp = frappe.db.get_value("Item", itm, "stock_group") or "Sugar"

            stk_grp_name = r.get("stock_group_name")
            if stk_grp and not stk_grp_name:
                stk_grp_name = frappe.db.get_value("Stock Group", stk_grp, "stock_group_name") or stk_grp

            method = r.get("brokerage_method") or "Percentage"
            pct = flt(r.get("percentage") or 0)
            bag = flt(r.get("per_bag") or 0)
            qtl = flt(r.get("per_quintal") or 0)
            # Enforce mutual exclusivity
            if method == "Percentage":
                bag, qtl = 0, 0
            elif method == "Per Bag":
                pct, qtl = 0, 0
            elif method == "Per Quintal":
                pct, bag = 0, 0

            doc.append("sales_brokerage_rules", {
                "stock_group": stk_grp,
                "stock_group_name": stk_grp_name,
                "item": itm,
                "item_name": r.get("item_name") or (frappe.db.get_value("Item", itm, "item_name") if itm else ""),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.save()
    frappe.db.commit()
    return get_broker_details(doc.name)


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_broker_item_rate(broker=None, item=None, stock_group=None, entry_type="Purchase", posting_date=None):
    """
    Core business rule lookup:
    When broker and item (or stock group) are chosen, automatically find the configured rate and method.
    Search order:
    1. Active date-wise Broker Rate Configuration (<= posting_date, sorted DESC) by Stock Group (or item)
    2. Broker master table (purchase_brokerage_rules or sales_brokerage_rules) by Stock Group (or item)
    Also returns resolved GST rate and CGST/SGST breakdown.
    """
    broker = broker or frappe.form_dict.get("broker")
    item = item or frappe.form_dict.get("item")
    stock_group = stock_group or frappe.form_dict.get("stock_group")
    entry_type = (entry_type or frappe.form_dict.get("entry_type") or "Purchase").strip().capitalize()
    posting_date = posting_date or frappe.form_dict.get("posting_date") or nowdate()

    if not broker:
        return {"found": False}

    gst_rate = 5.0
    # Resolve Stock Group and GST from Item if item is supplied
    if item and frappe.db.exists("Item", item):
        it_data = frappe.db.get_value("Item", item, ["stock_group", "gst_rate"], as_dict=True) or {}
        if not stock_group and it_data.get("stock_group"):
            stock_group = it_data.get("stock_group")
        if it_data.get("gst_rate") is not None and flt(it_data.get("gst_rate")) > 0:
            gst_rate = flt(it_data.get("gst_rate"))

    if not stock_group:
        stock_group = "Sugar"

    # If gst_rate is still default 5.0, check stock_group default_gst_rate
    if frappe.db.exists("Stock Group", stock_group):
        sg_gst = frappe.db.get_value("Stock Group", stock_group, "default_gst_rate")
        if sg_gst is not None and (gst_rate == 5.0 or gst_rate == 0):
            gst_rate = flt(sg_gst)

    cgst_rate = round(gst_rate / 2.0, 4)
    sgst_rate = round(gst_rate / 2.0, 4)
    stock_group_name = frappe.db.get_value("Stock Group", stock_group, "stock_group_name") or stock_group

    table_field = "purchase_brokerage_rules" if entry_type == "Purchase" else "sales_brokerage_rules"

    # 1. Search in date-wise Broker Rate Configuration
    config_records = frappe.get_all(
        "Broker Rate Configuration",
        filters={
            "broker": broker,
            "status": "Active",
            "effective_date": ["<=", posting_date],
        },
        fields=["name", "effective_date"],
        order_by="effective_date desc",
        limit=1,
    )

    if config_records:
        cfg_name = config_records[0].name
        # Match by stock_group first
        child_rows = frappe.get_all(
            "Broker Rate Item",
            filters={
                "parent": cfg_name,
                "parentfield": table_field,
                "stock_group": stock_group,
            },
            fields=["stock_group", "stock_group_name", "item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
            limit=1,
        )
        # Fallback match by item
        if not child_rows and item:
            child_rows = frappe.get_all(
                "Broker Rate Item",
                filters={
                    "parent": cfg_name,
                    "parentfield": table_field,
                    "item": item,
                },
                fields=["stock_group", "stock_group_name", "item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
                limit=1,
            )

        if child_rows:
            r = child_rows[0]
            method = r.brokerage_method or "Percentage"
            rate_val = flt(r.percentage) if method == "Percentage" else (flt(r.per_bag) if method == "Per Bag" else flt(r.per_quintal))
            return {
                "found": True,
                "broker": broker,
                "item": item,
                "stock_group": stock_group,
                "stock_group_name": r.stock_group_name or stock_group_name,
                "brokerage_method": method,
                "rate": rate_val,
                "percentage": flt(r.percentage),
                "per_bag": flt(r.per_bag),
                "per_quintal": flt(r.per_quintal),
                "gst_rate": gst_rate,
                "cgst_rate": cgst_rate,
                "sgst_rate": sgst_rate,
                "source": f"Rate Card ({cfg_name})",
            }

    # 2. Search in Broker Master direct child tables
    # Match by stock_group first
    child_rows = frappe.get_all(
        "Broker Rate Item",
        filters={
            "parent": broker,
            "parentfield": table_field,
            "stock_group": stock_group,
        },
        fields=["stock_group", "stock_group_name", "item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
        limit=1,
    )
    # Fallback match by item
    if not child_rows and item:
        child_rows = frappe.get_all(
            "Broker Rate Item",
            filters={
                "parent": broker,
                "parentfield": table_field,
                "item": item,
            },
            fields=["stock_group", "stock_group_name", "item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
            limit=1,
        )

    if child_rows:
        r = child_rows[0]
        method = r.brokerage_method or "Percentage"
        rate_val = flt(r.percentage) if method == "Percentage" else (flt(r.per_bag) if method == "Per Bag" else flt(r.per_quintal))
        return {
            "found": True,
            "broker": broker,
            "item": item,
            "stock_group": stock_group,
            "stock_group_name": r.stock_group_name or stock_group_name,
            "brokerage_method": method,
            "rate": rate_val,
            "percentage": flt(r.percentage),
            "per_bag": flt(r.per_bag),
            "per_quintal": flt(r.per_quintal),
            "gst_rate": gst_rate,
            "cgst_rate": cgst_rate,
            "sgst_rate": sgst_rate,
            "source": f"Broker Master ({broker})",
        }

    return {
        "found": False,
        "broker": broker,
        "item": item,
        "stock_group": stock_group,
        "stock_group_name": stock_group_name,
        "gst_rate": gst_rate,
        "cgst_rate": cgst_rate,
        "sgst_rate": sgst_rate,
    }


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_rate_configuration(data=None):
    """
    Creates or updates a date-wise Broker Rate Configuration.
    Supports stock_group rules as well as item rules.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    name = payload.get("name")
    if name and frappe.db.exists("Broker Rate Configuration", name):
        doc = frappe.get_doc("Broker Rate Configuration", name)
    else:
        doc = frappe.new_doc("Broker Rate Configuration")

    doc.effective_date = payload.get("effective_date") or nowdate()
    doc.broker = payload.get("broker")
    doc.status = payload.get("status") or "Active"
    doc.remarks = payload.get("remarks")
    doc.sync_broker_flags()

    doc.set("purchase_brokerage_rules", [])
    if doc.applicable_for_purchase:
        for r in payload.get("purchase_brokerage_rules", []):
            stk_grp = r.get("stock_group")
            itm = r.get("item")
            if not stk_grp and not itm:
                continue
            if not stk_grp and itm:
                stk_grp = frappe.db.get_value("Item", itm, "stock_group") or "Sugar"

            stk_grp_name = r.get("stock_group_name")
            if stk_grp and not stk_grp_name:
                stk_grp_name = frappe.db.get_value("Stock Group", stk_grp, "stock_group_name") or stk_grp

            method = r.get("brokerage_method") or "Percentage"
            pct = flt(r.get("percentage") or 0)
            bag = flt(r.get("per_bag") or 0)
            qtl = flt(r.get("per_quintal") or 0)
            if method == "Percentage":
                bag, qtl = 0, 0
            elif method == "Per Bag":
                pct, qtl = 0, 0
            elif method == "Per Quintal":
                pct, bag = 0, 0

            doc.append("purchase_brokerage_rules", {
                "stock_group": stk_grp,
                "stock_group_name": stk_grp_name,
                "item": itm,
                "item_name": r.get("item_name") or (frappe.db.get_value("Item", itm, "item_name") if itm else ""),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.set("sales_brokerage_rules", [])
    if doc.applicable_for_sales:
        for r in payload.get("sales_brokerage_rules", []):
            stk_grp = r.get("stock_group")
            itm = r.get("item")
            if not stk_grp and not itm:
                continue
            if not stk_grp and itm:
                stk_grp = frappe.db.get_value("Item", itm, "stock_group") or "Sugar"

            stk_grp_name = r.get("stock_group_name")
            if stk_grp and not stk_grp_name:
                stk_grp_name = frappe.db.get_value("Stock Group", stk_grp, "stock_group_name") or stk_grp

            method = r.get("brokerage_method") or "Percentage"
            pct = flt(r.get("percentage") or 0)
            bag = flt(r.get("per_bag") or 0)
            qtl = flt(r.get("per_quintal") or 0)
            if method == "Percentage":
                bag, qtl = 0, 0
            elif method == "Per Bag":
                pct, qtl = 0, 0
            elif method == "Per Quintal":
                pct, bag = 0, 0

            doc.append("sales_brokerage_rules", {
                "stock_group": stk_grp,
                "stock_group_name": stk_grp_name,
                "item": itm,
                "item_name": r.get("item_name") or (frappe.db.get_value("Item", itm, "item_name") if itm else ""),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.save()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_rate_configurations(broker=None, limit=50):
    filters = {}
    if broker:
        filters["broker"] = broker
    records = frappe.get_all(
        "Broker Rate Configuration",
        filters=filters,
        fields=["name", "effective_date", "broker", "broker_name", "applicable_for_purchase", "applicable_for_sales", "status"],
        order_by="effective_date desc, creation desc",
        limit=int(limit or 50),
    )
    for r in records:
        r["purchase_rules_count"] = frappe.db.count("Broker Rate Item", {"parent": r.name, "parentfield": "purchase_brokerage_rules"})
        r["sales_rules_count"] = frappe.db.count("Broker Rate Item", {"parent": r.name, "parentfield": "sales_brokerage_rules"})
    return records


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_purchase_entry(data=None):
    """
    Submits a new Broker Purchase Entry with computed brokerage and GST.
    Supports both single-item and multi-item voucher payloads.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    doc = frappe.new_doc("Broker Purchase Entry")
    doc.posting_date = payload.get("posting_date") or nowdate()
    comp = payload.get("company") or frappe.defaults.get_user_default("company")
    if not comp and frappe.db.exists("DocType", "Company"):
        comps = frappe.get_all("Company", pluck="name")
        comp = comps[0] if comps else None
    doc.company = comp or "Default Company"
    doc.broker = payload.get("broker")
    b_name = payload.get("broker_name") or frappe.db.get_value("Brokers", doc.broker, "broker_name")
    if not b_name and frappe.db.exists("DocType", "Broker"):
        b_name = frappe.db.get_value("Broker", doc.broker, "broker_name")
    doc.broker_name = b_name or doc.broker
    doc.remarks = payload.get("remarks")

    items_list = payload.get("items")
    if items_list and isinstance(items_list, list) and len(items_list) > 0:
        for it in items_list:
            doc.append("items", {
                "item": it.get("item"),
                "item_name": it.get("item_name") or (frappe.db.get_value("Item", it.get("item"), "item_name") if it.get("item") else ""),
                "stock_group": it.get("stock_group") or (frappe.db.get_value("Item", it.get("item"), "stock_group") if it.get("item") else "Sugar"),
                "quantity": flt(it.get("quantity")),
                "bags": flt(it.get("bags") or (flt(it.get("quantity")) * 2.0)),
                "rate": flt(it.get("rate")),
                "gst_rate": flt(it.get("gst_rate") if it.get("gst_rate") is not None else 5.0),
                "brokerage_method": it.get("brokerage_method") or "Percentage",
                "brokerage_rate": flt(it.get("brokerage_rate")),
                "percentage": flt(it.get("percentage") or (flt(it.get("brokerage_rate")) if (it.get("brokerage_method") or "Percentage") == "Percentage" else 0)),
                "per_bag": flt(it.get("per_bag") or (flt(it.get("brokerage_rate")) if it.get("brokerage_method") == "Per Bag" else 0)),
                "per_quintal": flt(it.get("per_quintal") or (flt(it.get("brokerage_rate")) if it.get("brokerage_method") == "Per Quintal" else 0)),
                "rate_source": it.get("rate_source") or "Direct Entry",
                "remarks": it.get("remarks")
            })
    else:
        doc.item = payload.get("item")
        doc.stock_group = payload.get("stock_group") or (frappe.db.get_value("Item", doc.item, "stock_group") if doc.item else "Sugar")
        doc.quantity = flt(payload.get("quantity"))
        doc.bags = flt(payload.get("bags") or doc.quantity * 2.0)
        doc.rate = flt(payload.get("rate"))

        # GST rate
        if payload.get("gst_rate") is not None and str(payload.get("gst_rate")).strip() != "":
            doc.gst_rate = flt(payload.get("gst_rate"))
        elif doc.stock_group:
            sg_gst = frappe.db.get_value("Stock Group", doc.stock_group, "default_gst_rate")
            doc.gst_rate = flt(sg_gst) if sg_gst is not None else 5.0
        else:
            doc.gst_rate = 5.0

        doc.brokerage_method = payload.get("brokerage_method") or "Percentage"
        doc.brokerage_rate = flt(payload.get("brokerage_rate"))
        doc.percentage = flt(payload.get("percentage") or (doc.brokerage_rate if doc.brokerage_method == "Percentage" else 0))
        doc.per_bag = flt(payload.get("per_bag") or (doc.brokerage_rate if doc.brokerage_method == "Per Bag" else 0))
        doc.per_quintal = flt(payload.get("per_quintal") or (doc.brokerage_rate if doc.brokerage_method == "Per Quintal" else 0))
        doc.rate_source = payload.get("rate_source") or "Direct Entry"

    doc.flags.ignore_permissions = True
    doc.flags.ignore_links = True
    doc.insert()
    if payload.get("submit", True):
        doc.submit()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_sales_entry(data=None):
    """
    Submits a new Broker Sales Entry with computed brokerage and GST.
    Supports both single-item and multi-item voucher payloads.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    doc = frappe.new_doc("Broker Sales Entry")
    doc.posting_date = payload.get("posting_date") or nowdate()
    comp = payload.get("company") or frappe.defaults.get_user_default("company")
    if not comp and frappe.db.exists("DocType", "Company"):
        comps = frappe.get_all("Company", pluck="name")
        comp = comps[0] if comps else None
    doc.company = comp or "Default Company"
    doc.broker = payload.get("broker")
    b_name = payload.get("broker_name") or frappe.db.get_value("Brokers", doc.broker, "broker_name")
    if not b_name and frappe.db.exists("DocType", "Broker"):
        b_name = frappe.db.get_value("Broker", doc.broker, "broker_name")
    doc.broker_name = b_name or doc.broker
    doc.remarks = payload.get("remarks")

    items_list = payload.get("items")
    if items_list and isinstance(items_list, list) and len(items_list) > 0:
        for it in items_list:
            doc.append("items", {
                "item": it.get("item"),
                "item_name": it.get("item_name") or (frappe.db.get_value("Item", it.get("item"), "item_name") if it.get("item") else ""),
                "stock_group": it.get("stock_group") or (frappe.db.get_value("Item", it.get("item"), "stock_group") if it.get("item") else "Sugar"),
                "quantity": flt(it.get("quantity")),
                "bags": flt(it.get("bags") or (flt(it.get("quantity")) * 2.0)),
                "rate": flt(it.get("rate")),
                "gst_rate": flt(it.get("gst_rate") if it.get("gst_rate") is not None else 5.0),
                "brokerage_method": it.get("brokerage_method") or "Percentage",
                "brokerage_rate": flt(it.get("brokerage_rate")),
                "percentage": flt(it.get("percentage") or (flt(it.get("brokerage_rate")) if (it.get("brokerage_method") or "Percentage") == "Percentage" else 0)),
                "per_bag": flt(it.get("per_bag") or (flt(it.get("brokerage_rate")) if it.get("brokerage_method") == "Per Bag" else 0)),
                "per_quintal": flt(it.get("per_quintal") or (flt(it.get("brokerage_rate")) if it.get("brokerage_method") == "Per Quintal" else 0)),
                "rate_source": it.get("rate_source") or "Direct Entry",
                "remarks": it.get("remarks")
            })
    else:
        doc.item = payload.get("item")
        doc.stock_group = payload.get("stock_group") or (frappe.db.get_value("Item", doc.item, "stock_group") if doc.item else "Sugar")
        doc.quantity = flt(payload.get("quantity"))
        doc.bags = flt(payload.get("bags") or doc.quantity * 2.0)
        doc.rate = flt(payload.get("rate"))

        # GST rate
        if payload.get("gst_rate") is not None and str(payload.get("gst_rate")).strip() != "":
            doc.gst_rate = flt(payload.get("gst_rate"))
        elif doc.stock_group:
            sg_gst = frappe.db.get_value("Stock Group", doc.stock_group, "default_gst_rate")
            doc.gst_rate = flt(sg_gst) if sg_gst is not None else 5.0
        else:
            doc.gst_rate = 5.0

        doc.brokerage_method = payload.get("brokerage_method") or "Percentage"
        doc.brokerage_rate = flt(payload.get("brokerage_rate"))
        doc.percentage = flt(payload.get("percentage") or (doc.brokerage_rate if doc.brokerage_method == "Percentage" else 0))
        doc.per_bag = flt(payload.get("per_bag") or (doc.brokerage_rate if doc.brokerage_method == "Per Bag" else 0))
        doc.per_quintal = flt(payload.get("per_quintal") or (doc.brokerage_rate if doc.brokerage_method == "Per Quintal" else 0))
        doc.rate_source = payload.get("rate_source") or "Direct Entry"

    doc.flags.ignore_permissions = True
    doc.flags.ignore_links = True
    doc.insert()
    if payload.get("submit", True):
        doc.submit()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_entries(entry_type="Purchase", from_date=None, to_date=None, broker=None, limit=100):
    """
    Returns registered entries with totals including GST and Grand Total.
    """
    entry_type = (entry_type or "Purchase").strip().capitalize()
    doctype = "Broker Purchase Entry" if entry_type == "Purchase" else "Broker Sales Entry"

    filters = {}
    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["posting_date"] = [">=", from_date]
    elif to_date:
        filters["posting_date"] = ["<=", to_date]

    if broker:
        filters["broker"] = broker

    records = frappe.get_all(
        doctype,
        filters=filters,
        fields=[
            "name", "posting_date", "broker", "broker_name",
            "item", "item_name", "stock_group", "quantity", "bags", "rate", "trade_amount",
            "gst_rate", "cgst_rate", "cgst_amount", "sgst_rate", "sgst_amount", "total_gst_amount", "grand_total",
            "brokerage_method", "brokerage_rate", "brokerage_amount", "status", "rate_source"
        ],
        order_by="posting_date desc, creation desc",
        limit=int(limit or 100),
    )

    # Attach child items if present
    has_voucher_item_dt = frappe.db.exists("DocType", "Broker Voucher Item")
    for r in records:
        if has_voucher_item_dt:
            child_rows = frappe.get_all(
                "Broker Voucher Item",
                filters={"parent": r.name, "parenttype": doctype},
                fields=[
                    "item", "item_name", "stock_group", "quantity", "bags", "rate",
                    "trade_amount", "gst_rate", "cgst_amount", "sgst_amount", "total_gst_amount",
                    "grand_total", "brokerage_method", "brokerage_rate", "brokerage_amount", "rate_source"
                ],
                order_by="idx asc"
            )
            r["items"] = child_rows
            r["items_count"] = len(child_rows)
        else:
            r["items"] = []
            r["items_count"] = 0

    total_trade = sum(flt(r.trade_amount) for r in records)
    total_brokerage = sum(flt(r.brokerage_amount) for r in records)
    total_qty = sum(flt(r.quantity) for r in records)
    total_gst = sum(flt(r.get("total_gst_amount") or 0) for r in records)
    total_grand = sum(flt(r.get("grand_total") or r.get("trade_amount") or 0) for r in records)

    return {
        "records": records,
        "total_count": len(records),
        "total_trade": round(total_trade, 2),
        "total_brokerage": round(total_brokerage, 2),
        "total_qty": round(total_qty, 2),
        "total_gst": round(total_gst, 2),
        "total_grand": round(total_grand, 2),
    }


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_item_wise_register(from_date=None, to_date=None, broker=None, item=None, stock_group=None):
    """
    Returns item-wise aggregated trading and brokerage register.
    Consolidates both purchase and sales vouchers per commodity/item.
    """
    filters_p = {}
    filters_s = {}
    if from_date and to_date:
        filters_p["posting_date"] = ["between", [from_date, to_date]]
        filters_s["posting_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters_p["posting_date"] = [">=", from_date]
        filters_s["posting_date"] = [">=", from_date]
    elif to_date:
        filters_p["posting_date"] = ["<=", to_date]
        filters_s["posting_date"] = ["<=", to_date]

    if broker:
        filters_p["broker"] = broker
        filters_s["broker"] = broker

    has_voucher_item_dt = frappe.db.exists("DocType", "Broker Voucher Item")

    # Fetch all purchase entries
    p_entries = frappe.get_all(
        "Broker Purchase Entry",
        filters=filters_p,
        fields=[
            "name", "posting_date", "broker", "broker_name", "item", "item_name", "stock_group",
            "quantity", "bags", "rate", "trade_amount", "brokerage_amount", "grand_total", "status"
        ],
        order_by="posting_date desc, creation desc"
    )

    # Fetch all sales entries
    s_entries = frappe.get_all(
        "Broker Sales Entry",
        filters=filters_s,
        fields=[
            "name", "posting_date", "broker", "broker_name", "item", "item_name", "stock_group",
            "quantity", "bags", "rate", "trade_amount", "brokerage_amount", "grand_total", "status"
        ],
        order_by="posting_date desc, creation desc"
    )

    items_map = {}

    def process_entry(entry, voucher_type):
        child_rows = []
        if has_voucher_item_dt:
            child_rows = frappe.get_all(
                "Broker Voucher Item",
                filters={"parent": entry.name, "parenttype": "Broker Purchase Entry" if voucher_type == "Purchase" else "Broker Sales Entry"},
                fields=[
                    "item", "item_name", "stock_group", "quantity", "bags", "rate",
                    "trade_amount", "brokerage_method", "brokerage_rate", "brokerage_amount", "grand_total"
                ]
            )

        if not child_rows and entry.item:
            child_rows = [{
                "item": entry.item,
                "item_name": entry.item_name or entry.item,
                "stock_group": entry.stock_group or "Sugar",
                "quantity": flt(entry.quantity),
                "bags": flt(entry.bags),
                "rate": flt(entry.rate),
                "trade_amount": flt(entry.trade_amount),
                "brokerage_method": "Direct",
                "brokerage_rate": 0,
                "brokerage_amount": flt(entry.brokerage_amount),
                "grand_total": flt(entry.grand_total or entry.trade_amount)
            }]

        for row in child_rows:
            i_code = row.get("item")
            if not i_code:
                continue

            # Item and Stock group filters
            if item and i_code != item:
                continue
            i_sg = row.get("stock_group") or "Sugar"
            if stock_group and i_sg != stock_group:
                continue

            i_name = row.get("item_name") or i_code
            if i_code not in items_map:
                items_map[i_code] = {
                    "item_code": i_code,
                    "item_name": i_name,
                    "stock_group": i_sg,
                    "purchase_qty": 0.0,
                    "purchase_bags": 0.0,
                    "purchase_trade": 0.0,
                    "purchase_brokerage": 0.0,
                    "sales_qty": 0.0,
                    "sales_bags": 0.0,
                    "sales_trade": 0.0,
                    "sales_brokerage": 0.0,
                    "total_trade": 0.0,
                    "total_brokerage": 0.0,
                    "vouchers_count": 0,
                    "vouchers": []
                }

            rec = items_map[i_code]
            qty = flt(row.get("quantity"))
            bags = flt(row.get("bags"))
            trade = flt(row.get("trade_amount"))
            brk = flt(row.get("brokerage_amount"))

            if voucher_type == "Purchase":
                rec["purchase_qty"] += qty
                rec["purchase_bags"] += bags
                rec["purchase_trade"] += trade
                rec["purchase_brokerage"] += brk
            else:
                rec["sales_qty"] += qty
                rec["sales_bags"] += bags
                rec["sales_trade"] += trade
                rec["sales_brokerage"] += brk

            rec["total_trade"] += trade
            rec["total_brokerage"] += brk
            rec["vouchers_count"] += 1
            rec["vouchers"].append({
                "voucher": entry.name,
                "posting_date": str(entry.posting_date),
                "voucher_type": voucher_type,
                "broker": entry.broker,
                "broker_name": entry.broker_name,
                "quantity": qty,
                "bags": bags,
                "rate": flt(row.get("rate")),
                "trade_amount": trade,
                "brokerage_amount": brk,
                "grand_total": flt(row.get("grand_total") or trade),
                "status": entry.status
            })

    for p in p_entries:
        process_entry(p, "Purchase")
    for s in s_entries:
        process_entry(s, "Sell")

    # Round all values
    item_list = list(items_map.values())
    for itm in item_list:
        itm["purchase_qty"] = round(itm["purchase_qty"], 2)
        itm["purchase_bags"] = round(itm["purchase_bags"], 2)
        itm["purchase_trade"] = round(itm["purchase_trade"], 2)
        itm["purchase_brokerage"] = round(itm["purchase_brokerage"], 2)
        itm["sales_qty"] = round(itm["sales_qty"], 2)
        itm["sales_bags"] = round(itm["sales_bags"], 2)
        itm["sales_trade"] = round(itm["sales_trade"], 2)
        itm["sales_brokerage"] = round(itm["sales_brokerage"], 2)
        itm["total_trade"] = round(itm["total_trade"], 2)
        itm["total_brokerage"] = round(itm["total_brokerage"], 2)
        itm["net_qty"] = round(itm["purchase_qty"] - itm["sales_qty"], 2)

    item_list.sort(key=lambda x: x["total_trade"], reverse=True)

    summary = {
        "total_items": len(item_list),
        "total_purchase_qty": round(sum(i["purchase_qty"] for i in item_list), 2),
        "total_purchase_trade": round(sum(i["purchase_trade"] for i in item_list), 2),
        "total_purchase_brokerage": round(sum(i["purchase_brokerage"] for i in item_list), 2),
        "total_sales_qty": round(sum(i["sales_qty"] for i in item_list), 2),
        "total_sales_trade": round(sum(i["sales_trade"] for i in item_list), 2),
        "total_sales_brokerage": round(sum(i["sales_brokerage"] for i in item_list), 2),
        "overall_trade": round(sum(i["total_trade"] for i in item_list), 2),
        "overall_brokerage": round(sum(i["total_brokerage"] for i in item_list), 2),
        "total_vouchers": sum(i["vouchers_count"] for i in item_list)
    }

    return {
        "items": item_list,
        "summary": summary
    }


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_dashboard_summary():
    """
    Returns summary statistics for the Brokerage Desk.
    """
    broker_dt = "Brokers" if frappe.db.exists("DocType", "Brokers") else "Broker"
    total_brokers = frappe.db.count(broker_dt, {"status": "Active"})
    purchase_brokers = frappe.db.count(broker_dt, {"status": "Active", "applicable_for_purchase": 1})
    sales_brokers = frappe.db.count(broker_dt, {"status": "Active", "applicable_for_sales": 1})

    p_stats = frappe.db.sql("""
        SELECT COUNT(*), COALESCE(SUM(trade_amount), 0), COALESCE(SUM(brokerage_amount), 0)
        FROM `tabBroker Purchase Entry`
        WHERE docstatus = 1
    """)[0]

    s_stats = frappe.db.sql("""
        SELECT COUNT(*), COALESCE(SUM(trade_amount), 0), COALESCE(SUM(brokerage_amount), 0)
        FROM `tabBroker Sales Entry`
        WHERE docstatus = 1
    """)[0]

    return {
        "brokers": {
            "total": total_brokers,
            "purchase": purchase_brokers,
            "sales": sales_brokers,
        },
        "purchase": {
            "count": p_stats[0],
            "total_trade": round(flt(p_stats[1]), 2),
            "total_brokerage": round(flt(p_stats[2]), 2),
        },
        "sales": {
            "count": s_stats[0],
            "total_trade": round(flt(s_stats[1]), 2),
            "total_brokerage": round(flt(s_stats[2]), 2),
        },
    }


@frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
def sync_legacy_brokers():
    """
    Copies any legacy Broker records from sugar_module's Broker into brokerage_module's dedicated Brokers doctype.
    """
    synced = 0
    if not frappe.db.exists("DocType", "Broker"):
        return {"synced": 0, "total": frappe.db.count("Brokers")}

    brokers = frappe.get_all("Broker", fields=["*"])
    for b in brokers:
        if not frappe.db.exists("Brokers", b.name):
            new_b = frappe.new_doc("Brokers")
            new_b.name = b.name
            new_b.broker_name = b.broker_name
            new_b.mobile_no = b.mobile_no or ""
            new_b.email = b.email or ""
            new_b.address = b.address or ""
            new_b.city = b.city or ""
            new_b.state = b.state or ""
            new_b.gst_number = b.gst_number or ""
            new_b.status = b.status or "Active"
            new_b.applicable_for_purchase = b.applicable_for_purchase
            new_b.applicable_for_sales = b.applicable_for_sales

            # purchase rules
            p_rules = frappe.get_all(
                "Broker Rate Item",
                filters={"parent": b.name, "parenttype": "Broker", "parentfield": "purchase_brokerage_rules"},
                fields=["*"],
            )
            for r in p_rules:
                new_b.append("purchase_brokerage_rules", {
                    "item": r.item,
                    "item_name": r.item_name,
                    "brokerage_method": r.brokerage_method,
                    "percentage": r.percentage,
                    "per_bag": r.per_bag,
                    "per_quintal": r.per_quintal,
                    "remarks": r.remarks,
                })

            # sales rules
            s_rules = frappe.get_all(
                "Broker Rate Item",
                filters={"parent": b.name, "parenttype": "Broker", "parentfield": "sales_brokerage_rules"},
                fields=["*"],
            )
            for r in s_rules:
                new_b.append("sales_brokerage_rules", {
                    "item": r.item,
                    "item_name": r.item_name,
                    "brokerage_method": r.brokerage_method,
                    "percentage": r.percentage,
                    "per_bag": r.per_bag,
                    "per_quintal": r.per_quintal,
                    "remarks": r.remarks,
                })

            new_b.flags.ignore_permissions = True
            new_b.flags.ignore_mandatory = True
            new_b.insert(set_name=b.name)
            synced += 1

    frappe.db.commit()
    return {"synced": synced, "total_brokers": frappe.db.count("Brokers")}


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_sales_outstanding_register(from_date=None, to_date=None, broker=None, settlement_status=None, query=None, limit=200):
    """
    Returns Sales Outstandings Register:
    - Detailed voucher records with trade amount, brokerage, settled amount, outstanding trade, outstanding brokerage, days ageing.
    - Grouped broker summary with total trade dues and brokerage dues.
    - Summary KPI statistics and ageing buckets (0-7, 8-15, 16-30, 30+ days).
    """
    filters = {"docstatus": 1}

    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["posting_date"] = [">=", from_date]
    elif to_date:
        filters["posting_date"] = ["<=", to_date]

    if broker:
        filters["broker"] = broker

    if settlement_status and settlement_status != "All":
        filters["settlement_status"] = settlement_status

    fields = [
        "name", "posting_date", "broker", "broker_name",
        "item", "item_name", "stock_group", "quantity", "bags", "rate", "trade_amount",
        "gst_rate", "cgst_rate", "cgst_amount", "sgst_rate", "sgst_amount", "total_gst_amount", "grand_total",
        "brokerage_method", "brokerage_rate", "brokerage_amount",
        "settled_amount", "outstanding_amount", "settled_brokerage", "outstanding_brokerage",
        "settlement_status", "settlement_date", "status", "rate_source", "remarks"
    ]

    records = frappe.get_all(
        "Broker Sales Entry",
        filters=filters,
        fields=fields,
        order_by="posting_date desc, creation desc",
        limit=int(limit or 200),
    )

    today = getdate(nowdate())
    ageing_buckets = {
        "0-7 Days": {"count": 0, "trade_amount": 0.0, "brokerage": 0.0},
        "8-15 Days": {"count": 0, "trade_amount": 0.0, "brokerage": 0.0},
        "16-30 Days": {"count": 0, "trade_amount": 0.0, "brokerage": 0.0},
        "30+ Days": {"count": 0, "trade_amount": 0.0, "brokerage": 0.0},
    }

    broker_map = {}

    for r in records:
        trade_amt = flt(r.trade_amount)
        brk_amt = flt(r.brokerage_amount)
        settled_amt = flt(r.settled_amount)
        settled_brk = flt(r.settled_brokerage)

        out_trade = max(0.0, round(trade_amt - settled_amt, 2))
        out_brk = max(0.0, round(brk_amt - settled_brk, 2))

        r["trade_amount"] = trade_amt
        r["brokerage_amount"] = brk_amt
        r["settled_amount"] = settled_amt
        r["settled_brokerage"] = settled_brk
        r["outstanding_amount"] = out_trade
        r["outstanding_brokerage"] = out_brk

        p_date = getdate(r.posting_date) if r.posting_date else today
        days = (today - p_date).days
        r["days_outstanding"] = max(0, days)

        if days <= 7:
            bucket = "0-7 Days"
        elif days <= 15:
            bucket = "8-15 Days"
        elif days <= 30:
            bucket = "16-30 Days"
        else:
            bucket = "30+ Days"

        r["ageing_bucket"] = bucket

        # Tally ageing bucket
        ageing_buckets[bucket]["count"] += 1
        ageing_buckets[bucket]["trade_amount"] += out_trade
        ageing_buckets[bucket]["brokerage"] += out_brk

        # Group by broker
        b_key = r.broker or "Unknown"
        if b_key not in broker_map:
            broker_info = frappe.db.get_value("Brokers", b_key, ["mobile_no", "city"], as_dict=True) or {}
            broker_map[b_key] = {
                "broker": b_key,
                "broker_name": r.broker_name or b_key,
                "mobile_no": broker_info.get("mobile_no") or "",
                "city": broker_info.get("city") or "",
                "vouchers_count": 0,
                "pending_vouchers_count": 0,
                "total_quantity": 0.0,
                "total_bags": 0.0,
                "total_trade_amount": 0.0,
                "total_trade_outstanding": 0.0,
                "total_brokerage": 0.0,
                "total_brokerage_outstanding": 0.0,
                "settled_brokerage": 0.0,
                "status": "Settled",
                "vouchers": []
            }

        bm = broker_map[b_key]
        bm["vouchers_count"] += 1
        if r.settlement_status != "Settled":
            bm["pending_vouchers_count"] += 1
        bm["total_quantity"] += flt(r.quantity)
        bm["total_bags"] += flt(r.bags)
        bm["total_trade_amount"] += trade_amt
        bm["total_trade_outstanding"] += out_trade
        bm["total_brokerage"] += brk_amt
        bm["total_brokerage_outstanding"] += out_brk
        bm["settled_brokerage"] += settled_brk
        bm["vouchers"].append(r)

    # Format broker map
    broker_summary = []
    for bm in broker_map.values():
        bm["total_quantity"] = round(bm["total_quantity"], 2)
        bm["total_bags"] = round(bm["total_bags"], 2)
        bm["total_trade_amount"] = round(bm["total_trade_amount"], 2)
        bm["total_trade_outstanding"] = round(bm["total_trade_outstanding"], 2)
        bm["total_brokerage"] = round(bm["total_brokerage"], 2)
        bm["total_brokerage_outstanding"] = round(bm["total_brokerage_outstanding"], 2)
        bm["settled_brokerage"] = round(bm["settled_brokerage"], 2)

        if bm["total_brokerage_outstanding"] <= 0 and bm["total_trade_outstanding"] <= 0:
            bm["status"] = "Settled"
        elif bm["total_brokerage_outstanding"] >= 10000 or bm["total_trade_outstanding"] >= 500000:
            bm["status"] = "High Due"
        else:
            bm["status"] = "Due"
        broker_summary.append(bm)

    broker_summary.sort(key=lambda x: (x["total_brokerage_outstanding"], x["total_trade_outstanding"]), reverse=True)

    # Text Query Filter if provided
    if query:
        q = query.lower()
        records = [
            r for r in records
            if q in r["name"].lower()
            or q in (r.get("broker_name") or "").lower()
            or q in (r.get("broker") or "").lower()
            or q in (r.get("item_name") or "").lower()
        ]
        broker_summary = [
            b for b in broker_summary
            if q in b["broker_name"].lower()
            or q in b["broker"].lower()
            or q in b["city"].lower()
        ]

    total_trade = sum(r["trade_amount"] for r in records)
    total_trade_out = sum(r["outstanding_amount"] for r in records)
    total_brk = sum(r["brokerage_amount"] for r in records)
    total_brk_out = sum(r["outstanding_brokerage"] for r in records)
    total_brk_settled = sum(r["settled_brokerage"] for r in records)
    total_qty = sum(flt(r.quantity) for r in records)
    total_bags = sum(flt(r.bags) for r in records)

    pending_count = sum(1 for r in records if r["settlement_status"] != "Settled")
    settled_count = sum(1 for r in records if r["settlement_status"] == "Settled")
    brokers_with_dues = sum(1 for b in broker_summary if b["total_brokerage_outstanding"] > 0 or b["total_trade_outstanding"] > 0)

    for k in ageing_buckets:
        ageing_buckets[k]["trade_amount"] = round(ageing_buckets[k]["trade_amount"], 2)
        ageing_buckets[k]["brokerage"] = round(ageing_buckets[k]["brokerage"], 2)

    return {
        "records": records,
        "broker_summary": broker_summary,
        "summary": {
            "total_vouchers": len(records),
            "pending_vouchers": pending_count,
            "settled_vouchers": settled_count,
            "total_trade_volume": round(total_trade, 2),
            "total_trade_outstanding": round(total_trade_out, 2),
            "total_brokerage": round(total_brk, 2),
            "total_brokerage_outstanding": round(total_brk_out, 2),
            "total_brokerage_settled": round(total_brk_settled, 2),
            "total_qty": round(total_qty, 2),
            "total_bags": round(total_bags, 2),
            "total_brokers": len(broker_summary),
            "brokers_with_dues": brokers_with_dues,
            "ageing_summary": ageing_buckets,
        }
    }


@frappe.whitelist(methods=["POST"], allow_guest=True)
def settle_sales_entry(voucher_id=None, settled_trade_amount=None, settled_brokerage=None, remarks=None, mark_full=False, **kwargs):
    """
    Records settlement against a Broker Sales Entry voucher.
    """
    voucher_id = voucher_id or frappe.form_dict.get("voucher_id") or kwargs.get("voucher_id")
    if not voucher_id or not frappe.db.exists("Broker Sales Entry", voucher_id):
        frappe.throw(_("Broker Sales Entry {0} not found.").format(voucher_id))

    doc = frappe.get_doc("Broker Sales Entry", voucher_id)
    raw_mark_full = mark_full if mark_full is not None else frappe.form_dict.get("mark_full")
    is_mark_full = raw_mark_full in (1, "1", True, "true")

    if is_mark_full:
        doc.settled_amount = doc.trade_amount
        doc.settled_brokerage = doc.brokerage_amount
        doc.outstanding_amount = 0.0
        doc.outstanding_brokerage = 0.0
        doc.settlement_status = "Settled"
        doc.settlement_date = nowdate()
    else:
        if settled_trade_amount is not None:
            doc.settled_amount = flt(settled_trade_amount)
        if settled_brokerage is not None:
            doc.settled_brokerage = flt(settled_brokerage)

        doc.outstanding_amount = max(0.0, round(flt(doc.trade_amount) - flt(doc.settled_amount), 2))
        doc.outstanding_brokerage = max(0.0, round(flt(doc.brokerage_amount) - flt(doc.settled_brokerage), 2))

        if doc.outstanding_brokerage <= 0 and (doc.settled_brokerage > 0 or doc.settled_amount >= doc.trade_amount):
            doc.settlement_status = "Settled"
        elif doc.settled_brokerage > 0 or doc.settled_amount > 0:
            doc.settlement_status = "Partially Settled"
        else:
            doc.settlement_status = "Pending"

        doc.settlement_date = nowdate()

    if remarks:
        existing = (doc.remarks or "").strip()
        doc.remarks = f"{existing}\n[Settlement {nowdate()}]: {remarks}".strip()

    doc.db_set({
        "settled_amount": doc.settled_amount,
        "settled_brokerage": doc.settled_brokerage,
        "outstanding_amount": doc.outstanding_amount,
        "outstanding_brokerage": doc.outstanding_brokerage,
        "settlement_status": doc.settlement_status,
        "settlement_date": doc.settlement_date,
        "remarks": doc.remarks,
    })
    frappe.db.commit()

    return {
        "success": True,
        "name": doc.name,
        "settlement_status": doc.settlement_status,
        "settled_amount": doc.settled_amount,
        "outstanding_amount": doc.outstanding_amount,
        "settled_brokerage": doc.settled_brokerage,
        "outstanding_brokerage": doc.outstanding_brokerage,
    }



