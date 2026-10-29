# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


class BrokerSalesEntry(Document):
    def validate(self):
        self.validate_broker_eligibility()
        self.calculate_totals()

    def validate_broker_eligibility(self):
        if not self.broker:
            frappe.throw(_("Please select a Broker."))
        is_sales = frappe.db.get_value("Brokers", self.broker, "applicable_for_sales")
        if is_sales is None:
            is_sales = frappe.db.get_value("Broker", self.broker, "applicable_for_sales")
        if not is_sales:
            frappe.throw(
                _("Broker {0} is not marked as Applicable for Sell.").format(self.broker_name or self.broker)
            )

    def calculate_totals(self):
        qty = flt(self.quantity)
        rate = flt(self.rate)
        self.trade_amount = round(qty * rate, 2)

        # Fetch Stock Group if missing
        if not self.stock_group and self.item:
            self.stock_group = frappe.db.get_value("Item", self.item, "stock_group")

        # GST Calculations (CGST + SGST)
        if self.gst_rate is None or str(self.gst_rate).strip() == "":
            item_gst = frappe.db.get_value("Item", self.item, "gst_rate") if self.item else None
            self.gst_rate = flt(item_gst) if item_gst is not None else 5.0
        else:
            self.gst_rate = flt(self.gst_rate)

        half_pct = round(self.gst_rate / 2.0, 4)
        self.cgst_rate = half_pct
        self.sgst_rate = half_pct
        self.cgst_amount = round(self.trade_amount * (half_pct / 100.0), 2)
        self.sgst_amount = round(self.trade_amount * (half_pct / 100.0), 2)
        self.total_gst_amount = round(self.cgst_amount + self.sgst_amount, 2)
        self.grand_total = round(self.trade_amount + self.total_gst_amount, 2)

        # Brokerage Calculation
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

        # Settlement & Outstanding tracking (based on grand_total or trade_amount)
        base_trade_total = flt(self.grand_total if self.grand_total > 0 else self.trade_amount)
        settled_amt = flt(self.settled_amount or 0)
        self.outstanding_amount = max(0.0, round(base_trade_total - settled_amt, 2))
        settled_brk = flt(self.settled_brokerage or 0)
        self.outstanding_brokerage = max(0.0, round(self.brokerage_amount - settled_brk, 2))

        if self.outstanding_brokerage <= 0 and (settled_brk > 0 or (settled_amt >= base_trade_total and base_trade_total > 0)):
            self.settlement_status = "Settled"
        elif settled_brk > 0 or settled_amt > 0:
            self.settlement_status = "Partially Settled"
        else:
            self.settlement_status = getattr(self, "settlement_status", None) or "Pending"

    def on_submit(self):
        self.db_set("status", "Submitted")

    def on_cancel(self):
        self.db_set("status", "Cancelled")
