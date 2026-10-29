import frappe
from frappe.utils import nowdate
from brokerage_module.brokerage_module.api import (
    save_broker,
    get_broker_details,
    get_broker_item_rate,
    save_rate_configuration,
    save_purchase_entry,
    save_sales_entry,
    get_entries,
    get_dashboard_summary
)


def ensure_test_prerequisites():
    """Ensure Company, Item, and Stock Group DocTypes and records exist so tests can run self-contained."""
    # 1. Ensure Company DocType and record exist
    if not frappe.db.exists("DocType", "Company"):
        dt = frappe.new_doc("DocType")
        dt.name = "Company"
        dt.module = "Brokerage Module"
        dt.custom = 1
        dt.fields = [
            {"fieldname": "company_name", "fieldtype": "Data", "label": "Company Name", "reqd": 1},
            {"fieldname": "default_currency", "fieldtype": "Data", "label": "Default Currency"}
        ]
        dt.insert(ignore_permissions=True)

    companies = frappe.get_all("Company", limit=1, pluck="name")
    if not companies:
        c = frappe.new_doc("Company")
        c.company_name = "Test Brokerage Trading Co"
        if hasattr(c, "default_currency"):
            c.default_currency = "INR"
        c.insert(ignore_permissions=True)
        company_name = c.name
    else:
        company_name = companies[0]

    # 2. Ensure Item DocType exists
    if not frappe.db.exists("DocType", "Item"):
        item_dt = frappe.new_doc("DocType")
        item_dt.name = "Item"
        item_dt.module = "Brokerage Module"
        item_dt.custom = 1
        item_dt.fields = [
            {"fieldname": "item_code", "fieldtype": "Data", "label": "Item Code", "reqd": 1},
            {"fieldname": "item_name", "fieldtype": "Data", "label": "Item Name"},
            {"fieldname": "item_group", "fieldtype": "Data", "label": "Item Group"},
            {"fieldname": "stock_group", "fieldtype": "Link", "options": "Stock Group", "label": "Stock Group"},
            {"fieldname": "gst_rate", "fieldtype": "Percent", "label": "GST Rate"},
            {"fieldname": "stock_uom", "fieldtype": "Data", "label": "Stock UOM"},
            {"fieldname": "standard_rate", "fieldtype": "Currency", "label": "Standard Rate"},
            {"fieldname": "description", "fieldtype": "Small Text", "label": "Description"}
        ]
        item_dt.insert(ignore_permissions=True)

    # 3. Ensure Stock Group setup
    from brokerage_module.brokerage_module.api import ensure_stock_group_setup
    ensure_stock_group_setup()

    # 4. Get or create test items
    items = frappe.get_all("Item", limit=2, pluck="name")
    if not items:
        item_doc = frappe.new_doc("Item")
        item_doc.item_code = "TEST-COMMODITY-A"
        item_doc.item_name = "Test Sugar Commodity A"
        item_doc.stock_uom = "Quintal"
        item_doc.stock_group = "Sugar"
        item_doc.gst_rate = 5.0
        item_doc.insert(ignore_permissions=True)

        item_doc_b = frappe.new_doc("Item")
        item_doc_b.item_code = "TEST-COMMODITY-B"
        item_doc_b.item_name = "Test Sugar Commodity B"
        item_doc_b.stock_uom = "Quintal"
        item_doc_b.stock_group = "Sugar"
        item_doc_b.gst_rate = 5.0
        item_doc_b.insert(ignore_permissions=True)

        items = [item_doc.name, item_doc_b.name]

    item_a = items[0]
    item_b = items[1] if len(items) > 1 else items[0]

    return company_name, item_a, item_b


def run_tests():
    print("==================================================")
    print("STARTING BROKERAGE MODULE INTEGRATION TESTS")
    print("==================================================")

    company, item_a, item_b = ensure_test_prerequisites()
    print(f"[OK] Using Company: {company}")
    print(f"[OK] Using Items: {item_a}, {item_b}")

    # 3. Test Broker Creation with Checkpoints & Tables
    print("\n--- Test 1: Create Broker with Checkpoints & 3-Method Table ---")
    broker_payload = {
        "broker_name": "Kailash Broker Enterprise",
        "mobile_no": "9876543210",
        "city": "Pune",
        "state": "Maharashtra",
        "status": "Active",
        "applicable_for_purchase": 1,
        "applicable_for_sales": 1,
        "purchase_brokerage_rules": [
            {
                "item": item_a,
                "brokerage_method": "Percentage",
                "percentage": 5.0,
                "per_bag": 0,
                "per_quintal": 0,
                "remarks": "5% Purchase Brokerage"
            }
        ],
        "sales_brokerage_rules": [
            {
                "item": item_b,
                "brokerage_method": "Per Bag",
                "percentage": 0,
                "per_bag": 12.5,
                "per_quintal": 0,
                "remarks": "₹12.5 per bag sell brokerage"
            }
        ]
    }

    broker_res = save_broker(broker_payload)
    broker_id = broker_res["name"]
    assert broker_res["applicable_for_purchase"] == 1, "applicable_for_purchase should be 1"
    assert broker_res["applicable_for_sales"] == 1, "applicable_for_sales should be 1"
    assert len(broker_res["purchase_brokerage_rules"]) >= 1, "Purchase table should have 1 item"
    assert broker_res["purchase_brokerage_rules"][0]["percentage"] == 5.0, "Expected 5.0%"
    assert broker_res["sales_brokerage_rules"][0]["per_bag"] == 12.5, "Expected 12.5 / bag"
    print(f"  [PASS] Broker created: {broker_id} with purchase & sell checkpoint tables!")

    # 4. Test Auto-fetch lookup (Item A for Purchase -> Percentage 5%)
    print("\n--- Test 2: Auto-fetch Brokerage Rule in Purchase (Expect 5%) ---")
    lookup_purchase = get_broker_item_rate(broker=broker_id, item=item_a, entry_type="Purchase")
    assert lookup_purchase["found"] is True, "Lookup must find the rate"
    assert lookup_purchase["brokerage_method"] == "Percentage", f"Expected Percentage, got {lookup_purchase['brokerage_method']}"
    assert lookup_purchase["rate"] == 5.0, f"Expected 5.0, got {lookup_purchase['rate']}"
    print(f"  [PASS] Successfully fetched: {lookup_purchase['brokerage_method']} @ {lookup_purchase['rate']}% (Source: {lookup_purchase['source']})")

    # 5. Test Auto-fetch lookup (Item B for Sell -> Per Bag 12.5)
    print("\n--- Test 3: Auto-fetch Brokerage Rule in Sell (Expect Per Bag 12.5) ---")
    lookup_sell = get_broker_item_rate(broker=broker_id, item=item_b, entry_type="Sell")
    assert lookup_sell["found"] is True, "Lookup must find sell rate"
    assert lookup_sell["brokerage_method"] == "Per Bag", f"Expected Per Bag, got {lookup_sell['brokerage_method']}"
    assert lookup_sell["rate"] == 12.5, f"Expected 12.5, got {lookup_sell['rate']}"
    print(f"  [PASS] Successfully fetched: {lookup_sell['brokerage_method']} @ ₹{lookup_sell['rate']}/bag")

    # 6. Test Date-Wise Broker Rate Configuration (Override Item A with Per Quintal ₹25)
    print("\n--- Test 4: Create Date-wise Broker Rate Configuration (Separate DocType) ---")
    config_payload = {
        "effective_date": nowdate(),
        "broker": broker_id,
        "status": "Active",
        "remarks": "Special festive date-wise rates",
        "purchase_brokerage_rules": [
            {
                "item": item_a,
                "brokerage_method": "Per Quintal",
                "percentage": 0,
                "per_bag": 0,
                "per_quintal": 25.0,
                "remarks": "Festive rate override"
            }
        ]
    }
    cfg_res = save_rate_configuration(config_payload)
    cfg_id = cfg_res["name"]
    print(f"  [PASS] Date-wise configuration created: {cfg_id}")

    # 7. Test Date-wise override lookup
    print("\n--- Test 5: Verify Date-Wise Rate Override Lookup ---")
    lookup_override = get_broker_item_rate(broker=broker_id, item=item_a, entry_type="Purchase", posting_date=nowdate())
    assert lookup_override["found"] is True, "Must find date-wise override"
    assert lookup_override["brokerage_method"] == "Per Quintal", f"Expected Per Quintal, got {lookup_override['brokerage_method']}"
    assert lookup_override["rate"] == 25.0, f"Expected 25.0, got {lookup_override['rate']}"
    print(f"  [PASS] Successfully overridden by date-wise config: {lookup_override['brokerage_method']} @ ₹{lookup_override['rate']}/qtl")

    # 8. Test Purchase Entry Submission & Brokerage Calculation
    print("\n--- Test 6: Create & Submit Broker Purchase Entry ---")
    p_entry = save_purchase_entry({
        "posting_date": nowdate(),
        "company": company,
        "broker": broker_id,
        "item": item_a,
        "quantity": 100,  # 100 Qtl
        "bags": 200,      # 200 Bags
        "rate": 3800,     # ₹3800 / Qtl
        "brokerage_method": lookup_override["brokerage_method"],
        "brokerage_rate": lookup_override["rate"],
        "per_quintal": lookup_override["per_quintal"],
        "rate_source": lookup_override["source"],
        "submit": True
    })
    assert p_entry["trade_amount"] == 380000.0, f"Expected 380000, got {p_entry['trade_amount']}"
    assert p_entry["brokerage_amount"] == 2500.0, f"Expected 2500 (100 Qtl * 25), got {p_entry['brokerage_amount']}"
    assert p_entry["status"] == "Submitted", "Entry should be submitted"
    print(f"  [PASS] Purchase Entry {p_entry['name']}: Trade Amt ₹{p_entry['trade_amount']}, Brokerage ₹{p_entry['brokerage_amount']}")

    # 9. Test Sales Entry Submission & Brokerage Calculation
    print("\n--- Test 7: Create & Submit Broker Sales Entry ---")
    s_entry = save_sales_entry({
        "posting_date": nowdate(),
        "company": company,
        "broker": broker_id,
        "item": item_b,
        "quantity": 50,  # 50 Qtl
        "bags": 100,     # 100 Bags
        "rate": 4000,    # ₹4000 / Qtl
        "brokerage_method": lookup_sell["brokerage_method"],
        "brokerage_rate": lookup_sell["rate"],
        "per_bag": lookup_sell["per_bag"],
        "rate_source": lookup_sell["source"],
        "submit": True
    })
    assert s_entry["trade_amount"] == 200000.0, f"Expected 200000, got {s_entry['trade_amount']}"
    assert s_entry["brokerage_amount"] == 1250.0, f"Expected 1250 (100 bags * 12.5), got {s_entry['brokerage_amount']}"
    assert s_entry["status"] == "Submitted", "Entry should be submitted"
    print(f"  [PASS] Sales Entry {s_entry['name']}: Trade Amt ₹{s_entry['trade_amount']}, Brokerage ₹{s_entry['brokerage_amount']}")

    # 10. Test Registers & Dashboard Stats
    print("\n--- Test 8: Registers & Dashboard Analytics ---")
    p_reg = get_entries(entry_type="Purchase", broker=broker_id)
    assert p_reg["total_count"] >= 1, "Should have at least 1 purchase record"
    assert p_reg["total_trade"] >= 380000.0, "Trade total should match"
    assert p_reg["total_brokerage"] >= 2500.0, "Brokerage total should match"

    stats = get_dashboard_summary()
    assert stats["brokers"]["total"] >= 1
    assert stats["purchase"]["count"] >= 1
    assert stats["sales"]["count"] >= 1
    print(f"  [PASS] Dashboard: {stats['brokers']['total']} brokers, Purchase: ₹{stats['purchase']['total_trade']} (Brk: ₹{stats['purchase']['total_brokerage']}), Sales: ₹{stats['sales']['total_trade']} (Brk: ₹{stats['sales']['total_brokerage']})")

    # 11. Test Sales Outstandings Register & Settlement
    print("\n--- Test 9: Sales Outstanding Register & Settlement ---")
    from brokerage_module.brokerage_module.api import get_sales_outstanding_register, settle_sales_entry
    out_reg = get_sales_outstanding_register(broker=broker_id)
    assert out_reg["summary"]["total_vouchers"] >= 1, "Should have sales vouchers"
    assert out_reg["summary"]["total_brokerage_outstanding"] >= 1250.0, "Should have pending brokerage due"
    print(f"  [PASS] Sales Outstanding Register: {out_reg['summary']['pending_vouchers']} pending vouchers, ₹{out_reg['summary']['total_brokerage_outstanding']} brokerage due across {out_reg['summary']['total_brokers']} brokers")

    # Settle the sales entry
    settle_res = settle_sales_entry(voucher_id=s_entry["name"], mark_full=1, remarks="Test Full Settlement")
    assert settle_res["settlement_status"] == "Settled"
    assert settle_res["outstanding_brokerage"] == 0.0
    print(f"  [PASS] Successfully settled {s_entry['name']}: Status = {settle_res['settlement_status']}, Outstandings = ₹{settle_res['outstanding_brokerage']}")

    # 12. Test Stock Group & Item Master with GST
    print("\n--- Test 10: Stock Group DocType & Item Master with GST ---")
    from brokerage_module.brokerage_module.api import (
        save_stock_group,
        get_stock_groups,
        save_item,
        get_items
    )

    sg_res = save_stock_group({
        "stock_group_name": "Jaggery & Sweeteners",
        "default_gst_rate": 5.0,
        "is_active": 1,
        "description": "Natural jaggery, jaggery powder, and related organic sweeteners"
    })
    sg_name = sg_res["name"]
    assert sg_res["default_gst_rate"] == 5.0, "Expected default GST 5.0%"
    print(f"  [PASS] Stock Group created: {sg_name} with 5% default GST")

    # Create Item assigned to this Stock Group
    item_payload = {
        "item_code": "JAGGERY-ORGANIC-50KG",
        "item_name": "Organic Kolhapur Jaggery 50KG",
        "stock_group": sg_name,
        "stock_uom": "Bag",
        "gst_rate": 5.0,
        "standard_rate": 4200.0,
        "description": "Kolhapur premium organic jaggery blocks"
    }
    item_res = save_item(item_payload)
    test_item_code = item_res["item_code"]
    assert item_res["stock_group"] == sg_name, f"Expected {sg_name}, got {item_res['stock_group']}"
    assert item_res["gst_rate"] == 5.0, f"Expected GST 5.0, got {item_res['gst_rate']}"
    print(f"  [PASS] Item created: {test_item_code} mapped to Stock Group '{sg_name}' with 5.0% GST")

    # 13. Test Broker Rate Configuration by Stock Group & GST calculations in Voucher Entries
    print("\n--- Test 11: Stock Group Brokerage Inheritance & Intra-state GST (CGST/SGST) ---")
    # Create a broker whose brokerage rules are defined by Stock Group
    sg_broker_payload = {
        "broker_name": "Kolhapur Jaggery Commission Agent",
        "mobile_no": "9988776655",
        "city": "Kolhapur",
        "state": "Maharashtra",
        "status": "Active",
        "applicable_for_purchase": 1,
        "applicable_for_sales": 1,
        "purchase_brokerage_rules": [
            {
                "stock_group": sg_name,
                "brokerage_method": "Per Bag",
                "percentage": 0,
                "per_bag": 18.0,
                "per_quintal": 0,
                "remarks": "₹18/bag for Jaggery & Sweeteners purchase"
            }
        ],
        "sales_brokerage_rules": [
            {
                "stock_group": sg_name,
                "brokerage_method": "Per Quintal",
                "percentage": 0,
                "per_bag": 0,
                "per_quintal": 30.0,
                "remarks": "₹30/qtl for Jaggery & Sweeteners sale"
            }
        ]
    }
    sg_broker = save_broker(sg_broker_payload)
    sg_broker_id = sg_broker["name"]
    print(f"  [PASS] Broker created: {sg_broker_id} with rates configured on Stock Group '{sg_name}'")

    # Test automatic inheritance in Purchase by selecting item (without manually selecting stock group)
    sg_lookup_p = get_broker_item_rate(broker=sg_broker_id, item=test_item_code, entry_type="Purchase")
    assert sg_lookup_p["found"] is True, "Must find brokerage rate via item's stock group"
    assert sg_lookup_p["stock_group"] == sg_name, f"Expected {sg_name}, got {sg_lookup_p['stock_group']}"
    assert sg_lookup_p["brokerage_method"] == "Per Bag", f"Expected Per Bag, got {sg_lookup_p['brokerage_method']}"
    assert sg_lookup_p["rate"] == 18.0, f"Expected 18.0/bag, got {sg_lookup_p['rate']}"
    assert sg_lookup_p["gst_rate"] == 5.0, f"Expected 5.0% GST, got {sg_lookup_p['gst_rate']}"
    assert sg_lookup_p["cgst_rate"] == 2.5, f"Expected 2.5% CGST, got {sg_lookup_p['cgst_rate']}"
    assert sg_lookup_p["sgst_rate"] == 2.5, f"Expected 2.5% SGST, got {sg_lookup_p['sgst_rate']}"
    print(f"  [PASS] Purchase rate auto-inherited by Item Stock Group: {sg_lookup_p['brokerage_method']} @ ₹{sg_lookup_p['rate']}/bag | GST: {sg_lookup_p['gst_rate']}% (CGST {sg_lookup_p['cgst_rate']}% + SGST {sg_lookup_p['sgst_rate']}%)")

    # Submit Purchase Entry with GST
    # 50 bags @ ₹4200 = ₹2,10,000 Trade. GST 5% = ₹10,500 (CGST ₹5,250 + SGST ₹5,250). Grand Total = ₹2,20,500. Brokerage = 50 * 18 = ₹900.
    trade_amt_p = 50 * 4200.0
    gst_amt_p = trade_amt_p * 0.05
    cgst_amt_p = gst_amt_p / 2.0
    sgst_amt_p = gst_amt_p / 2.0
    grand_tot_p = trade_amt_p + gst_amt_p

    sg_p_entry = save_purchase_entry({
        "posting_date": nowdate(),
        "company": company,
        "broker": sg_broker_id,
        "item": test_item_code,
        "stock_group": sg_name,
        "quantity": 50,
        "bags": 50,
        "rate": 4200.0,
        "brokerage_method": sg_lookup_p["brokerage_method"],
        "brokerage_rate": sg_lookup_p["rate"],
        "per_bag": sg_lookup_p["per_bag"],
        "rate_source": sg_lookup_p["source"],
        "gst_rate": 5.0,
        "cgst_rate": 2.5,
        "cgst_amount": cgst_amt_p,
        "sgst_rate": 2.5,
        "sgst_amount": sgst_amt_p,
        "total_gst_amount": gst_amt_p,
        "grand_total": grand_tot_p,
        "submit": True
    })
    assert sg_p_entry["trade_amount"] == 210000.0, f"Expected 210000, got {sg_p_entry['trade_amount']}"
    assert sg_p_entry["total_gst_amount"] == 10500.0, f"Expected 10500 GST, got {sg_p_entry['total_gst_amount']}"
    assert sg_p_entry["cgst_amount"] == 5250.0, f"Expected 5250 CGST, got {sg_p_entry['cgst_amount']}"
    assert sg_p_entry["sgst_amount"] == 5250.0, f"Expected 5250 SGST, got {sg_p_entry['sgst_amount']}"
    assert sg_p_entry["grand_total"] == 220500.0, f"Expected 220500 Grand Total, got {sg_p_entry['grand_total']}"
    assert sg_p_entry["brokerage_amount"] == 900.0, f"Expected 900 Brokerage, got {sg_p_entry['brokerage_amount']}"
    print(f"  [PASS] Purchase Entry {sg_p_entry['name']}: Trade ₹{sg_p_entry['trade_amount']} + CGST ₹{sg_p_entry['cgst_amount']} + SGST ₹{sg_p_entry['sgst_amount']} = Grand Total ₹{sg_p_entry['grand_total']} | Brokerage ₹{sg_p_entry['brokerage_amount']}")

    # Test automatic inheritance in Sales by selecting item
    sg_lookup_s = get_broker_item_rate(broker=sg_broker_id, item=test_item_code, entry_type="Sell")
    assert sg_lookup_s["found"] is True, "Must find brokerage rate via item's stock group"
    assert sg_lookup_s["brokerage_method"] == "Per Quintal", f"Expected Per Quintal, got {sg_lookup_s['brokerage_method']}"
    assert sg_lookup_s["rate"] == 30.0, f"Expected 30.0/qtl, got {sg_lookup_s['rate']}"

    # Submit Sales Entry with GST
    # 40 Qtl @ ₹4500 = ₹1,80,000 Trade. GST 5% = ₹9,000 (CGST ₹4,500 + SGST ₹4,500). Grand Total = ₹1,89,000. Brokerage = 40 * 30 = ₹1,200.
    trade_amt_s = 40 * 4500.0
    gst_amt_s = trade_amt_s * 0.05
    cgst_amt_s = gst_amt_s / 2.0
    sgst_amt_s = gst_amt_s / 2.0
    grand_tot_s = trade_amt_s + gst_amt_s

    sg_s_entry = save_sales_entry({
        "posting_date": nowdate(),
        "company": company,
        "broker": sg_broker_id,
        "item": test_item_code,
        "stock_group": sg_name,
        "quantity": 40,
        "bags": 80,
        "rate": 4500.0,
        "brokerage_method": sg_lookup_s["brokerage_method"],
        "brokerage_rate": sg_lookup_s["rate"],
        "per_quintal": sg_lookup_s["per_quintal"],
        "rate_source": sg_lookup_s["source"],
        "gst_rate": 5.0,
        "cgst_rate": 2.5,
        "cgst_amount": cgst_amt_s,
        "sgst_rate": 2.5,
        "sgst_amount": sgst_amt_s,
        "total_gst_amount": gst_amt_s,
        "grand_total": grand_tot_s,
        "submit": True
    })
    assert sg_s_entry["trade_amount"] == 180000.0, f"Expected 180000, got {sg_s_entry['trade_amount']}"
    assert sg_s_entry["total_gst_amount"] == 9000.0, f"Expected 9000 GST, got {sg_s_entry['total_gst_amount']}"
    assert sg_s_entry["cgst_amount"] == 4500.0, f"Expected 4500 CGST, got {sg_s_entry['cgst_amount']}"
    assert sg_s_entry["sgst_amount"] == 4500.0, f"Expected 4500 SGST, got {sg_s_entry['sgst_amount']}"
    assert sg_s_entry["grand_total"] == 189000.0, f"Expected 189000 Grand Total, got {sg_s_entry['grand_total']}"
    assert sg_s_entry["brokerage_amount"] == 1200.0, f"Expected 1200 Brokerage, got {sg_s_entry['brokerage_amount']}"
    print(f"  [PASS] Sales Entry {sg_s_entry['name']}: Trade ₹{sg_s_entry['trade_amount']} + CGST ₹{sg_s_entry['cgst_amount']} + SGST ₹{sg_s_entry['sgst_amount']} = Grand Total ₹{sg_s_entry['grand_total']} | Brokerage ₹{sg_s_entry['brokerage_amount']}")

    print("\n==================================================")
    print("ALL 11 BROKERAGE MODULE BACKEND TESTS PASSED (100%)")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
