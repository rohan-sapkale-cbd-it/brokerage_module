# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class Brokers(Document):
    def validate(self):
        self.validate_checkpoints()
        self.validate_mutual_exclusivity()

    def validate_checkpoints(self):
        """Ensure at least one role checkpoint is active."""
        if not self.applicable_for_purchase and not self.applicable_for_sales:
            frappe.throw(_("Broker '{0}' must have at least one checkpoint active: Applicable for Purchase or Applicable for Sell.").format(self.broker_name))

    def validate_mutual_exclusivity(self):
        """Enforce mutual exclusivity among the 3 methods in each row:
        - Percentage
        - Per Bag
        - Per Quintal
        Only ONE method can have a non-zero value per row.
        """
        for table_field in ["purchase_brokerage_rules", "sales_brokerage_rules"]:
            table_label = "Purchase Rules" if table_field == "purchase_brokerage_rules" else "Sell Rules"
            rows = self.get(table_field) or []
            seen_items = set()

            for row in rows:
                if not row.item:
                    continue

                if row.item in seen_items:
                    frappe.throw(_("In {0}, item '{1}' appears multiple times. Each item must have only one rule row.").format(table_label, row.item))
                seen_items.add(row.item)

                active_methods = []
                if row.percentage and float(row.percentage) > 0:
                    active_methods.append(("Percentage", float(row.percentage)))
                if row.per_bag and float(row.per_bag) > 0:
                    active_methods.append(("Per Bag", float(row.per_bag)))
                if row.per_quintal and float(row.per_quintal) > 0:
                    active_methods.append(("Per Quintal", float(row.per_quintal)))

                if len(active_methods) > 1:
                    methods_str = ", ".join([f"{m[0]}: {m[1]}" for m in active_methods])
                    frappe.throw(
                        _("Row #{0} for item '{1}' has multiple active methods ({2}). Only ONE method (Percentage, Per Bag, or Per Quintal) is allowed per item.").format(
                            row.idx, row.item, methods_str
                        )
                    )

                if active_methods:
                    row.brokerage_method = active_methods[0][0]
                    if row.brokerage_method == "Percentage":
                        row.per_bag = 0
                        row.per_quintal = 0
                    elif row.brokerage_method == "Per Bag":
                        row.percentage = 0
                        row.per_quintal = 0
                    elif row.brokerage_method == "Per Quintal":
                        row.percentage = 0
                        row.per_bag = 0

