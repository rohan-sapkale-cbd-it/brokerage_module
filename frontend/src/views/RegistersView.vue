<template>
  <div class="content-card">
    <div class="page-header">
      <div>
        <div class="page-title">
          <span>📋 Brokerage Audit Registers</span>
        </div>
        <div class="page-subtitle">
          View all booked Purchase &amp; Sell entries with exact brokerage calculations and source audit.
        </div>
      </div>

      <div style="display: flex; gap: 8px;">
        <button
          type="button"
          class="btn"
          :class="currentType === 'Purchase' ? 'btn-primary' : 'btn-secondary'"
          @click="switchType('Purchase')"
        >
          🛒 Purchase Register
        </button>
        <button
          type="button"
          class="btn"
          :class="currentType === 'Sell' ? 'btn-primary' : 'btn-secondary'"
          @click="switchType('Sell')"
        >
          🏷️ Sell Register
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div style="background: #f8fafc; padding: 14px 18px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px; display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap;">
      <div class="form-group" style="min-width: 150px;">
        <label>From Date</label>
        <input v-model="filters.from_date" type="date" @change="loadData" />
      </div>

      <div class="form-group" style="min-width: 150px;">
        <label>To Date</label>
        <input v-model="filters.to_date" type="date" @change="loadData" />
      </div>

      <div class="form-group" style="min-width: 260px;">
        <label>Filter by Broker</label>
        <TypeaheadSelect
          v-model="filters.broker"
          :label="filters.broker_name"
          placeholder="All Brokers..."
          :fetch-fn="searchBrokers"
          @change="onBrokerFilter"
        />
      </div>

      <button type="button" class="btn btn-secondary btn-sm" style="margin-bottom: 4px;" @click="resetFilters">
        Reset Filters
      </button>
    </div>

    <!-- Metric Summary Ribbon -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; box-shadow: var(--shadow-sm);">
        <div style="font-size: 11.5px; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Total Vouchers</div>
        <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 4px;">
          {{ summary.total_count }}
        </div>
      </div>

      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; box-shadow: var(--shadow-sm);">
        <div style="font-size: 11.5px; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Total Quantity (Qtl)</div>
        <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 4px;">
          {{ formatNumber(summary.total_qty) }} Qtl
        </div>
      </div>

      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; box-shadow: var(--shadow-sm);">
        <div style="font-size: 11.5px; color: #1e40af; font-weight: 700; text-transform: uppercase;">Total Trade Volume</div>
        <div style="font-size: 22px; font-weight: 800; color: #1e3a8a; margin-top: 4px;">
          ₹ {{ formatCurrency(summary.total_trade) }}
        </div>
      </div>

      <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 14px 18px; box-shadow: var(--shadow-sm);">
        <div style="font-size: 11.5px; color: #065f46; font-weight: 700; text-transform: uppercase;">Total Brokerage Earned / Counted</div>
        <div style="font-size: 22px; font-weight: 800; color: #059669; margin-top: 4px;">
          ₹ {{ formatCurrency(summary.total_brokerage) }}
        </div>
      </div>
    </div>

    <!-- Table of Entries -->
    <div class="data-table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Entry ID</th>
            <th>Date</th>
            <th>Broker</th>
            <th>{{ currentType === 'Purchase' ? 'Supplier' : 'Customer' }}</th>
            <th>Item</th>
            <th style="text-align: right;">Qty (Qtl)</th>
            <th style="text-align: right;">Bags</th>
            <th style="text-align: right;">Rate (₹)</th>
            <th style="text-align: right;">Trade Amount (₹)</th>
            <th>Method</th>
            <th style="text-align: right;">Brokerage Rate</th>
            <th style="text-align: right;">Brokerage (₹)</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="records.length === 0">
            <td colspan="13" style="text-align: center; padding: 40px; color: #64748b;">
              No {{ currentType }} entries found for selected criteria.
            </td>
          </tr>
          <tr v-for="r in records" :key="r.name">
            <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px;">
              <a :href="`/app/${currentType === 'Purchase' ? 'broker-purchase-entry' : 'broker-sales-entry'}/${r.name}`" target="_blank" style="color: #2563eb; text-decoration: none;">
                {{ r.name }} ↗
              </a>
            </td>
            <td>{{ r.posting_date }}</td>
            <td style="font-weight: 600;">{{ r.broker_name || r.broker }}</td>
            <td>{{ r.supplier || r.customer }}</td>
            <td style="font-weight: 600;">{{ r.item_name || r.item }}</td>
            <td style="text-align: right;">{{ formatNumber(r.quantity) }}</td>
            <td style="text-align: right;">{{ formatNumber(r.bags) }}</td>
            <td style="text-align: right;">₹{{ formatCurrency(r.rate) }}</td>
            <td style="text-align: right; font-weight: 700; color: #0f172a;">
              ₹{{ formatCurrency(r.trade_amount) }}
            </td>
            <td>
              <span class="badge badge-blue">{{ r.brokerage_method }}</span>
            </td>
            <td style="text-align: right; font-family: var(--font-mono);">
              {{ r.brokerage_method === 'Percentage' ? `${r.brokerage_rate}%` : (r.brokerage_method === 'Per Bag' ? `₹${r.brokerage_rate}/bag` : `₹${r.brokerage_rate}/qtl`) }}
            </td>
            <td style="text-align: right; font-weight: 800; color: #059669;">
              ₹{{ formatCurrency(r.brokerage_amount) }}
            </td>
            <td>
              <span class="badge badge-green">{{ r.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import TypeaheadSelect from '../components/TypeaheadSelect.vue'

const route = useRoute()
const router = useRouter()
const { getEntries, searchEntities } = useFrappeApi()

const currentType = ref('Purchase')
const records = ref([])
const summary = reactive({
  total_count: 0,
  total_trade: 0,
  total_brokerage: 0,
  total_qty: 0,
})

const filters = reactive({
  from_date: '',
  to_date: '',
  broker: '',
  broker_name: '',
})

const switchType = (type) => {
  currentType.value = type
  router.replace({ query: { type } })
  loadData()
}

const searchBrokers = async (q) => {
  return await searchEntities('Broker', q)
}

const onBrokerFilter = (b) => {
  filters.broker = b ? (b.id || b.name) : ''
  filters.broker_name = b ? (b.label || b.name) : ''
  loadData()
}

const resetFilters = () => {
  filters.from_date = ''
  filters.to_date = ''
  filters.broker = ''
  filters.broker_name = ''
  loadData()
}

const loadData = async () => {
  try {
    const res = await getEntries(currentType.value, {
      from_date: filters.from_date || undefined,
      to_date: filters.to_date || undefined,
      broker: filters.broker || undefined,
    })
    records.value = res.records || []
    summary.total_count = res.total_count || 0
    summary.total_trade = res.total_trade || 0
    summary.total_brokerage = res.total_brokerage || 0
    summary.total_qty = res.total_qty || 0
  } catch (e) {
    console.error('Failed to load register entries:', e)
  }
}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

onMounted(() => {
  if (route.query.type === 'Sell') {
    currentType.value = 'Sell'
  }
  loadData()
})
</script>
