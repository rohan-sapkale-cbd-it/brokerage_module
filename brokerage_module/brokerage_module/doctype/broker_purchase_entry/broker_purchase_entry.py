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
        # Multi-Item Calculation if child items table is populated
        if hasattr(self, "items") and self.items and len(self.items) > 0:
            tot_qty = 0.0
            tot_bags = 0.0
            tot_trade = 0.0
            tot_cgst = 0.0
            tot_sgst = 0.0
            tot_gst = 0.0
            tot_grand = 0.0
            tot_brk = 0.0

            for row in self.items:
                qty = flt(row.quantity)
                rate = flt(row.rate)
                row.trade_amount = round(qty * rate, 2)

                if not row.stock_group and row.item:
                    row.stock_group = frappe.db.get_value("Item", row.item, "stock_group") or "Sugar"
                if not row.item_name and row.item:
                    row.item_name = frappe.db.get_value("Item", row.item, "item_name") or row.item

                # GST Calculations (CGST + SGST)
                if row.gst_rate is None or str(row.gst_rate).strip() == "":
                    item_gst = frappe.db.get_value("Item", row.item, "gst_rate") if row.item else None
                    row.gst_rate = flt(item_gst) if item_gst is not None else 5.0
                else:
                    row.gst_rate = flt(row.gst_rate)

                half_pct = round(row.gst_rate / 2.0, 4)
                row.cgst_rate = half_pct
                row.sgst_rate = half_pct
                row.cgst_amount = round(row.trade_amount * (half_pct / 100.0), 2)
                row.sgst_amount = round(row.trade_amount * (half_pct / 100.0), 2)
                row.total_gst_amount = round(row.cgst_amount + row.sgst_amount, 2)
                row.grand_total = round(row.trade_amount + row.total_gst_amount, 2)

                # Brokerage Calculation
                method = row.brokerage_method or "Percentage"
                if method == "Percentage":
                    pct = flt(row.percentage if row.percentage is not None and str(row.percentage).strip() != "" else row.brokerage_rate)
                    row.percentage = pct
                    row.per_bag = 0
                    row.per_quintal = 0
                    row.brokerage_amount = round(row.trade_amount * (pct / 100.0), 2)
                elif method == "Per Bag":
                    bags_count = flt(row.bags if row.bags is not None and str(row.bags).strip() != "" else qty * 2.0)
                    row.bags = bags_count
                    bag_rate = flt(row.per_bag if row.per_bag is not None and str(row.per_bag).strip() != "" else row.brokerage_rate)
                    row.per_bag = bag_rate
                    row.percentage = 0
                    row.per_quintal = 0
                    row.brokerage_amount = round(bags_count * bag_rate, 2)
                elif method == "Per Quintal":
                    qtl_rate = flt(row.per_quintal if row.per_quintal is not None and str(row.per_quintal).strip() != "" else row.brokerage_rate)
                    row.per_quintal = qtl_rate
                    row.percentage = 0
                    row.per_bag = 0
                    row.brokerage_amount = round(qty * qtl_rate, 2)

                tot_qty += qty
                tot_bags += flt(row.bags)
                tot_trade += row.trade_amount
                tot_cgst += row.cgst_amount
                tot_sgst += row.sgst_amount
                tot_gst += row.total_gst_amount
                tot_grand += row.grand_total
                tot_brk += row.brokerage_amount

            self.quantity = round(tot_qty, 2)
            self.bags = round(tot_bags, 2)
            self.trade_amount = round(tot_trade, 2)
            self.cgst_amount = round(tot_cgst, 2)
            self.sgst_amount = round(tot_sgst, 2)
            self.total_gst_amount = round(tot_gst, 2)
            self.grand_total = round(tot_grand, 2)
            self.brokerage_amount = round(tot_brk, 2)

            first_row = self.items[0]
            self.item = first_row.item
            if len(self.items) == 1:
                self.item_name = first_row.item_name or first_row.item
                self.rate = first_row.rate
                self.brokerage_method = first_row.brokerage_method
                self.brokerage_rate = first_row.brokerage_rate
                self.stock_group = first_row.stock_group
                self.gst_rate = first_row.gst_rate
            else:
                self.item_name = f"{first_row.item_name or first_row.item} (+{len(self.items)-1} more)"
                self.rate = round(tot_trade / tot_qty, 2) if tot_qty else 0
                self.brokerage_method = first_row.brokerage_method or "Percentage"
                self.stock_group = first_row.stock_group
                self.gst_rate = first_row.gst_rate

        else:
            # Single item direct calculation
            qty = flt(self.quantity)
            rate = flt(self.rate)
            self.trade_amount = round(qty * rate, 2)

            if not self.stock_group and self.item:
                self.stock_group = frappe.db.get_value("Item", self.item, "stock_group") or "Sugar"
            if not self.item_name and self.item:
                self.item_name = frappe.db.get_value("Item", self.item, "item_name") or self.item

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

            # If items table exists on doc but is empty, sync single item row
            if hasattr(self, "items") and (self.items is None or len(self.items) == 0) and self.item:
                self.append("items", {
                    "item": self.item,
                    "item_name": self.item_name,
                    "stock_group": self.stock_group,
                    "quantity": self.quantity,
                    "bags": self.bags,
                    "rate": self.rate,
                    "trade_amount": self.trade_amount,
                    "gst_rate": self.gst_rate,
                    "cgst_rate": self.cgst_rate,
                    "cgst_amount": self.cgst_amount,
                    "sgst_rate": self.sgst_rate,
                    "sgst_amount": self.sgst_amount,
                    "total_gst_amount": self.total_gst_amount,
                    "grand_total": self.grand_total,
                    "brokerage_method": self.brokerage_method,
                    "brokerage_rate": self.brokerage_rate,
                    "percentage": self.percentage,
                    "per_bag": self.per_bag,
                    "per_quintal": self.per_quintal,
                    "brokerage_amount": self.brokerage_amount,
                    "rate_source": getattr(self, "rate_source", None),
                    "remarks": getattr(self, "remarks", None)
                })

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"
