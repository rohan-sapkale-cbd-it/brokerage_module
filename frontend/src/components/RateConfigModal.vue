<template>
  <div v-if="show" class="modal-overlay" :class="{ 'fullscreen-overlay': isFullscreen }" @click.self="close">
    <div
      class="modal-dialog"
      :class="{ 'modal-fullscreen': isFullscreen }"
      :style="isFullscreen ? '' : 'max-width: 1100px; width: 95%; max-height: 92vh;'"
    >
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
          <div class="modal-title" style="display: flex; align-items: center; gap: 8px;">
            <span>📅 Date-Wise Broker Rate Configuration</span>
            <span v-if="isFullscreen" class="badge badge-purple" style="font-size: 11px;">⛶ Full Screen Mode</span>
          </div>
          <span v-if="selectedBroker" class="badge badge-blue">Broker: {{ selectedBroker.broker_name || form.broker }}</span>
        </div>

        <div style="display: flex; align-items: center; gap: 10px;">
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            style="background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.25);"
            @click="isFullscreen = !isFullscreen"
          >
            {{ isFullscreen ? '🗗 Standard Window' : '⛶ Full Screen' }}
          </button>
          <button
            type="button"
            class="btn btn-sm"
            style="background: #ef4444; color: #fff; font-weight: 700; border: none; padding: 6px 12px;"
            @click="close"
          >
            ✕ Close
          </button>
        </div>
      </div>

      <div class="modal-body">
        <div class="notice-banner notice-info" style="margin-bottom: 20px;">
          <span>💡 Select Effective Date and Broker Name. Based on whether the broker is marked for <strong>Purchase</strong>, <strong>Sell</strong>, or <strong>Both</strong>, the respective tables dynamically load here for date-wise rate rules.</span>
        </div>

        <!-- Meta Grid -->
        <div style="background: #ffffff; padding: 18px 24px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 24px;">
          <div class="form-grid" style="grid-template-columns: 1fr 2fr; gap: 20px;">
            <div class="form-group">
              <label>Effective Date *</label>
              <input v-model="form.effective_date" type="date" required style="font-size: 14px;" />
            </div>

            <div class="form-group">
              <label>Broker Name *</label>
              <TypeaheadSelect
                v-model="form.broker"
                :label="form.broker_name"
                placeholder="Search Broker Name..."
                :fetch-fn="searchBrokers"
                @change="onBrokerSelect"
              />
            </div>
          </div>
        </div>

        <!-- Broker Eligibility Badges -->
        <div v-if="selectedBroker" style="display: flex; gap: 14px; align-items: center; margin-bottom: 20px; padding: 12px 18px; background: #ffffff; border-radius: 8px; border: 1px solid var(--border);">
          <span style="font-size: 13px; font-weight: 700; color: #334155;">Active Checkpoints:</span>
          <span
            class="badge"
            :class="selectedBroker.applicable_for_purchase ? 'badge-blue' : 'badge-gray'"
          >
            {{ selectedBroker.applicable_for_purchase ? '✓ Purchase Checkpoint Active' : '✗ Purchase Inactive' }}
          </span>
          <span
            class="badge"
            :class="selectedBroker.applicable_for_sales ? 'badge-green' : 'badge-gray'"
          >
            {{ selectedBroker.applicable_for_sales ? '✓ Sell Checkpoint Active' : '✗ Sell Inactive' }}
          </span>
        </div>

        <!-- 1. Purchase Table (shown only if broker is applicable for purchase) -->
        <div
          v-if="selectedBroker && selectedBroker.applicable_for_purchase"
          style="background: #ffffff; border: 2px solid #93c5fd; border-radius: 10px; padding: 20px 24px; margin-bottom: 24px;"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div>
              <span style="font-weight: 800; font-size: 15px; color: #1e40af;">🛒 Purchase Brokerage Rates (Effective from {{ form.effective_date }})</span>
            </div>
            <div style="display: flex; gap: 8px;">
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="quickAddAllStockGroups('purchase_brokerage_rules')"
              >
                ⚡ Add All Stock Groups
              </button>
              <button type="button" class="btn btn-primary btn-sm" @click="addPurchaseRow">
                + Add Purchase Group Rate
              </button>
            </div>
          </div>

          <div v-if="form.purchase_brokerage_rules.length === 0" style="text-align: center; padding: 24px; color: #64748b; font-size: 13px; background: #f8fafc; border-radius: 6px;">
            No date-wise purchase rates set. Click "+ Add Purchase Group Rate" to configure.
          </div>

          <div v-else class="modal-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 36px; text-align: center;">#</th>
                  <th style="min-width: 360px;">Stock Group *</th>
                  <th style="width: 170px;">Active Method</th>
                  <th style="width: 150px;">Per Bag (₹)</th>
                  <th style="width: 150px;">Per Quintal (₹)</th>
                  <th style="width: 150px;">Percentage (%)</th>
                  <th style="width: 44px; text-align: center;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.purchase_brokerage_rules" :key="idx">
                  <td style="text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">{{ idx + 1 }}</td>
                  <td>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <div style="flex: 1; min-width: 240px;">
                        <TypeaheadSelect
                          v-model="row.stock_group"
                          :label="row.stock_group_name || row.stock_group"
                          placeholder="Search Stock Group..."
                          :fetch-fn="searchStockGroups"
                          @change="(g) => { if(g) { row.stock_group_name = g.label || g.name; row.stock_group = g.id || g.name; } }"
                        />
                      </div>
                      <select
                        v-if="availableStockGroups.length > 0"
                        style="width: 150px; font-size: 12px; padding: 7px 8px; background: #f1f5f9;"
                        @change="(e) => onQuickPickStockGroup(row, e)"
                      >
                        <option value="">▼ Pick Group...</option>
                        <option v-for="g in availableStockGroups" :key="g.name" :value="g.name">
                          {{ g.stock_group_name || g.name }}
                        </option>
                      </select>
                    </div>
                  </td>
                  <td>
                    <select v-model="row.brokerage_method" @change="onMethodChange(row)">
                      <option value="Percentage">Percentage (%)</option>
                      <option value="Per Bag">Per Bag (₹)</option>
                      <option value="Per Quintal">Per Quintal (₹)</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_bag"
                      :style="row.brokerage_method === 'Per Bag' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerBagInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_quintal"
                      :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerQuintalInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.percentage"
                      :style="row.brokerage_method === 'Percentage' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPercentageInput(row)"
                    />
                  </td>
                  <td style="text-align: center;">
                    <button type="button" class="btn btn-sm" style="background: transparent; color: #ef4444; border: none; font-size: 16px;" @click="removePurchaseRow(idx)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 2. Sell Table (shown only if broker is applicable for sell) -->
        <div
          v-if="selectedBroker && selectedBroker.applicable_for_sales"
          style="background: #ffffff; border: 2px solid #86efac; border-radius: 10px; padding: 20px 24px; margin-bottom: 24px;"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div>
              <span style="font-weight: 800; font-size: 15px; color: #065f46;">🏷️ Sell Brokerage Rates (Effective from {{ form.effective_date }})</span>
            </div>
            <div style="display: flex; gap: 8px;">
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="quickAddAllStockGroups('sales_brokerage_rules')"
              >
                ⚡ Add All Stock Groups
              </button>
              <button type="button" class="btn btn-success btn-sm" @click="addSalesRow">
                + Add Sell Group Rate
              </button>
            </div>
          </div>

          <div v-if="form.sales_brokerage_rules.length === 0" style="text-align: center; padding: 24px; color: #64748b; font-size: 13px; background: #f8fafc; border-radius: 6px;">
            No date-wise sell rates set. Click "+ Add Sell Group Rate" to configure.
          </div>

          <div v-else class="modal-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 36px; text-align: center;">#</th>
                  <th style="min-width: 360px;">Stock Group *</th>
                  <th style="width: 170px;">Active Method</th>
                  <th style="width: 150px;">Per Bag (₹)</th>
                  <th style="width: 150px;">Per Quintal (₹)</th>
                  <th style="width: 150px;">Percentage (%)</th>
                  <th style="width: 44px; text-align: center;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.sales_brokerage_rules" :key="idx">
                  <td style="text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">{{ idx + 1 }}</td>
                  <td>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <div style="flex: 1; min-width: 240px;">
                        <TypeaheadSelect
                          v-model="row.stock_group"
                          :label="row.stock_group_name || row.stock_group"
                          placeholder="Search Stock Group..."
                          :fetch-fn="searchStockGroups"
                          @change="(g) => { if(g) { row.stock_group_name = g.label || g.name; row.stock_group = g.id || g.name; } }"
                        />
                      </div>
                      <select
                        v-if="availableStockGroups.length > 0"
                        style="width: 150px; font-size: 12px; padding: 7px 8px; background: #f1f5f9;"
                        @change="(e) => onQuickPickStockGroup(row, e)"
                      >
                        <option value="">▼ Pick Group...</option>
                        <option v-for="g in availableStockGroups" :key="g.name" :value="g.name">
                          {{ g.stock_group_name || g.name }}
                        </option>
                      </select>
                    </div>
                  </td>
                  <td>
                    <select v-model="row.brokerage_method" @change="onMethodChange(row)">
                      <option value="Percentage">Percentage (%)</option>
                      <option value="Per Bag">Per Bag (₹)</option>
                      <option value="Per Quintal">Per Quintal (₹)</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_bag"
                      :style="row.brokerage_method === 'Per Bag' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerBagInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_quintal"
                      :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerQuintalInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.percentage"
                      :style="row.brokerage_method === 'Percentage' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPercentageInput(row)"
                    />
                  </td>
                  <td style="text-align: center;">
                    <button type="button" class="btn btn-sm" style="background: transparent; color: #ef4444; border: none; font-size: 16px;" @click="removeSalesRow(idx)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="!selectedBroker" style="text-align: center; padding: 50px 20px; color: #94a3b8; font-size: 14px; background: #ffffff; border-radius: 8px; border: 1px dashed #cbd5e1;">
          <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
          Select a Broker above to automatically reveal applicable Purchase and Sell rate tables.
        </div>
      </div>

      <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 13px; color: #64748b;">
          Status: <span class="badge badge-green">Active Rate Card</span>
        </div>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn btn-secondary" @click="close">Cancel (<kbd>Esc</kbd>)</button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="isSaving || !selectedBroker"
            style="padding: 10px 24px; font-weight: 700;"
            @click="submitSave"
          >
            {{ isSaving ? 'Saving...' : '💾 Save Date-Wise Configuration' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import TypeaheadSelect from './TypeaheadSelect.vue'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const { searchEntities, getBrokerDetails, saveRateConfiguration, getStockGroups } = useFrappeApi()
const isSaving = ref(false)
const isFullscreen = ref(true)
const selectedBroker = ref(null)
const availableStockGroups = ref([])

const form = reactive({
  effective_date: bootState.today || new Date().toISOString().split('T')[0],
  broker: '',
  broker_name: '',
  status: 'Active',
  purchase_brokerage_rules: [],
  sales_brokerage_rules: [],
})

const loadAvailableStockGroups = async () => {
  try {
    const res = await getStockGroups()
    availableStockGroups.value = res || []
  } catch (err) {
    console.error('Failed to load stock groups:', err)
  }
}

watch(
  () => props.show,
  (val) => {
    if (val) {
      loadAvailableStockGroups()
    }
  }
)

const searchBrokers = async (q) => {
  return await searchEntities('Brokers', q)
}

const searchStockGroups = async (q) => {
  return await searchEntities('Stock Group', q)
}

const onQuickPickStockGroup = (row, e) => {
  const chosenVal = e.target.value
  if (!chosenVal) return
  const g = availableStockGroups.value.find((i) => i.name === chosenVal)
  if (g) {
    row.stock_group = g.name
    row.stock_group_name = g.stock_group_name || g.name
  }
  e.target.value = ''
}

const quickAddAllStockGroups = (tableField) => {
  if (availableStockGroups.value.length === 0) return
  const currentTable = form[tableField]
  const existingGroups = new Set(currentTable.map((r) => r.stock_group))

  for (const g of availableStockGroups.value) {
    const grpName = g.name
    if (!existingGroups.has(grpName)) {
      currentTable.push({
        stock_group: grpName,
        stock_group_name: g.stock_group_name || grpName,
        brokerage_method: 'Percentage',
        percentage: 1.0,
        per_bag: 0,
        per_quintal: 0,
        remarks: '',
      })
      existingGroups.add(grpName)
    }
  }
}

const onBrokerSelect = async (item) => {
  if (!item) {
    selectedBroker.value = null
    form.broker = ''
    form.broker_name = ''
    form.purchase_brokerage_rules = []
    form.sales_brokerage_rules = []
    return
  }

  form.broker = item.id || item.name
  form.broker_name = item.label || item.broker_name || form.broker

  try {
    const details = await getBrokerDetails(form.broker)
    selectedBroker.value = details
    form.purchase_brokerage_rules = (details.purchase_brokerage_rules || []).map((r) => ({
      stock_group: r.stock_group || r.item || 'Sugar',
      stock_group_name: r.stock_group_name || r.item_name || r.stock_group || 'Sugar',
      ...r,
    }))
    form.sales_brokerage_rules = (details.sales_brokerage_rules || []).map((r) => ({
      stock_group: r.stock_group || r.item || 'Sugar',
      stock_group_name: r.stock_group_name || r.item_name || r.stock_group || 'Sugar',
      ...r,
    }))
  } catch (e) {
    console.error('Failed to load broker details:', e)
  }
}

const addPurchaseRow = () => {
  const defaultGrp = availableStockGroups.value[0]?.name || 'Sugar'
  form.purchase_brokerage_rules.push({
    stock_group: defaultGrp,
    stock_group_name: defaultGrp,
    brokerage_method: 'Percentage',
    percentage: 1.0,
    per_bag: 0,
    per_quintal: 0,
    remarks: '',
  })
}

const removePurchaseRow = (idx) => {
  form.purchase_brokerage_rules.splice(idx, 1)
}

const addSalesRow = () => {
  const defaultGrp = availableStockGroups.value[0]?.name || 'Sugar'
  form.sales_brokerage_rules.push({
    stock_group: defaultGrp,
    stock_group_name: defaultGrp,
    brokerage_method: 'Percentage',
    percentage: 1.0,
    per_bag: 0,
    per_quintal: 0,
    remarks: '',
  })
}

const removeSalesRow = (idx) => {
  form.sales_brokerage_rules.splice(idx, 1)
}

const onMethodChange = (row) => {
  if (row.brokerage_method === 'Percentage') {
    row.per_bag = 0
    row.per_quintal = 0
    if (!row.percentage) row.percentage = 1.0
  } else if (row.brokerage_method === 'Per Bag') {
    row.percentage = 0
    row.per_quintal = 0
    if (!row.per_bag) row.per_bag = 10.0
  } else if (row.brokerage_method === 'Per Quintal') {
    row.percentage = 0
    row.per_bag = 0
    if (!row.per_quintal) row.per_quintal = 20.0
  }
}

const onPerBagInput = (row) => {
  if (row.per_bag > 0) {
    row.brokerage_method = 'Per Bag'
    row.percentage = 0
    row.per_quintal = 0
  }
}

const onPerQuintalInput = (row) => {
  if (row.per_quintal > 0) {
    row.brokerage_method = 'Per Quintal'
    row.percentage = 0
    row.per_bag = 0
  }
}

const onPercentageInput = (row) => {
  if (row.percentage > 0) {
    row.brokerage_method = 'Percentage'
    row.per_bag = 0
    row.per_quintal = 0
  }
}

const close = () => {
  emit('close')
}

const handleKeydown = (e) => {
  if (!props.show) return
  if (e.key === 'Escape') {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  loadAvailableStockGroups()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

const submitSave = async () => {
  if (!form.broker) {
    alert('Please select a Broker.')
    return
  }
  if (!form.effective_date) {
    alert('Please select Effective Date.')
    return
  }

  isSaving.value = true
  try {
    const res = await saveRateConfiguration(form)
    emit('saved', res)
    close()
  } catch (e) {
    alert('Error saving configuration: ' + e.message)
  } finally {
    isSaving.value = false
  }
}
</script>
