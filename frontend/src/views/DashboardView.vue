<template>
  <div>
    <!-- Welcome Header -->
    <div style="background: linear-gradient(135deg, #1e3a8a, #0f172a); color: #fff; border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; box-shadow: var(--shadow-md);">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
          <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #93c5fd; font-weight: 700;">
            Commodity Brokerage Platform
          </div>
          <h1 style="font-size: 26px; font-weight: 800; margin-top: 4px; letter-spacing: -0.02em;">
            Welcome to Brokerage Desk
          </h1>
          <p style="font-size: 14px; color: #cbd5e1; margin-top: 6px; max-width: 720px;">
            Shop purchase &amp; sell management with automated broker commissions. Supports Purchase/Sell checkpoints, 3 calculation methods (Per Bag, Per Quintal, Percentage), and date-effective rate cards.
          </p>
        </div>

        <div style="display: flex; gap: 10px;">
          <router-link to="/purchase" class="btn btn-primary" style="background: #2563eb; border: 1px solid #60a5fa;">
            🛒 Purchase Entry (<kbd style="background: rgba(255,255,255,0.2); color: #fff; border: none;">F9</kbd>)
          </router-link>
          <router-link to="/sell" class="btn btn-success" style="background: #059669; border: 1px solid #34d399;">
            🏷️ Sell Entry (<kbd style="background: rgba(255,255,255,0.2); color: #fff; border: none;">F8</kbd>)
          </router-link>
        </div>
      </div>
    </div>

    <!-- KPI Cards Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 28px;">
      <!-- Active Brokers -->
      <div class="content-card" style="margin-bottom: 0; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">Active Brokers</div>
          <span style="font-size: 20px;">👥</span>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 8px;">
          {{ stats.brokers.total }}
        </div>
        <div style="display: flex; gap: 8px; margin-top: 8px;">
          <span class="badge badge-blue">🛒 {{ stats.brokers.purchase }} Purchase</span>
          <span class="badge badge-green">🏷️ {{ stats.brokers.sales }} Sell</span>
        </div>
      </div>

      <!-- Purchase Volume -->
      <div class="content-card" style="margin-bottom: 0; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 12px; font-weight: 700; color: #1e40af; text-transform: uppercase;">Purchase Trade Volume</div>
          <span style="font-size: 20px;">🛒</span>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #1e3a8a; margin-top: 8px;">
          ₹ {{ formatCurrency(stats.purchase.total_trade) }}
        </div>
        <div style="font-size: 12.5px; color: #059669; font-weight: 600; margin-top: 8px;">
          Commission: ₹{{ formatCurrency(stats.purchase.total_brokerage) }} ({{ stats.purchase.count }} vouchers)
        </div>
      </div>

      <!-- Sales Volume -->
      <div class="content-card" style="margin-bottom: 0; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 12px; font-weight: 700; color: #065f46; text-transform: uppercase;">Sales Trade Volume</div>
          <span style="font-size: 20px;">🏷️</span>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #065f46; margin-top: 8px;">
          ₹ {{ formatCurrency(stats.sales.total_trade) }}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
          <span style="font-size: 12.5px; color: #059669; font-weight: 600;">
            Commission: ₹{{ formatCurrency(stats.sales.total_brokerage) }} ({{ stats.sales.count }} vouchers)
          </span>
        </div>
      </div>

      <!-- Total Brokerage Combined -->
      <div class="content-card" style="margin-bottom: 0; padding: 20px; background: #ecfdf5; border-color: #a7f3d0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 12px; font-weight: 700; color: #065f46; text-transform: uppercase;">Total Brokerage Counted</div>
          <span style="font-size: 20px;">💰</span>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #047857; margin-top: 8px;">
          ₹ {{ formatCurrency((stats.purchase.total_brokerage || 0) + (stats.sales.total_brokerage || 0)) }}
        </div>
        <div style="font-size: 12px; color: #166534; margin-top: 8px;">
          Unified ledger across purchase &amp; sell
        </div>
      </div>
    </div>

    <!-- Quick Action Cards Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-bottom: 28px;">
      <router-link to="/purchase" class="content-card" style="text-decoration: none; color: inherit; transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer;">
        <div style="font-size: 24px; margin-bottom: 12px;">🛒</div>
        <div style="font-size: 16px; font-weight: 700; color: #1e3a8a;">New Purchase Entry</div>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
          Select Purchase Broker, Supplier, and Item. The system automatically pre-fills the configured brokerage terms with live amount breakdown.
        </p>
        <div style="margin-top: 14px; font-size: 13px; font-weight: 600; color: #2563eb;">
          Open Purchase Entry →
        </div>
      </router-link>

      <router-link to="/sell" class="content-card" style="text-decoration: none; color: inherit; transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer;">
        <div style="font-size: 24px; margin-bottom: 12px;">🏷️</div>
        <div style="font-size: 16px; font-weight: 700; color: #065f46;">New Sell Entry</div>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
          Select Sell Broker, Customer, and Item. Auto-applies configured terms with bidirectional Quantity ⇄ Bags unit calculation.
        </p>
        <div style="margin-top: 14px; font-size: 13px; font-weight: 600; color: #059669;">
          Open Sell Entry →
        </div>
      </router-link>

      <router-link to="/brokers" class="content-card" style="text-decoration: none; color: inherit; transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer;">
        <div style="font-size: 24px; margin-bottom: 12px;">👥</div>
        <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Brokers Master &amp; Checkpoints</div>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
          Manage Purchase / Sell checkboxes and 3-method table (Per Bag, Per Quintal, Percentage) with mutual exclusivity per row.
        </p>
        <div style="margin-top: 14px; font-size: 13px; font-weight: 600; color: #2563eb;">
          Manage Brokers →
        </div>
      </router-link>

      <router-link to="/rate-configs" class="content-card" style="text-decoration: none; color: inherit; transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: pointer;">
        <div style="font-size: 24px; margin-bottom: 12px;">📅</div>
        <div style="font-size: 16px; font-weight: 700; color: #7e22ce;">Date-Wise Broker Rate Contracts</div>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
          Create separate DocType records for date-effective rate revisions. Dynamically reveals Purchase and/or Sell tables.
        </p>
        <div style="margin-top: 14px; font-size: 13px; font-weight: 600; color: #7e22ce;">
          Configure Date-Wise Rates →
        </div>
      </router-link>
    </div>

    <!-- Feature Architecture Banner -->
    <div class="content-card" style="background: #f8fafc;">
      <div style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
        🔍 System Design &amp; Problem Statement Alignment
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; font-size: 13px; color: #334155;">
        <div style="background: #fff; padding: 14px; border-radius: 6px; border: 1px solid var(--border);">
          <strong>1. Broker Checkpoints</strong>
          <p style="color: #64748b; margin-top: 4px;">
            Dual boolean checkpoints (<code>Applicable for Purchase</code> and <code>Applicable for Sell</code>). A broker can be active for either role or both.
          </p>
        </div>

        <div style="background: #fff; padding: 14px; border-radius: 6px; border: 1px solid var(--border);">
          <strong>2. 3-Method Table Columns</strong>
          <p style="color: #64748b; margin-top: 4px;">
            Tables feature <code>Item</code>, <code>Per Bag (₹)</code>, <code>Per Quintal (₹)</code>, and <code>Percentage (%)</code>. Each item strictly enforces only one active method.
          </p>
        </div>

        <div style="background: #fff; padding: 14px; border-radius: 6px; border: 1px solid var(--border);">
          <strong>3. Auto-Fetch in Entries</strong>
          <p style="color: #64748b; margin-top: 4px;">
            Selecting broker and item in Purchase or Sell automatically inherits the exact configured percentage or bag/quintal rate.
          </p>
        </div>

        <div style="background: #fff; padding: 14px; border-radius: 6px; border: 1px solid var(--border);">
          <strong>4. Date-Wise Separate DocType</strong>
          <p style="color: #64748b; margin-top: 4px;">
            <code>Broker Rate Configuration</code> provides date-effective agreements, dynamically loading tables according to broker capabilities.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'

const { getDashboardSummary } = useFrappeApi()

const stats = reactive({
  brokers: { total: 0, purchase: 0, sales: 0 },
  purchase: { count: 0, total_trade: 0, total_brokerage: 0 },
  sales: { count: 0, total_trade: 0, total_brokerage: 0 },
})

const loadStats = async () => {
  try {
    const data = await getDashboardSummary()
    if (data) {
      stats.brokers = data.brokers || stats.brokers
      stats.purchase = data.purchase || stats.purchase
      stats.sales = data.sales || stats.sales
    }
  } catch (e) {
    console.error('Failed to load dashboard stats:', e)
  }
}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadStats()
})
</script>

