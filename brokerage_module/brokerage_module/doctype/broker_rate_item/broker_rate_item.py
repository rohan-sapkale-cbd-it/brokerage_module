# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


class BrokerRateItem(Document):
    def validate(self):
        # Enforce that only the selected method's value is kept, others zeroed out
        method = self.brokerage_method or "Percentage"
        if method == "Percentage":
            self.per_bag = 0
            self.per_quintal = 0
            if flt(self.percentage) < 0:
                self.percentage = 0
        elif method == "Per Bag":
            self.percentage = 0
            self.per_quintal = 0
            if flt(self.per_bag) < 0:
                self.per_bag = 0
        elif method == "Per Quintal":
            self.percentage = 0
            self.per_bag = 0
            if flt(self.per_quintal) < 0:
                self.per_quintal = 0
