<template>
  <div class="content-card">
    <div class="page-header">
      <div>
        <div class="page-title">
          <span>👥 Brokers Directory &amp; Master Setup</span>
        </div>
        <div class="page-subtitle">
          Configure broker checkpoints (Purchase / Sell) and item-wise brokerage rules (Per Bag, Per Quintal, or Percentage).
        </div>
      </div>

      <div style="display: flex; gap: 10px;">
        <button type="button" class="btn btn-primary" @click="openCreateModal">
          ➕ New Broker Master
        </button>
      </div>
    </div>

    <!-- Filter chips -->
    <div style="display: flex; gap: 10px; margin-bottom: 18px; align-items: center; flex-wrap: wrap;">
      <span style="font-size: 13px; font-weight: 600; color: #475569;">Filter:</span>
      <button
        type="button"
        class="btn btn-sm"
        :class="filterRole === 'All' ? 'btn-primary' : 'btn-secondary'"
        @click="filterRole = 'All'"
      >
        All Brokers ({{ brokers.length }})
      </button>
      <button
        type="button"
        class="btn btn-sm"
        :class="filterRole === 'Purchase' ? 'btn-primary' : 'btn-secondary'"
        @click="filterRole = 'Purchase'"
      >
        🛒 Purchase Brokers ({{ countPurchase }})
      </button>
      <button
        type="button"
        class="btn btn-sm"
        :class="filterRole === 'Sell' ? 'btn-primary' : 'btn-secondary'"
        @click="filterRole = 'Sell'"
      >
        🏷️ Sell Brokers ({{ countSales }})
      </button>
    </div>

    <!-- Table of Brokers -->
    <div class="data-table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Broker Name</th>
            <th>Mobile</th>
            <th>City</th>
            <th>Checkpoints / Roles</th>
            <th>Purchase Rules</th>
            <th>Sell Rules</th>
            <th>Status</th>
            <th style="text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredBrokers.length === 0">
            <td colspan="9" style="text-align: center; padding: 30px; color: #64748b;">
              No brokers found matching current filter. Click "➕ New Broker Master" to create one.
            </td>
          </tr>
          <tr v-for="b in filteredBrokers" :key="b.name">
            <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px; color: #2563eb;">
              {{ b.name }}
            </td>
            <td style="font-weight: 700; color: #0f172a;">
              {{ b.broker_name }}
            </td>
            <td>{{ b.mobile_no || '—' }}</td>
            <td>{{ b.city || '—' }}</td>
            <td>
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span v-if="b.applicable_for_purchase" class="badge badge-blue">🛒 Purchase</span>
                <span v-if="b.applicable_for_sales" class="badge badge-green">🏷️ Sell</span>
                <span v-if="!b.applicable_for_purchase && !b.applicable_for_sales" class="badge badge-gray">None</span>
              </div>
            </td>
            <td>
              <span class="badge badge-gray">{{ b.purchase_rules_count || 0 }} items</span>
            </td>
            <td>
              <span class="badge badge-gray">{{ b.sales_rules_count || 0 }} items</span>
            </td>
            <td>
              <span :class="b.status === 'Active' ? 'badge badge-green' : 'badge badge-gray'">
                {{ b.status }}
              </span>
            </td>
            <td style="text-align: right;">
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="editBroker(b)"
              >
                ✏️ Edit &amp; Rates
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Broker Create / Edit Modal -->
    <BrokerModal
      :show="showModal"
      :broker-data="activeBrokerData"
      @close="showModal = false"
      @saved="onBrokerSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import BrokerModal from '../components/BrokerModal.vue'

const { searchEntities, getBrokerDetails } = useFrappeApi()

const brokers = ref([])
const filterRole = ref('All')
const showModal = ref(false)
const activeBrokerData = ref(null)
const isLoading = ref(false)

const loadBrokers = async () => {
  isLoading.value = true
  try {
    const list = await searchEntities('Broker', '', { limit: 100 })
    // Fetch counts and full details
    const fullList = []
    for (const b of list) {
      try {
        const details = await getBrokerDetails(b.id || b.name)
        fullList.push({
          ...b,
          applicable_for_purchase: details.applicable_for_purchase,
          applicable_for_sales: details.applicable_for_sales,
          purchase_rules_count: details.purchase_brokerage_rules?.length || 0,
          sales_rules_count: details.sales_brokerage_rules?.length || 0,
        })
      } catch (e) {
        fullList.push(b)
      }
    }
    brokers.value = fullList
  } catch (e) {
    console.error('Failed to load brokers:', e)
  } finally {
    isLoading.value = false
  }
}

const countPurchase = computed(() => brokers.value.filter((b) => b.applicable_for_purchase).length)
const countSales = computed(() => brokers.value.filter((b) => b.applicable_for_sales).length)

const filteredBrokers = computed(() => {
  if (filterRole.value === 'Purchase') {
    return brokers.value.filter((b) => b.applicable_for_purchase)
  }
  if (filterRole.value === 'Sell') {
    return brokers.value.filter((b) => b.applicable_for_sales)
  }
  return brokers.value
})

const openCreateModal = () => {
  activeBrokerData.value = null
  showModal.value = true
}

const editBroker = async (b) => {
  try {
    const details = await getBrokerDetails(b.id || b.name)
    activeBrokerData.value = details
    showModal.value = true
  } catch (e) {
    alert('Failed to load broker: ' + e.message)
  }
}

const onBrokerSaved = () => {
  loadBrokers()
}

onMounted(() => {
  loadBrokers()
})
</script>
