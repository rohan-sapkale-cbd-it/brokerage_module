// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.ui.form.on("Broker Purchase Entry", {
    setup: function(frm) {
        frm.set_query("broker", function() {
            return {
                filters: {
                    applicable_for_purchase: 1,
                    status: "Active"
                }
            };
        });
    },

    broker: function(frm) {
        frm.trigger("fetch_brokerage_rule");
    },

    item: function(frm) {
        frm.trigger("fetch_brokerage_rule");
    },

    quantity: function(frm) {
        frm.trigger("recalc");
    },

    bags: function(frm) {
        frm.trigger("recalc");
    },

    rate: function(frm) {
        frm.trigger("recalc");
    },

    brokerage_method: function(frm) {
        frm.trigger("recalc");
    },

    brokerage_rate: function(frm) {
        if (frm.doc.brokerage_method === "Percentage") {
            frm.set_value("percentage", frm.doc.brokerage_rate);
        } else if (frm.doc.brokerage_method === "Per Bag") {
            frm.set_value("per_bag", frm.doc.brokerage_rate);
        } else if (frm.doc.brokerage_method === "Per Quintal") {
            frm.set_value("per_quintal", frm.doc.brokerage_rate);
        }
        frm.trigger("recalc");
    },

    percentage: function(frm) {
        if (flt(frm.doc.percentage) > 0) {
            frm.set_value("brokerage_method", "Percentage");
            frm.set_value("per_bag", 0);
            frm.set_value("per_quintal", 0);
            frm.set_value("brokerage_rate", frm.doc.percentage);
        }
        frm.trigger("recalc");
    },

    per_bag: function(frm) {
        if (flt(frm.doc.per_bag) > 0) {
            frm.set_value("brokerage_method", "Per Bag");
            frm.set_value("percentage", 0);
            frm.set_value("per_quintal", 0);
            frm.set_value("brokerage_rate", frm.doc.per_bag);
        }
        frm.trigger("recalc");
    },

    per_quintal: function(frm) {
        if (flt(frm.doc.per_quintal) > 0) {
            frm.set_value("brokerage_method", "Per Quintal");
            frm.set_value("percentage", 0);
            frm.set_value("per_bag", 0);
            frm.set_value("brokerage_rate", frm.doc.per_quintal);
        }
        frm.trigger("recalc");
    },

    fetch_brokerage_rule: function(frm) {
        if (!frm.doc.broker || !frm.doc.item) return;

        frappe.call({
            method: "brokerage_module.brokerage_module.api.get_broker_item_rate",
            args: {
                broker: frm.doc.broker,
                item: frm.doc.item,
                entry_type: "Purchase",
                posting_date: frm.doc.posting_date || frappe.datetime.nowdate()
            },
            callback: function(r) {
                if (r.message && r.message.found) {
                    let rule = r.message;
                    frm.set_value("brokerage_method", rule.brokerage_method);
                    frm.set_value("brokerage_rate", rule.rate);
                    frm.set_value("percentage", rule.percentage || 0);
                    frm.set_value("per_bag", rule.per_bag || 0);
                    frm.set_value("per_quintal", rule.per_quintal || 0);
                    frm.set_value("rate_source", rule.source || "Broker Rule");
                    frappe.show_alert({
                        message: __("Applied Brokerage Rule: {0} @ {1}", [rule.brokerage_method, rule.rate]),
                        indicator: "green"
                    });
                    frm.trigger("recalc");
                }
            }
        });
    },

    recalc: function(frm) {
        let qty = flt(frm.doc.quantity);
        let rate = flt(frm.doc.rate);
        let trade_amount = Math.round(qty * rate * 100) / 100;
        frm.set_value("trade_amount", trade_amount);

        let method = frm.doc.brokerage_method || "Percentage";
        let brk_amt = 0;

        if (method === "Percentage") {
            let pct = flt(frm.doc.percentage || frm.doc.brokerage_rate);
            brk_amt = Math.round((trade_amount * pct / 100) * 100) / 100;
        } else if (method === "Per Bag") {
            let bags = flt(frm.doc.bags || (qty * 2));
            let per_bag = flt(frm.doc.per_bag || frm.doc.brokerage_rate);
            brk_amt = Math.round((bags * per_bag) * 100) / 100;
        } else if (method === "Per Quintal") {
            let per_qtl = flt(frm.doc.per_quintal || frm.doc.brokerage_rate);
            brk_amt = Math.round((qty * per_qtl) * 100) / 100;
        }

        frm.set_value("brokerage_amount", brk_amt);
    }
});
