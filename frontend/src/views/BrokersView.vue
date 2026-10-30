<template>
  <div id="main-layout">
    <div id="content-area">
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
              ➕ New Broker Master (Full Screen)
            </button>
          </div>
        </div>

        <!-- Filter chips -->
        <div style="display: flex; gap: 8px; margin-bottom: 16px; align-items: center; flex-wrap: wrap;">
          <span style="font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase;">Role Filter:</span>
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
        <div style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th style="min-width: 220px;">Broker Name &amp; ID</th>
                <th>Mobile</th>
                <th>City &amp; State</th>
                <th>Checkpoints / Roles</th>
                <th>Purchase Rules</th>
                <th>Sell Rules</th>
                <th>Status</th>
                <th style="text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredBrokers.length === 0">
                <td colspan="8" style="text-align: center; padding: 30px; color: var(--muted);">
                  {{ isLoading ? 'Loading brokers...' : 'No brokers found matching current filter.' }}
                </td>
              </tr>
              <tr v-for="b in filteredBrokers" :key="b.name">
                <td>
                  <div style="font-weight: 800; font-size: 14px; color: var(--navy); display: flex; align-items: center; gap: 6px;">
                    <span>👤</span>
                    <span>{{ b.broker_name }}</span>
                  </div>
                  <div style="font-family: var(--font-mono); font-size: 11px; color: var(--muted); margin-top: 2px;">
                    ID: {{ b.name }}
                  </div>
                </td>
                <td style="font-weight: 600;">{{ b.mobile_no || '—' }}</td>
                <td>{{ b.city ? `${b.city}${b.state ? ', ' + b.state : ''}` : '—' }}</td>
                <td>
                  <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <span v-if="b.applicable_for_purchase" class="badge badge-blue">🛒 Purchase</span>
                    <span v-if="b.applicable_for_sales" class="badge badge-green">🏷️ Sell</span>
                    <span v-if="!b.applicable_for_purchase && !b.applicable_for_sales" class="badge badge-amber">None</span>
                  </div>
                </td>
                <td>
                  <span class="badge badge-blue">{{ b.purchase_rules_count || 0 }} items</span>
                </td>
                <td>
                  <span class="badge badge-green">{{ b.sales_rules_count || 0 }} items</span>
                </td>
                <td>
                  <span :class="b.status === 'Active' ? 'badge badge-green' : 'badge badge-amber'">
                    {{ b.status }}
                  </span>
                </td>
                <td style="text-align: right;">
                  <button
                    type="button"
                    class="btn btn-secondary btn-sm"
                    :title="`Edit rules & rates for ${b.broker_name}`"
                    @click="editBroker(b)"
                  >
                    ✏️ Edit Rates
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
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Brokers Master"
      :items="menuItems"
      :active-index="0"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import BrokerModal from '../components/BrokerModal.vue'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { searchEntities, getBrokerDetails } = useFrappeApi()

const brokers = ref([])
const filterRole = ref('All')
const showModal = ref(false)
const activeBrokerData = ref(null)
const isLoading = ref(false)

const loadBrokers = async () => {
  isLoading.value = true
  try {
    const list = await searchEntities('Brokers', '', { limit: 100 })
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
    showToast('Failed to load broker: ' + e.message)
  }
}

const onBrokerSaved = () => {
  showModal.value = false
  loadBrokers()
  showToast('Broker master updated')
}

// Right-side Menu Items
const menuItems = [
  { isHeader: true, label: '🏢 BROKER MASTERS' },
  { key: 'N', label: '+ New Broker (Full Screen)', action: () => openCreateModal() },
  { key: 'R', label: 'Date-Wise Rate Cards', action: () => router.push('/rate-configs') },

  { isHeader: true, label: '⚡ VOUCHERS' },
  { key: 'F9', label: 'Purchase Entry', action: () => router.push('/purchase') },
  { key: 'F8', label: 'Sales Entry', action: () => router.push('/sell') },

  { isHeader: true, label: '📋 REGISTERS' },
  { key: 'L', label: 'All Registers', action: () => router.push('/registers') },
  { key: 'Esc', label: 'Gateway of Brokerage', action: () => router.push('/') },
]

const handleSelect = (idx) => {
  if (menuItems[idx].isHeader) return
  menuItems[idx].action()
}

onMounted(() => {
  loadBrokers()
})
</script>
