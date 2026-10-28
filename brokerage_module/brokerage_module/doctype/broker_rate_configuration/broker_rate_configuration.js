// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.ui.form.on("Broker Rate Configuration", {
    broker: function(frm) {
        if (!frm.doc.broker) return;
        frappe.db.get_value("Brokers", frm.doc.broker, ["applicable_for_purchase", "applicable_for_sales", "broker_name"], (r) => {
            if (r) {
                frm.set_value("applicable_for_purchase", r.applicable_for_purchase || 0);
                frm.set_value("applicable_for_sales", r.applicable_for_sales || 0);
                frm.set_value("broker_name", r.broker_name || frm.doc.broker);
            }
        });
    }
});

frappe.ui.form.on("Broker Rate Item", {
    brokerage_method: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.brokerage_method === "Percentage") {
            frappe.model.set_value(cdt, cdn, "per_bag", 0);
            frappe.model.set_value(cdt, cdn, "per_quintal", 0);
        } else if (row.brokerage_method === "Per Bag") {
            frappe.model.set_value(cdt, cdn, "percentage", 0);
            frappe.model.set_value(cdt, cdn, "per_quintal", 0);
        } else if (row.brokerage_method === "Per Quintal") {
            frappe.model.set_value(cdt, cdn, "percentage", 0);
            frappe.model.set_value(cdt, cdn, "per_bag", 0);
        }
    },
    per_bag: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (flt(row.per_bag) > 0) {
            frappe.model.set_value(cdt, cdn, "brokerage_method", "Per Bag");
            frappe.model.set_value(cdt, cdn, "percentage", 0);
            frappe.model.set_value(cdt, cdn, "per_quintal", 0);
        }
    },
    per_quintal: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (flt(row.per_quintal) > 0) {
            frappe.model.set_value(cdt, cdn, "brokerage_method", "Per Quintal");
            frappe.model.set_value(cdt, cdn, "percentage", 0);
            frappe.model.set_value(cdt, cdn, "per_bag", 0);
        }
    },
    percentage: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (flt(row.percentage) > 0) {
            frappe.model.set_value(cdt, cdn, "brokerage_method", "Percentage");
            frappe.model.set_value(cdt, cdn, "per_bag", 0);
            frappe.model.set_value(cdt, cdn, "per_quintal", 0);
        }
    }
});

