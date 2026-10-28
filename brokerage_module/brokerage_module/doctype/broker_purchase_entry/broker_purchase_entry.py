# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


class BrokerPurchaseEntry(Document):
    def validate(self):
        self.validate_broker_eligibility()
        self.calculate_totals()

    def validate_broker_eligibility(self):
        if not self.broker:
            frappe.throw(_("Please select a Broker."))
        is_purchase = frappe.db.get_value("Brokers", self.broker, "applicable_for_purchase")
        if is_purchase is None:
            is_purchase = frappe.db.get_value("Broker", self.broker, "applicable_for_purchase")
        if not is_purchase:
            frappe.throw(
                _("Broker {0} is not marked as Applicable for Purchase.").format(self.broker_name or self.broker)
            )

    def calculate_totals(self):
        qty = flt(self.quantity)
        rate = flt(self.rate)
        self.trade_amount = round(qty * rate, 2)

        method = self.brokerage_method or "Percentage"
        if method == "Percentage":
            pct = flt(self.percentage if self.percentage is not None and str(self.percentage).strip() != "" else self.brokerage_rate)
            self.percentage = pct
            self.per_bag = 0
            self.per_quintal = 0
            self.brokerage_amount = round(self.trade_amount * (pct / 100.0), 2)
        elif method == "Per Bag":
            bags_count = flt(self.bags if self.bags is not None and str(self.bags).strip() != "" else qty * 2.0)
            bag_rate = flt(self.per_bag if self.per_bag is not None and str(self.per_bag).strip() != "" else self.brokerage_rate)
            self.per_bag = bag_rate
            self.percentage = 0
            self.per_quintal = 0
            self.brokerage_amount = round(bags_count * bag_rate, 2)
        elif method == "Per Quintal":
            qtl_rate = flt(self.per_quintal if self.per_quintal is not None and str(self.per_quintal).strip() != "" else self.brokerage_rate)
            self.per_quintal = qtl_rate
            self.percentage = 0
            self.per_bag = 0
            self.brokerage_amount = round(qty * qtl_rate, 2)

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

