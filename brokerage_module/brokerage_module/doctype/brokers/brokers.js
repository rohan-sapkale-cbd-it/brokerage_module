// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.ui.form.on("Brokers", {
    refresh: function(frm) {
        frm.trigger("toggle_role_sections");
    },
    applicable_for_purchase: function(frm) {
        frm.trigger("toggle_role_sections");
    },
    applicable_for_sales: function(frm) {
        frm.trigger("toggle_role_sections");
    },
    toggle_role_sections: function(frm) {
        frm.toggle_display("section_purchase_rules", !!frm.doc.applicable_for_purchase);
        frm.toggle_display("section_sales_rules", !!frm.doc.applicable_for_sales);
    }
});

function setup_rule_events(doctype_name) {
    frappe.ui.form.on(doctype_name, {
        percentage: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.percentage && row.percentage > 0) {
                frappe.model.set_value(cdt, cdn, "per_bag", 0);
                frappe.model.set_value(cdt, cdn, "per_quintal", 0);
                frappe.model.set_value(cdt, cdn, "brokerage_method", "Percentage");
            }
        },
        per_bag: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.per_bag && row.per_bag > 0) {
                frappe.model.set_value(cdt, cdn, "percentage", 0);
                frappe.model.set_value(cdt, cdn, "per_quintal", 0);
                frappe.model.set_value(cdt, cdn, "brokerage_method", "Per Bag");
            }
        },
        per_quintal: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.per_quintal && row.per_quintal > 0) {
                frappe.model.set_value(cdt, cdn, "percentage", 0);
                frappe.model.set_value(cdt, cdn, "per_bag", 0);
                frappe.model.set_value(cdt, cdn, "brokerage_method", "Per Quintal");
            }
        }
    });
}

setup_rule_events("Broker Rate Item");

