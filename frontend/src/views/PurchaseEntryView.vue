<template>
  <div class="content-card">
    <div class="page-header">
      <div>
        <div class="page-title">
          <span>🛒 Purchase Entry (with Brokerage)</span>
          <span class="badge badge-blue">Purchase Mode</span>
        </div>
        <div class="page-subtitle">
          Record commodities purchased by the shop through a broker. Auto-applies configured brokerage rules.
        </div>
      </div>

      <div style="display: flex; gap: 8px;">
        <router-link to="/registers?type=Purchase" class="btn btn-secondary btn-sm">
          📋 Purchase Register (<kbd>Alt+L</kbd>)
        </router-link>
      </div>
    </div>

    <form @submit.prevent="promptSubmit">
      <!-- Row 1: Header Meta -->
      <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr; margin-bottom: 16px;">
        <div class="form-group">
          <label>Entry Date *</label>
          <input v-model="form.posting_date" type="date" required @change="onDateChange" />
        </div>

        <div class="form-group">
          <label>Company</label>
          <input type="text" :value="bootState.defaultCompany" readonly />
        </div>

        <div class="form-group">
          <label>Broker (Purchase Applicable) *</label>
          <TypeaheadSelect
            v-model="form.broker"
            :label="form.broker_name"
            placeholder="Search Purchase Broker..."
            :fetch-fn="searchPurchaseBrokers"
            @change="onBrokerSelected"
          />
        </div>
      </div>

      <!-- Row 2: Parties & Item -->
      <div class="form-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 20px;">
        <div class="form-group">
          <label>Supplier (Seller to Shop) *</label>
          <TypeaheadSelect
            v-model="form.supplier"
            :label="form.supplier_name"
            placeholder="Search Supplier..."
            :fetch-fn="searchSuppliers"
            @change="(s) => { if(s) form.supplier_name = s.label || s.name }"
          />
        </div>

        <div class="form-group">
          <label>Commodity / Item *</label>
          <TypeaheadSelect
            v-model="form.item"
            :label="form.item_name"
            placeholder="Search Commodity..."
            :fetch-fn="searchItems"
            @change="onItemSelected"
          />
        </div>
      </div>

      <!-- Auto-Fetch Rule Notice Banner -->
      <div v-if="appliedRuleNotice" class="notice-banner notice-success">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 16px;">⚡</span>
          <span><strong>Auto-Fetched Broker Rule:</strong> {{ appliedRuleNotice }}</span>
        </div>
        <span class="badge badge-green">Editable Override Allowed</span>
      </div>

      <!-- Row 3: Quantity, Bags & Trade Rate -->
      <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr 1fr; margin-bottom: 20px; background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid var(--border);">
        <div class="form-group">
          <label>Quantity (Qtl) *</label>
          <input
            v-model.number="form.quantity"
            type="number"
            step="0.01"
            min="0.01"
            required
            @input="onQuantityInput"
          />
        </div>

        <div class="form-group">
          <label>Number of Bags</label>
          <input
            v-model.number="form.bags"
            type="number"
            step="1"
            min="0"
            @input="onBagsInput"
          />
        </div>

        <div class="form-group">
          <label>Rate per Qtl (₹) *</label>
          <input
            v-model.number="form.rate"
            type="number"
            step="0.01"
            min="0"
            required
            @input="recalculate"
          />
        </div>

        <div class="form-group">
          <label>Total Trade Amount (₹)</label>
          <input
            type="text"
            :value="formatCurrency(calculatedTradeAmount)"
            readonly
            style="font-weight: 700; color: #1e3a8a;"
          />
        </div>
      </div>

      <!-- Brokerage Calculation Section -->
      <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <div style="font-weight: 700; font-size: 14px; color: #0f172a;">
            💼 Brokerage Calculation Method &amp; Rate
          </div>
          <span class="badge badge-blue">Selected: {{ form.brokerage_method }}</span>
        </div>

        <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr 1fr; align-items: end;">
          <div class="form-group">
            <label>Brokerage Method *</label>
            <select v-model="form.brokerage_method" @change="onMethodChanged">
              <option value="Percentage">Percentage (%)</option>
              <option value="Per Bag">Per Bag (₹ / Bag)</option>
              <option value="Per Quintal">Per Quintal (₹ / Qtl)</option>
            </select>
          </div>

          <!-- Mode 1: Percentage -->
          <div v-if="form.brokerage_method === 'Percentage'" class="form-group">
            <label>Brokerage Percentage (%) *</label>
            <input
              v-model.number="form.percentage"
              type="number"
              step="0.01"
              min="0"
              required
              @input="recalculate"
            />
          </div>

          <!-- Mode 2: Per Bag -->
          <div v-else-if="form.brokerage_method === 'Per Bag'" class="form-group">
            <label>Rate per Bag (₹) *</label>
            <input
              v-model.number="form.per_bag"
              type="number"
              step="0.01"
              min="0"
              required
              @input="recalculate"
            />
          </div>

          <!-- Mode 3: Per Quintal -->
          <div v-else-if="form.brokerage_method === 'Per Quintal'" class="form-group">
            <label>Rate per Quintal (₹) *</label>
            <input
              v-model.number="form.per_quintal"
              type="number"
              step="0.01"
              min="0"
              required
              @input="recalculate"
            />
          </div>

          <!-- Formula display -->
          <div class="form-group" style="grid-column: span 2;">
            <label>Formula Calculation Breakdown</label>
            <div style="padding: 8px 12px; background: #f8fafc; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; color: #475569; font-family: var(--font-mono);">
              <span v-if="form.brokerage_method === 'Percentage'">
                ₹{{ formatCurrency(calculatedTradeAmount) }} × {{ form.percentage || 0 }}% =
              </span>
              <span v-else-if="form.brokerage_method === 'Per Bag'">
                {{ form.bags || 0 }} Bags × ₹{{ form.per_bag || 0 }}/Bag =
              </span>
              <span v-else-if="form.brokerage_method === 'Per Quintal'">
                {{ form.quantity || 0 }} Qtl × ₹{{ form.per_quintal || 0 }}/Qtl =
              </span>
              <strong style="color: #059669; font-size: 14px; margin-left: 6px;">
                ₹{{ formatCurrency(calculatedBrokerageAmount) }}
              </strong>
            </div>
          </div>
        </div>

        <!-- Net Summary Box -->
        <div style="margin-top: 14px; padding: 12px 16px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 700;">Calculated Brokerage Amount</div>
            <div style="font-size: 22px; font-weight: 800; color: #15803d;">
              ₹ {{ formatCurrency(calculatedBrokerageAmount) }}
            </div>
          </div>

          <div style="text-align: right;">
            <div style="font-size: 11px; text-transform: uppercase; color: #1e3a8a; font-weight: 700;">Total Trade Value</div>
            <div style="font-size: 20px; font-weight: 800; color: #1e40af;">
              ₹ {{ formatCurrency(calculatedTradeAmount) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Remarks -->
      <div class="form-group" style="margin-bottom: 24px;">
        <label>Remarks / Contract Notes</label>
        <textarea v-model="form.remarks" rows="2" placeholder="Optional notes..."></textarea>
      </div>

      <!-- Action Buttons -->
      <div style="display: flex; justify-content: flex-end; gap: 12px; align-items: center;">
        <button type="button" class="btn btn-secondary" @click="resetForm">
          Reset Form
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting" style="padding: 10px 24px; font-size: 14px;">
          {{ isSubmitting ? 'Saving...' : '💾 Submit Purchase Entry' }}
          <kbd style="background: rgba(255,255,255,0.25); color: #fff; border: none;">Ctrl+Enter</kbd>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import TypeaheadSelect from '../components/TypeaheadSelect.vue'

const router = useRouter()
const { searchEntities, getBrokerItemRate, savePurchaseEntry } = useFrappeApi()

const isSubmitting = ref(false)
const appliedRuleNotice = ref('')

const form = reactive({
  posting_date: bootState.today || new Date().toISOString().split('T')[0],
  broker: '',
  broker_name: '',
  supplier: '',
  supplier_name: '',
  item: '',
  item_name: '',
  quantity: 100,
  bags: 200,
  rate: 3800,
  brokerage_method: 'Percentage',
  brokerage_rate: 1.0,
  percentage: 1.0,
  per_bag: 0,
  per_quintal: 0,
  rate_source: '',
  remarks: '',
})

const calculatedTradeAmount = computed(() => {
  return Math.round((Number(form.quantity) || 0) * (Number(form.rate) || 0) * 100) / 100
})

const calculatedBrokerageAmount = computed(() => {
  const method = form.brokerage_method
  const tradeAmt = calculatedTradeAmount.value
  const qty = Number(form.quantity) || 0
  const bags = Number(form.bags) || (qty * 2.0)

  if (method === 'Percentage') {
    const pct = Number(form.percentage) || 0
    return Math.round((tradeAmt * (pct / 100.0)) * 100) / 100
  } else if (method === 'Per Bag') {
    const bagRate = Number(form.per_bag) || 0
    return Math.round((bags * bagRate) * 100) / 100
  } else if (method === 'Per Quintal') {
    const qtlRate = Number(form.per_quintal) || 0
    return Math.round((qty * qtlRate) * 100) / 100
  }
  return 0
})

const searchPurchaseBrokers = async (q) => {
  return await searchEntities('Broker', q, { for_purchase: 1 })
}

const searchSuppliers = async (q) => {
  return await searchEntities('Supplier', q)
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
}

const onBrokerSelected = (item) => {
  if (item) {
    form.broker_name = item.label || item.name
    triggerAutoRateFetch()
  } else {
    form.broker = ''
    form.broker_name = ''
    appliedRuleNotice.value = ''
  }
}

const onItemSelected = (item) => {
  if (item) {
    form.item_name = item.label || item.name
    triggerAutoRateFetch()
  } else {
    form.item = ''
    form.item_name = ''
    appliedRuleNotice.value = ''
  }
}

const onDateChange = () => {
  triggerAutoRateFetch()
}

// Core Requirement: Auto-fetch broker rule for Item A & Broker
const triggerAutoRateFetch = async () => {
  if (!form.broker || !form.item) return

  try {
    const res = await getBrokerItemRate(form.broker, form.item, 'Purchase', form.posting_date)
    if (res && res.found) {
      form.brokerage_method = res.brokerage_method
      form.brokerage_rate = res.rate
      form.percentage = res.percentage || 0
      form.per_bag = res.per_bag || 0
      form.per_quintal = res.per_quintal || 0
      form.rate_source = res.source

      const symbol = res.brokerage_method === 'Percentage' ? `${res.rate}%` : (res.brokerage_method === 'Per Bag' ? `₹${res.rate}/bag` : `₹${res.rate}/qtl`)
      appliedRuleNotice.value = `${res.brokerage_method} @ ${symbol} (${res.source})`
    } else {
      appliedRuleNotice.value = ''
    }
  } catch (e) {
    console.error('Failed to auto-fetch broker rate:', e)
  }
}

// Vice-versa bags <-> quantity
const onQuantityInput = () => {
  form.bags = Math.round(Number(form.quantity || 0) * 2.0)
}

const onBagsInput = () => {
  form.quantity = Math.round((Number(form.bags || 0) / 2.0) * 100) / 100
}

const onMethodChanged = () => {
  if (form.brokerage_method === 'Percentage') {
    if (!form.percentage) form.percentage = 1.0
  } else if (form.brokerage_method === 'Per Bag') {
    if (!form.per_bag) form.per_bag = 10.0
  } else if (form.brokerage_method === 'Per Quintal') {
    if (!form.per_quintal) form.per_quintal = 20.0
  }
}

const recalculate = () => {
  // Triggers reactivity
}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const resetForm = () => {
  form.broker = ''
  form.broker_name = ''
  form.supplier = ''
  form.supplier_name = ''
  form.item = ''
  form.item_name = ''
  form.quantity = 100
  form.bags = 200
  form.rate = 3800
  form.brokerage_method = 'Percentage'
  form.percentage = 1.0
  form.per_bag = 0
  form.per_quintal = 0
  form.remarks = ''
  appliedRuleNotice.value = ''
}

const promptSubmit = async () => {
  if (!form.broker) {
    alert('Please select a purchase broker.')
    return
  }
  if (!form.supplier) {
    alert('Please select a supplier.')
    return
  }
  if (!form.item) {
    alert('Please select a commodity/item.')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      posting_date: form.posting_date,
      company: bootState.defaultCompany,
      broker: form.broker,
      supplier: form.supplier,
      item: form.item,
      quantity: form.quantity,
      bags: form.bags,
      rate: form.rate,
      brokerage_method: form.brokerage_method,
      brokerage_rate: form.brokerage_method === 'Percentage' ? form.percentage : (form.brokerage_method === 'Per Bag' ? form.per_bag : form.per_quintal),
      percentage: form.percentage,
      per_bag: form.per_bag,
      per_quintal: form.per_quintal,
      rate_source: form.rate_source || 'Purchase Entry',
      remarks: form.remarks,
      submit: true,
    }

    const res = await savePurchaseEntry(payload)
    alert(`✅ Purchase Entry ${res.name} submitted successfully! Total Brokerage: ₹${formatCurrency(res.brokerage_amount)}`)
    resetForm()
    router.push('/registers?type=Purchase')
  } catch (e) {
    alert('Submission failed: ' + e.message)
  } finally {
    isSubmitting.value = false
  }
}

// Global keyboard shortcut: Ctrl+Enter to submit
onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      promptSubmit()
    }
  })
})
</script>
