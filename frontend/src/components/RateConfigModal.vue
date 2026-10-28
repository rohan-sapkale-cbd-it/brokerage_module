<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-dialog" style="max-width: 950px;">
      <div class="modal-header">
        <div class="modal-title">
          <span>📅 Date-Wise Broker Rate Configuration (Separate DocType)</span>
        </div>
        <button type="button" class="clear-btn" style="position: static;" @click="close">✕</button>
      </div>

      <div class="modal-body">
        <div class="notice-banner notice-info">
          <span>💡 Select Effective Date and Broker Name. Based on whether the broker is marked for <strong>Purchase</strong>, <strong>Sell</strong>, or <strong>Both</strong>, the respective tables dynamically load here for date-wise rate rules.</span>
        </div>

        <div class="form-grid" style="grid-template-columns: 1fr 2fr; margin-bottom: 20px;">
          <div class="form-group">
            <label>Effective Date *</label>
            <input v-model="form.effective_date" type="date" required />
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

        <!-- Broker Eligibility Badges -->
        <div v-if="selectedBroker" style="display: flex; gap: 12px; align-items: center; margin-bottom: 16px; padding: 10px 14px; background: #f8fafc; border-radius: 6px; border: 1px solid var(--border);">
          <span style="font-size: 13px; font-weight: 600; color: #334155;">Broker Roles:</span>
          <span
            class="badge"
            :class="selectedBroker.applicable_for_purchase ? 'badge-blue' : 'badge-gray'"
          >
            {{ selectedBroker.applicable_for_purchase ? '✓ Purchase Applicable' : '✗ Purchase Inactive' }}
          </span>
          <span
            class="badge"
            :class="selectedBroker.applicable_for_sales ? 'badge-green' : 'badge-gray'"
          >
            {{ selectedBroker.applicable_for_sales ? '✓ Sell Applicable' : '✗ Sell Inactive' }}
          </span>
        </div>

        <!-- 1. Purchase Table (shown only if broker is applicable for purchase) -->
        <div v-if="selectedBroker && selectedBroker.applicable_for_purchase" style="margin-bottom: 24px; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px; background: #fafcff;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
              <span style="font-weight: 700; font-size: 14px; color: #1e40af;">🛒 Purchase Brokerage Rates (Effective from {{ form.effective_date }})</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="addPurchaseRow">
              + Add Purchase Item Rate
            </button>
          </div>

          <div v-if="form.purchase_brokerage_rules.length === 0" style="text-align: center; padding: 16px; color: #64748b; font-size: 12.5px;">
            No date-wise purchase rates set. Click "+ Add Purchase Item Rate" to configure.
          </div>

          <div v-else class="data-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 32%;">Item</th>
                  <th style="width: 18%;">Active Method</th>
                  <th style="width: 15%;">Per Bag (₹)</th>
                  <th style="width: 15%;">Per Quintal (₹)</th>
                  <th style="width: 15%;">Percentage (%)</th>
                  <th style="width: 5%;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.purchase_brokerage_rules" :key="idx">
                  <td>
                    <TypeaheadSelect
                      v-model="row.item"
                      :label="row.item_name || row.item"
                      placeholder="Search Item..."
                      :fetch-fn="searchItems"
                      @change="(it) => { if(it) row.item_name = it.label || it.name }"
                    />
                  </td>
                  <td>
                    <select v-model="row.brokerage_method" @change="onMethodChange(row)">
                      <option value="Percentage">Percentage</option>
                      <option value="Per Bag">Per Bag</option>
                      <option value="Per Quintal">Per Quintal</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_bag"
                      :style="row.brokerage_method === 'Per Bag' ? 'border-color: #2563eb; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerBagInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_quintal"
                      :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #2563eb; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerQuintalInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.percentage"
                      :style="row.brokerage_method === 'Percentage' ? 'border-color: #2563eb; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPercentageInput(row)"
                    />
                  </td>
                  <td style="text-align: center;">
                    <button type="button" class="clear-btn" style="position: static; color: #dc2626;" @click="removePurchaseRow(idx)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 2. Sell Table (shown only if broker is applicable for sell) -->
        <div v-if="selectedBroker && selectedBroker.applicable_for_sales" style="border: 1px solid #a7f3d0; border-radius: 8px; padding: 14px; background: #f0fdf4;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
              <span style="font-weight: 700; font-size: 14px; color: #065f46;">🏷️ Sell Brokerage Rates (Effective from {{ form.effective_date }})</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="addSalesRow">
              + Add Sell Item Rate
            </button>
          </div>

          <div v-if="form.sales_brokerage_rules.length === 0" style="text-align: center; padding: 16px; color: #64748b; font-size: 12.5px;">
            No date-wise sell rates set. Click "+ Add Sell Item Rate" to configure.
          </div>

          <div v-else class="data-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 32%;">Item</th>
                  <th style="width: 18%;">Active Method</th>
                  <th style="width: 15%;">Per Bag (₹)</th>
                  <th style="width: 15%;">Per Quintal (₹)</th>
                  <th style="width: 15%;">Percentage (%)</th>
                  <th style="width: 5%;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.sales_brokerage_rules" :key="idx">
                  <td>
                    <TypeaheadSelect
                      v-model="row.item"
                      :label="row.item_name || row.item"
                      placeholder="Search Item..."
                      :fetch-fn="searchItems"
                      @change="(it) => { if(it) row.item_name = it.label || it.name }"
                    />
                  </td>
                  <td>
                    <select v-model="row.brokerage_method" @change="onMethodChange(row)">
                      <option value="Percentage">Percentage</option>
                      <option value="Per Bag">Per Bag</option>
                      <option value="Per Quintal">Per Quintal</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_bag"
                      :style="row.brokerage_method === 'Per Bag' ? 'border-color: #059669; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerBagInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.per_quintal"
                      :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #059669; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPerQuintalInput(row)"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      v-model.number="row.percentage"
                      :style="row.brokerage_method === 'Percentage' ? 'border-color: #059669; font-weight: 700;' : 'opacity: 0.5;'"
                      placeholder="0.00"
                      @input="onPercentageInput(row)"
                    />
                  </td>
                  <td style="text-align: center;">
                    <button type="button" class="clear-btn" style="position: static; color: #dc2626;" @click="removeSalesRow(idx)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="!selectedBroker" style="text-align: center; padding: 40px; color: #94a3b8; font-size: 13.5px;">
          Select a Broker above to automatically reveal applicable Purchase and Sell rate tables.
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="close">Cancel</button>
        <button type="button" class="btn btn-primary" :disabled="isSaving || !selectedBroker" @click="submitSave">
          {{ isSaving ? 'Saving...' : '💾 Save Date-Wise Configuration' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import TypeaheadSelect from './TypeaheadSelect.vue'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const { searchEntities, getBrokerDetails, saveRateConfiguration } = useFrappeApi()
const isSaving = ref(false)
const selectedBroker = ref(null)

const form = reactive({
  effective_date: bootState.today,
  broker: '',
  broker_name: '',
  status: 'Active',
  purchase_brokerage_rules: [],
  sales_brokerage_rules: [],
})

const searchBrokers = async (q) => {
  return await searchEntities('Broker', q)
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
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
    // Pre-populate with existing master rules as sensible baseline
    form.purchase_brokerage_rules = (details.purchase_brokerage_rules || []).map((r) => ({ ...r }))
    form.sales_brokerage_rules = (details.sales_brokerage_rules || []).map((r) => ({ ...r }))
  } catch (e) {
    console.error('Failed to load broker details:', e)
  }
}

const addPurchaseRow = () => {
  form.purchase_brokerage_rules.push({
    item: '',
    item_name: '',
    brokerage_method: 'Percentage',
    percentage: 5.0,
    per_bag: 0,
    per_quintal: 0,
    remarks: '',
  })
}

const removePurchaseRow = (idx) => {
  form.purchase_brokerage_rules.splice(idx, 1)
}

const addSalesRow = () => {
  form.sales_brokerage_rules.push({
    item: '',
    item_name: '',
    brokerage_method: 'Percentage',
    percentage: 5.0,
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

const submitSave = async () => {
  if (!form.broker) {
    alert('Please select a broker.')
    return
  }

  isSaving.value = true
  try {
    const res = await saveRateConfiguration(form)
    emit('saved', res)
    close()
  } catch (e) {
    alert('Error saving rate configuration: ' + e.message)
  } finally {
    isSaving.value = false
  }
}
</script>
