<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="content-card">
        <div class="page-header">
          <div>
            <div class="page-title">
              <span>📅 Date-Wise Broker Rate Configurations</span>
            </div>
            <div class="page-subtitle">
              Separate DocType for managing effective date-wise brokerage rate contracts. Select broker to dynamically load Purchase and/or Sell rate tables.
            </div>
          </div>

          <div style="display: flex; gap: 10px;">
            <button type="button" class="btn btn-primary" @click="showModal = true">
              ➕ New Date-Wise Rate Configuration (Full Screen)
            </button>
          </div>
        </div>

        <!-- Table of Configurations -->
        <div style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Config ID</th>
                <th>Effective Date</th>
                <th>Broker ID</th>
                <th>Broker Name</th>
                <th>Purchase Rules</th>
                <th>Sell Rules</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="configs.length === 0">
                <td colspan="7" style="text-align: center; padding: 30px; color: var(--muted);">
                  {{ isLoading ? 'Loading configurations...' : 'No date-wise configurations recorded yet.' }}
                </td>
              </tr>
              <tr v-for="c in configs" :key="c.name">
                <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px; color: var(--blue);">
                  {{ c.name }}
                </td>
                <td style="font-weight: 600; color: var(--navy);">
                  {{ c.effective_date }}
                </td>
                <td style="font-family: var(--font-mono); font-size: 12px; color: var(--muted);">
                  {{ c.broker }}
                </td>
                <td style="font-weight: 700; color: var(--navy);">
                  {{ c.broker_name }}
                </td>
                <td>
                  <span class="badge badge-blue">
                    {{ c.purchase_rules_count || 0 }} items
                  </span>
                </td>
                <td>
                  <span class="badge badge-green">
                    {{ c.sales_rules_count || 0 }} items
                  </span>
                </td>
                <td>
                  <span class="badge badge-green">{{ c.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Rate Config Modal -->
        <RateConfigModal
          :show="showModal"
          @close="showModal = false"
          @saved="onConfigSaved"
        />
      </div>
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Rate Configurations"
      :items="menuItems"
      :active-index="0"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import RateConfigModal from '../components/RateConfigModal.vue'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getRateConfigurations } = useFrappeApi()

const configs = ref([])
const showModal = ref(false)
const isLoading = ref(false)

const loadConfigs = async () => {
  isLoading.value = true
  try {
    configs.value = await getRateConfigurations()
  } catch (e) {
    console.error('Failed to load rate configurations:', e)
  } finally {
    isLoading.value = false
  }
}

const onConfigSaved = () => {
  showModal.value = false
  loadConfigs()
  showToast('Rate configuration saved')
}

// Right-side Menu Items
const menuItems = [
  { isHeader: true, label: '📅 RATE CARDS' },
  { key: 'N', label: '+ New Rate Card (Full Screen)', action: () => { showModal.value = true } },
  { key: 'B', label: 'Brokers Directory', action: () => router.push('/brokers') },

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
  loadConfigs()
})
</script>
