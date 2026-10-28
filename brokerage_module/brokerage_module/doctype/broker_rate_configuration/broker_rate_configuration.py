# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


class BrokerRateConfiguration(Document):
    def validate(self):
        self.sync_broker_flags()
        self.validate_rate_rows("purchase_brokerage_rules", "Purchase")
        self.validate_rate_rows("sales_brokerage_rules", "Sell")

    def sync_broker_flags(self):
        if self.broker:
            flags = frappe.db.get_value(
                "Broker",
                self.broker,
                ["applicable_for_purchase", "applicable_for_sales", "broker_name"],
                as_dict=True,
            )
            if flags:
                self.applicable_for_purchase = flags.get("applicable_for_purchase") or 0
                self.applicable_for_sales = flags.get("applicable_for_sales") or 0
                self.broker_name = flags.get("broker_name") or self.broker

    def validate_rate_rows(self, table_fieldname, rule_type):
        rows = self.get(table_fieldname) or []
        for row in rows:
            method = row.brokerage_method or "Percentage"
            if method == "Percentage":
                row.per_bag = 0
                row.per_quintal = 0
                if flt(row.percentage) <= 0:
                    frappe.throw(
                        _("{0} Rules Row #{1}: Please specify a valid Percentage for item {2}.").format(
                            rule_type, row.idx, row.item
                        )
                    )
            elif method == "Per Bag":
                row.percentage = 0
                row.per_quintal = 0
                if flt(row.per_bag) <= 0:
                    frappe.throw(
                        _("{0} Rules Row #{1}: Please specify a valid Rate Per Bag for item {2}.").format(
                            rule_type, row.idx, row.item
                        )
                    )
            elif method == "Per Quintal":
                row.percentage = 0
                row.per_bag = 0
                if flt(row.per_quintal) <= 0:
                    frappe.throw(
                        _("{0} Rules Row #{1}: Please specify a valid Rate Per Quintal for item {2}.").format(
                            rule_type, row.idx, row.item
                        )
                    )

