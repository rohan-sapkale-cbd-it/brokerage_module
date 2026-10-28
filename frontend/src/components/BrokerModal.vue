<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-dialog" style="max-width: 950px;">
      <div class="modal-header">
        <div class="modal-title">
          <span>{{ form.name ? '✏️ Edit Broker Master' : '➕ Create New Broker Master' }}</span>
        </div>
        <button type="button" class="clear-btn" style="position: static;" @click="close">✕</button>
      </div>

      <div class="modal-body">
        <!-- Basic info -->
        <div class="form-grid" style="grid-template-columns: 2fr 1fr 1fr; margin-bottom: 20px;">
          <div class="form-group">
            <label>Broker Full Name *</label>
            <input v-model="form.broker_name" type="text" placeholder="e.g. Chirag Trading Co. / Nitin Bhai" required />
          </div>
          <div class="form-group">
            <label>Mobile Number (10 digits)</label>
            <input v-model="form.mobile_no" type="text" maxlength="10" placeholder="e.g. 9876543210" />
          </div>
          <div class="form-group">
            <label>City / Location</label>
            <input v-model="form.city" type="text" placeholder="e.g. Pune, Kolhapur" />
          </div>
        </div>

        <!-- Checkpoints Section -->
        <div style="background: #f1f5f9; padding: 14px 18px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px;">
          <div style="font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">
            📌 Broker Operational Checkpoints (Select one or both)
          </div>
          <div style="display: flex; gap: 30px; align-items: center;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px; font-weight: 600; color: #0f172a;">
              <input type="checkbox" v-model="form.applicable_for_purchase" style="width: 18px; height: 18px; accent-color: #2563eb;" />
              <span>🛒 Applicable for Purchase</span>
            </label>

            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px; font-weight: 600; color: #0f172a;">
              <input type="checkbox" v-model="form.applicable_for_sales" style="width: 18px; height: 18px; accent-color: #059669;" />
              <span>🏷️ Applicable for Sell</span>
            </label>
          </div>
        </div>

        <!-- 1. Purchase Brokerage Table -->
        <div v-if="form.applicable_for_purchase" style="margin-bottom: 24px; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px; background: #fafcff;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
              <span style="font-weight: 700; font-size: 14px; color: #1e40af;">🛒 Purchase Brokerage Rates Table</span>
              <span style="font-size: 12px; color: #64748b; margin-left: 8px;">(Configured rules applied when shop purchases through this broker)</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="addPurchaseRow">
              + Add Item Row
            </button>
          </div>

          <div v-if="form.purchase_brokerage_rules.length === 0" style="text-align: center; padding: 20px; color: #64748b; font-size: 12.5px;">
            No purchase rules added yet. Click "+ Add Item Row" to configure item rates.
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
                    <button type="button" class="clear-btn" style="position: static; color: #dc2626;" @click="removePurchaseRow(idx)" title="Remove row">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 2. Sell Brokerage Table -->
        <div v-if="form.applicable_for_sales" style="border: 1px solid #a7f3d0; border-radius: 8px; padding: 14px; background: #f0fdf4;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
              <span style="font-weight: 700; font-size: 14px; color: #065f46;">🏷️ Sell Brokerage Rates Table</span>
              <span style="font-size: 12px; color: #64748b; margin-left: 8px;">(Configured rules applied when shop sells through this broker)</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="addSalesRow">
              + Add Item Row
            </button>
          </div>

          <div v-if="form.sales_brokerage_rules.length === 0" style="text-align: center; padding: 20px; color: #64748b; font-size: 12.5px;">
            No sell rules added yet. Click "+ Add Item Row" to configure item rates.
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
                    <button type="button" class="clear-btn" style="position: static; color: #dc2626;" @click="removeSalesRow(idx)" title="Remove row">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="close">Cancel</button>
        <button type="button" class="btn btn-primary" :disabled="isSaving" @click="submitSave">
          {{ isSaving ? 'Saving...' : '💾 Save Broker Master' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import TypeaheadSelect from './TypeaheadSelect.vue'

const props = defineProps({
  show: Boolean,
  brokerData: Object,
})

const emit = defineEmits(['close', 'saved'])

const { saveBroker, searchEntities } = useFrappeApi()
const isSaving = ref(false)

const form = reactive({
  name: '',
  broker_name: '',
  mobile_no: '',
  city: '',
  state: '',
  status: 'Active',
  applicable_for_purchase: true,
  applicable_for_sales: true,
  purchase_brokerage_rules: [],
  sales_brokerage_rules: [],
})

watch(
  () => props.brokerData,
  (val) => {
    if (val) {
      form.name = val.name || ''
      form.broker_name = val.broker_name || ''
      form.mobile_no = val.mobile_no || ''
      form.city = val.city || ''
      form.state = val.state || ''
      form.status = val.status || 'Active'
      form.applicable_for_purchase = val.applicable_for_purchase in [1, true, '1']
      form.applicable_for_sales = val.applicable_for_sales in [1, true, '1']
      form.purchase_brokerage_rules = (val.purchase_brokerage_rules || []).map((r) => ({ ...r }))
      form.sales_brokerage_rules = (val.sales_brokerage_rules || []).map((r) => ({ ...r }))
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

const resetForm = () => {
  form.name = ''
  form.broker_name = ''
  form.mobile_no = ''
  form.city = ''
  form.state = ''
  form.status = 'Active'
  form.applicable_for_purchase = true
  form.applicable_for_sales = true
  form.purchase_brokerage_rules = []
  form.sales_brokerage_rules = []
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
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

// Mutual Exclusivity Rules: Each item row strictly supports ONE calculation method
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
  if (!form.broker_name.trim()) {
    alert('Please enter Broker Name.')
    return
  }
  if (!form.applicable_for_purchase && !form.applicable_for_sales) {
    alert('Please select at least one checkpoint: Applicable for Purchase or Applicable for Sell.')
    return
  }

  isSaving.value = true
  try {
    const res = await saveBroker(form)
    emit('saved', res)
    close()
  } catch (e) {
    alert('Error saving broker: ' + e.message)
  } finally {
    isSaving.value = false
  }
}
</script>
