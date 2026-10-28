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


def run_tests():
    print("==================================================")
    print("STARTING BROKERAGE MODULE INTEGRATION TESTS")
    print("==================================================")

    # 1. Get or create test items
    items = frappe.get_all("Item", limit=2, pluck="name")
    if not items:
        item_doc = frappe.new_doc("Item")
        item_doc.item_code = "TEST-COMMODITY-A"
        item_doc.item_name = "Test Sugar Commodity A"
        item_doc.item_group = "All Item Groups"
        item_doc.stock_uom = "Quintal"
        item_doc.insert()
        items = [item_doc.name]

    item_a = items[0]
    item_b = items[1] if len(items) > 1 else items[0]
    print(f"[OK] Using Items: {item_a}, {item_b}")

    # 2. Get or create test supplier and customer
    supplier = frappe.get_all("Supplier", limit=1, pluck="name")
    if not supplier:
        sup_doc = frappe.new_doc("Supplier")
        sup_doc.supplier_name = "Test Agro Supplier"
        sup_doc.insert()
        supplier = [sup_doc.name]
    supplier_name = supplier[0]

    customer = frappe.get_all("Customer", limit=1, pluck="name")
    if not customer:
        cust_doc = frappe.new_doc("Customer")
        cust_doc.customer_name = "Test Retail Customer"
        cust_doc.insert()
        customer = [cust_doc.name]
    customer_name = customer[0]

    company = frappe.get_all("Company", limit=1, pluck="name")[0]

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
        "supplier": supplier_name,
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
        "customer": customer_name,
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

    print("\n==================================================")
    print("ALL 8 BROKERAGE MODULE BACKEND TESTS PASSED (100%)")
    print("==================================================")


if __name__ == "__main__":
    run_tests()

