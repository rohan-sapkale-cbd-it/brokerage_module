import json
import frappe
import frappe.sessions
from frappe import _
from frappe.utils import flt, nowdate, getdate, now, cstr


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_boot():
    """
    Returns initial boot information for the Brokerage Desk Vue app.
    """
    user = frappe.session.user
    user_info = frappe.db.get_value(
        "User", user, ["full_name", "user_image", "email"], as_dict=True
    ) or {}

    roles = frappe.get_roles(user)
    companies = frappe.get_all(
        "Company", fields=["name", "company_name", "default_currency"], ignore_permissions=True
    )
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


@frappe.whitelist(methods=["GET", "POST"])
def search_entities(doctype=None, query=None, limit=30, **kwargs):
    """
    Typeahead search for Broker, Supplier, Customer, Item.
    Supports filtering brokers by applicable_for_purchase or applicable_for_sales.
    """
    doctype = doctype or frappe.form_dict.get("doctype")
    query = (query or frappe.form_dict.get("query") or "").strip()
    limit = int(limit or frappe.form_dict.get("limit") or 30)
    for_purchase = frappe.form_dict.get("for_purchase")
    for_sales = frappe.form_dict.get("for_sales")

    if not doctype:
        return []

    filters = {}
    if doctype == "Broker":
        filters["status"] = "Active"
        if for_purchase in (1, "1", True, "true"):
            filters["applicable_for_purchase"] = 1
        if for_sales in (1, "1", True, "true"):
            filters["applicable_for_sales"] = 1

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
            "Broker",
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

    elif doctype == "Item":
        fields = ["name", "item_name", "item_group", "stock_uom"]
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
                "sub": f"{r.item_group or ''} ({r.stock_uom or 'Qtl'})".strip(),
                "uom": r.stock_uom or "Quintal",
            }
            for r in records
        ]

    return []


@frappe.whitelist(methods=["GET", "POST"])
def get_broker_details(broker=None):
    """
    Returns broker info including purchase_brokerage_rules and sales_brokerage_rules child rows.
    """
    broker_id = broker or frappe.form_dict.get("broker")
    if not broker_id:
        frappe.throw(_("Broker identifier is required."))

    doc = frappe.get_doc("Broker", broker_id)
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


@frappe.whitelist(methods=["POST"])
def save_broker(data=None):
    """
    Creates or updates a Broker master with checkpoints & rules tables.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    name = payload.get("name")
    if name and frappe.db.exists("Broker", name):
        doc = frappe.get_doc("Broker", name)
    else:
        doc = frappe.new_doc("Broker")

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
            if not r.get("item"):
                continue
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
                "item": r.get("item"),
                "item_name": r.get("item_name") or frappe.db.get_value("Item", r.get("item"), "item_name"),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.set("sales_brokerage_rules", [])
    if doc.applicable_for_sales:
        for r in payload.get("sales_brokerage_rules", []):
            if not r.get("item"):
                continue
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
                "item": r.get("item"),
                "item_name": r.get("item_name") or frappe.db.get_value("Item", r.get("item"), "item_name"),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.save()
    frappe.db.commit()
    return get_broker_details(doc.name)


@frappe.whitelist(methods=["GET", "POST"])
def get_broker_item_rate(broker=None, item=None, entry_type="Purchase", posting_date=None):
    """
    Core business rule lookup:
    When broker and item are chosen, automatically find the configured rate and method.
    Search order:
    1. Active date-wise Broker Rate Configuration (<= posting_date, sorted DESC)
    2. Broker master table (purchase_brokerage_rules or sales_brokerage_rules)
    """
    broker = broker or frappe.form_dict.get("broker")
    item = item or frappe.form_dict.get("item")
    entry_type = (entry_type or frappe.form_dict.get("entry_type") or "Purchase").strip().capitalize()
    posting_date = posting_date or frappe.form_dict.get("posting_date") or nowdate()

    if not broker or not item:
        return {"found": False}

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
        child_rows = frappe.get_all(
            "Broker Rate Item",
            filters={
                "parent": cfg_name,
                "parentfield": table_field,
                "item": item,
            },
            fields=["item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
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
                "brokerage_method": method,
                "rate": rate_val,
                "percentage": flt(r.percentage),
                "per_bag": flt(r.per_bag),
                "per_quintal": flt(r.per_quintal),
                "source": f"Rate Card ({cfg_name})",
            }

    # 2. Search in Broker Master direct child tables
    child_rows = frappe.get_all(
        "Broker Rate Item",
        filters={
            "parent": broker,
            "parentfield": table_field,
            "item": item,
        },
        fields=["item", "item_name", "brokerage_method", "percentage", "per_bag", "per_quintal"],
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
            "brokerage_method": method,
            "rate": rate_val,
            "percentage": flt(r.percentage),
            "per_bag": flt(r.per_bag),
            "per_quintal": flt(r.per_quintal),
            "source": f"Broker Master ({broker})",
        }

    return {"found": False, "broker": broker, "item": item}


@frappe.whitelist(methods=["POST"])
def save_rate_configuration(data=None):
    """
    Creates or updates a date-wise Broker Rate Configuration.
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
            if not r.get("item"):
                continue
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
                "item": r.get("item"),
                "item_name": r.get("item_name") or frappe.db.get_value("Item", r.get("item"), "item_name"),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.set("sales_brokerage_rules", [])
    if doc.applicable_for_sales:
        for r in payload.get("sales_brokerage_rules", []):
            if not r.get("item"):
                continue
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
                "item": r.get("item"),
                "item_name": r.get("item_name") or frappe.db.get_value("Item", r.get("item"), "item_name"),
                "brokerage_method": method,
                "percentage": pct,
                "per_bag": bag,
                "per_quintal": qtl,
                "remarks": r.get("remarks"),
            })

    doc.save()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"])
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


@frappe.whitelist(methods=["POST"])
def save_purchase_entry(data=None):
    """
    Submits a new Broker Purchase Entry with computed brokerage.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    doc = frappe.new_doc("Broker Purchase Entry")
    doc.posting_date = payload.get("posting_date") or nowdate()
    doc.company = payload.get("company") or frappe.defaults.get_user_default("company") or frappe.get_all("Company", pluck="name")[0]
    doc.broker = payload.get("broker")
    doc.supplier = payload.get("supplier")
    doc.item = payload.get("item")
    doc.quantity = flt(payload.get("quantity"))
    doc.bags = flt(payload.get("bags") or doc.quantity * 2.0)
    doc.rate = flt(payload.get("rate"))
    doc.brokerage_method = payload.get("brokerage_method") or "Percentage"
    doc.brokerage_rate = flt(payload.get("brokerage_rate"))
    doc.percentage = flt(payload.get("percentage") or (doc.brokerage_rate if doc.brokerage_method == "Percentage" else 0))
    doc.per_bag = flt(payload.get("per_bag") or (doc.brokerage_rate if doc.brokerage_method == "Per Bag" else 0))
    doc.per_quintal = flt(payload.get("per_quintal") or (doc.brokerage_rate if doc.brokerage_method == "Per Quintal" else 0))
    doc.rate_source = payload.get("rate_source") or "Direct Entry"
    doc.remarks = payload.get("remarks")

    doc.insert()
    if payload.get("submit", True):
        doc.submit()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def save_sales_entry(data=None):
    """
    Submits a new Broker Sales Entry with computed brokerage.
    """
    if isinstance(data, str):
        payload = json.loads(data)
    else:
        payload = data or frappe.form_dict

    doc = frappe.new_doc("Broker Sales Entry")
    doc.posting_date = payload.get("posting_date") or nowdate()
    doc.company = payload.get("company") or frappe.defaults.get_user_default("company") or frappe.get_all("Company", pluck="name")[0]
    doc.broker = payload.get("broker")
    doc.customer = payload.get("customer")
    doc.item = payload.get("item")
    doc.quantity = flt(payload.get("quantity"))
    doc.bags = flt(payload.get("bags") or doc.quantity * 2.0)
    doc.rate = flt(payload.get("rate"))
    doc.brokerage_method = payload.get("brokerage_method") or "Percentage"
    doc.brokerage_rate = flt(payload.get("brokerage_rate"))
    doc.percentage = flt(payload.get("percentage") or (doc.brokerage_rate if doc.brokerage_method == "Percentage" else 0))
    doc.per_bag = flt(payload.get("per_bag") or (doc.brokerage_rate if doc.brokerage_method == "Per Bag" else 0))
    doc.per_quintal = flt(payload.get("per_quintal") or (doc.brokerage_rate if doc.brokerage_method == "Per Quintal" else 0))
    doc.rate_source = payload.get("rate_source") or "Direct Entry"
    doc.remarks = payload.get("remarks")

    doc.insert()
    if payload.get("submit", True):
        doc.submit()
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"])
def get_entries(entry_type="Purchase", from_date=None, to_date=None, broker=None, limit=100):
    """
    Returns registered entries with totals.
    """
    entry_type = (entry_type or "Purchase").strip().capitalize()
    doctype = "Broker Purchase Entry" if entry_type == "Purchase" else "Broker Sales Entry"
    party_field = "supplier" if entry_type == "Purchase" else "customer"

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
            "name", "posting_date", "broker", "broker_name", party_field,
            "item", "item_name", "quantity", "bags", "rate", "trade_amount",
            "brokerage_method", "brokerage_rate", "brokerage_amount", "status", "rate_source"
        ],
        order_by="posting_date desc, creation desc",
        limit=int(limit or 100),
    )

    total_trade = sum(flt(r.trade_amount) for r in records)
    total_brokerage = sum(flt(r.brokerage_amount) for r in records)
    total_qty = sum(flt(r.quantity) for r in records)

    return {
        "records": records,
        "total_count": len(records),
        "total_trade": round(total_trade, 2),
        "total_brokerage": round(total_brokerage, 2),
        "total_qty": round(total_qty, 2),
    }


@frappe.whitelist(methods=["GET", "POST"])
def get_dashboard_summary():
    """
    Returns summary statistics for the Brokerage Desk.
    """
    total_brokers = frappe.db.count("Broker", {"status": "Active"})
    purchase_brokers = frappe.db.count("Broker", {"status": "Active", "applicable_for_purchase": 1})
    sales_brokers = frappe.db.count("Broker", {"status": "Active", "applicable_for_sales": 1})

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
