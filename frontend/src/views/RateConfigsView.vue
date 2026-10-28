<template>
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
          ➕ New Date-Wise Rate Configuration
        </button>
      </div>
    </div>

    <!-- Table of Configurations -->
    <div class="data-table-wrap">
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
            <td colspan="7" style="text-align: center; padding: 30px; color: #64748b;">
              No date-wise configurations recorded yet. Click "➕ New Date-Wise Rate Configuration" to set effective date rates.
            </td>
          </tr>
          <tr v-for="c in configs" :key="c.name">
            <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px; color: #2563eb;">
              {{ c.name }}
            </td>
            <td style="font-weight: 600; color: #0f172a;">
              {{ c.effective_date }}
            </td>
            <td style="font-family: var(--font-mono); font-size: 12px; color: #475569;">
              {{ c.broker }}
            </td>
            <td style="font-weight: 700;">
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import RateConfigModal from '../components/RateConfigModal.vue'

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
  loadConfigs()
}

onMounted(() => {
  loadConfigs()
})
</script>

