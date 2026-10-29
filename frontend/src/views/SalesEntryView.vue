<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="content-card">
        <div class="page-header">
          <div>
            <div class="page-title">
              <span>🏷️ Sell Voucher (Broker Trade)</span>
              <span class="badge badge-green">Sell Mode</span>
            </div>
            <div class="page-subtitle">
              Supplier &amp; Buyer are one entity: <strong>Broker</strong>. Showing only brokers where <strong>[Sell]</strong> checkpoint is ON.
            </div>
          </div>

          <!-- Quick Toggle between Purchase & Sell -->
          <div style="display: flex; gap: 8px; align-items: center;">
            <div style="background: var(--panel-soft); padding: 3px; border-radius: 6px; border: 1px solid var(--line); display: inline-flex; gap: 4px;">
              <router-link
                to="/purchase"
                class="btn btn-sm"
                style="background: transparent; color: var(--muted); font-weight: 600;"
              >
                🛒 Purchase (<kbd>F9</kbd>)
              </router-link>
              <button
                type="button"
                class="btn btn-sm"
                style="background: var(--green); color: #fff; font-weight: 700;"
              >
                🏷️ Sell (<kbd style="background: rgba(255,255,255,0.25); color: #fff; border: none;">F8</kbd>)
              </button>
            </div>

            <router-link to="/registers?type=Sales" class="btn btn-secondary btn-sm">
              📋 Register (<kbd>S</kbd>)
            </router-link>
          </div>
        </div>

        <form @submit.prevent="promptSubmit">
          <!-- Row 1: Header Meta & The Sole Entity: Broker -->
          <div class="form-grid" style="grid-template-columns: 1fr 1fr 2fr; margin-bottom: 16px;">
            <div class="form-group">
              <label>Voucher Date *</label>
              <input
                ref="postingDateInput"
                v-model="form.posting_date"
                type="date"
                required
                @change="onDateChange"
                @keydown.enter.prevent="focusField('broker')"
              />
            </div>

            <div class="form-group">
              <label>Company</label>
              <input type="text" :value="bootState.defaultCompany" readonly />
            </div>

            <!-- Single Entity Field: Broker (Sell) -->
            <div class="form-group">
              <label style="display: flex; justify-content: space-between; align-items: center;">
                <span>Broker Name (Sell Entity) *</span>
                <span class="badge badge-green" style="font-size: 10px;">✓ Filter: Sell Checkbox ON</span>
              </label>
              <TypeaheadSelect
                ref="brokerSelect"
                v-model="form.broker"
                :label="form.broker_name"
                placeholder="Click or Enter to select Sell Broker..."
                :fetch-fn="searchSellBrokers"
                @change="onBrokerSelected"
                @enter="focusField('item')"
              />
            </div>
          </div>

          <!-- Row 2: Commodity Selection & Stock Group -->
          <div class="form-grid" style="grid-template-columns: 2fr 1fr; margin-bottom: 16px;">
            <div class="form-group">
              <label>Commodity / Item *</label>
              <TypeaheadSelect
                ref="itemSelect"
                v-model="form.item"
                :label="form.item_name"
                placeholder="Search Commodity / Item..."
                :fetch-fn="searchItems"
                @change="onItemSelected"
                @enter="focusField('quantity')"
              />
            </div>

            <div class="form-group">
              <label>Stock Group &amp; Role</label>
              <div style="padding: 7px 12px; background: var(--green-soft); border: 1px solid var(--green); border-radius: 4px; font-size: 12.5px; font-weight: 600; color: var(--green); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span>🏷️ Sell Broker</span>
                <span v-if="form.stock_group" class="badge badge-purple" style="font-size: 11px;">
                  🏷️ Group: {{ form.stock_group }}
                </span>
              </div>
            </div>
          </div>

          <!-- Auto-Fetch Rule Notice Banner -->
          <div v-if="appliedRuleNotice" class="notice-banner notice-success">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 16px;">⚡</span>
              <span><strong>Auto-Fetched Broker Terms:</strong> {{ appliedRuleNotice }}</span>
            </div>
            <span class="badge badge-green">Stock Group Rule Applied</span>
          </div>

          <!-- Row 3: Quantity, Bags & Trade Rate -->
          <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr 1fr; margin-bottom: 16px; background: var(--panel-soft); padding: 14px; border-radius: 6px; border: 1px solid var(--line);">
            <div class="form-group">
              <label>Quantity (Qtl) *</label>
              <input
                ref="quantityInput"
                v-model.number="form.quantity"
                type="number"
                step="0.01"
                min="0.01"
                required
                @input="onQuantityInput"
                @keydown.enter.prevent="focusField('bags')"
              />
            </div>

            <div class="form-group">
              <label>Number of Bags</label>
              <input
                ref="bagsInput"
                v-model.number="form.bags"
                type="number"
                step="1"
                min="0"
                @input="onBagsInput"
                @keydown.enter.prevent="focusField('rate')"
              />
            </div>

            <div class="form-group">
              <label>Rate per Qtl (₹) *</label>
              <input
                ref="rateInput"
                v-model.number="form.rate"
                type="number"
                step="0.01"
                min="0"
                required
                @input="recalculate"
                @keydown.enter.prevent="focusField('gstRate')"
              />
            </div>

            <div class="form-group">
              <label>Trade Subtotal (₹)</label>
              <input
                type="text"
                :value="formatCurrency(calculatedTradeAmount)"
                readonly
                style="font-weight: 700; color: var(--navy); background: var(--panel-soft);"
              />
            </div>
          </div>

          <!-- Row 3b: GST Calculation (CGST + SGST) -->
          <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr 1.3fr; margin-bottom: 18px; background: #f0fdf4; padding: 14px 16px; border-radius: 6px; border: 1px solid #bbf7d0;">
            <div class="form-group">
              <label style="color: #166534; font-weight: 700;">GST Rate (%) *</label>
              <div style="position: relative; display: flex; align-items: center;">
                <input
                  ref="gstRateInput"
                  v-model.number="form.gst_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  required
                  style="font-weight: 700; color: #166534; padding-right: 24px; background: #fff;"
                  @keydown.enter.prevent="focusField('method')"
                />
                <span style="position: absolute; right: 10px; font-weight: 700; color: #166534;">%</span>
              </div>
            </div>

            <div class="form-group">
              <label style="color: #166534;">CGST ({{ calculatedCgstRate }}%)</label>
              <input
                type="text"
                :value="'₹ ' + formatCurrency(calculatedCgstAmount)"
                readonly
                style="background: #fff; font-weight: 600; color: #166534;"
              />
            </div>

            <div class="form-group">
              <label style="color: #166534;">SGST ({{ calculatedSgstRate }}%)</label>
              <input
                type="text"
                :value="'₹ ' + formatCurrency(calculatedSgstAmount)"
                readonly
                style="background: #fff; font-weight: 600; color: #166534;"
              />
            </div>

            <div class="form-group">
              <label style="color: #166534; font-weight: 700;">Invoice Grand Total (₹)</label>
              <input
                type="text"
                :value="'₹ ' + formatCurrency(calculatedGrandTotal)"
                readonly
                style="background: #dcfce7; font-weight: 800; color: #14532d; font-size: 14px;"
              />
            </div>
          </div>

          <!-- Brokerage Calculation Section -->
          <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 16px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <div style="font-weight: 700; font-size: 13.5px; color: var(--navy);">
                💼 Brokerage Calculation Method &amp; Rate
              </div>
              <span class="badge badge-green">Method: {{ form.brokerage_method }}</span>
            </div>

            <div class="form-grid" style="grid-template-columns: 1fr 1fr 2fr; align-items: end;">
              <div class="form-group">
                <label>Brokerage Method *</label>
                <select
                  ref="methodSelect"
                  v-model="form.brokerage_method"
                  @change="onMethodChanged"
                  @keydown.enter.prevent="focusField('rateValue')"
                >
                  <option value="Percentage">Percentage (%)</option>
                  <option value="Per Bag">Per Bag (₹ / Bag)</option>
                  <option value="Per Quintal">Per Quintal (₹ / Qtl)</option>
                </select>
              </div>

              <!-- Mode 1: Percentage -->
              <div v-if="form.brokerage_method === 'Percentage'" class="form-group">
                <label>Brokerage Percentage (%) *</label>
                <input
                  ref="rateValueInput"
                  v-model.number="form.percentage"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  @input="recalculate"
                  @keydown.enter.prevent="focusField('remarks')"
                />
              </div>

              <!-- Mode 2: Per Bag -->
              <div v-else-if="form.brokerage_method === 'Per Bag'" class="form-group">
                <label>Rate per Bag (₹) *</label>
                <input
                  ref="rateValueInput"
                  v-model.number="form.per_bag"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  @input="recalculate"
                  @keydown.enter.prevent="focusField('remarks')"
                />
              </div>

              <!-- Mode 3: Per Quintal -->
              <div v-else-if="form.brokerage_method === 'Per Quintal'" class="form-group">
                <label>Rate per Quintal (₹) *</label>
                <input
                  ref="rateValueInput"
                  v-model.number="form.per_quintal"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  @input="recalculate"
                  @keydown.enter.prevent="focusField('remarks')"
                />
              </div>

              <!-- Formula display -->
              <div class="form-group">
                <label>Formula Calculation Breakdown</label>
                <div style="padding: 7px 12px; background: var(--panel-soft); border: 1px solid var(--line); border-radius: 4px; font-size: 12.5px; color: var(--muted); font-family: var(--font-mono);">
                  <span v-if="form.brokerage_method === 'Percentage'">
                    ₹{{ formatCurrency(calculatedTradeAmount) }} × {{ form.percentage || 0 }}% =
                  </span>
                  <span v-else-if="form.brokerage_method === 'Per Bag'">
                    {{ form.bags || 0 }} Bags × ₹{{ form.per_bag || 0 }}/Bag =
                  </span>
                  <span v-else-if="form.brokerage_method === 'Per Quintal'">
                    {{ form.quantity || 0 }} Qtl × ₹{{ form.per_quintal || 0 }}/Qtl =
                  </span>
                  <strong style="color: var(--green); font-size: 13.5px; margin-left: 6px;">
                    ₹{{ formatCurrency(calculatedBrokerageAmount) }}
                  </strong>
                </div>
              </div>
            </div>

            <!-- Net Summary Box (Tally Invoice Style) -->
            <div style="margin-top: 14px; padding: 14px 18px; background: var(--green-soft); border: 1px solid rgba(27, 135, 63, 0.2); border-radius: 6px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; align-items: center;">
              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: var(--navy); font-weight: 700;">Trade Subtotal</div>
                <div style="font-size: 16px; font-weight: 800; color: var(--navy);">
                  ₹ {{ formatCurrency(calculatedTradeAmount) }}
                </div>
              </div>

              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 700;">Total GST (CGST+SGST)</div>
                <div style="font-size: 16px; font-weight: 800; color: #166534;">
                  ₹ {{ formatCurrency(calculatedTotalGstAmount) }}
                </div>
              </div>

              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: var(--blue); font-weight: 700;">Grand Invoice Total</div>
                <div style="font-size: 18px; font-weight: 800; color: var(--blue);">
                  ₹ {{ formatCurrency(calculatedGrandTotal) }}
                </div>
              </div>

              <div style="text-align: right;">
                <div style="font-size: 11px; text-transform: uppercase; color: var(--green); font-weight: 700;">Brokerage Receivable</div>
                <div style="font-size: 18px; font-weight: 800; color: var(--green);">
                  ₹ {{ formatCurrency(calculatedBrokerageAmount) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Remarks -->
          <div class="form-group" style="margin-bottom: 20px;">
            <label>Remarks / Notes (Enter on this field prompts Accept Voucher)</label>
            <textarea
              ref="remarksInput"
              v-model="form.remarks"
              rows="2"
              placeholder="Trade terms, station, or delivery remarks... (Press Enter to Accept)"
              @keydown.enter.prevent="promptSubmit"
            ></textarea>
          </div>

          <!-- Action Buttons -->
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <button type="button" class="btn btn-secondary" @click="resetForm">
              Reset Form
            </button>
            <div style="display: flex; gap: 10px; align-items: center;">
              <button type="button" class="btn btn-secondary" @click="router.push('/')">
                Cancel (Esc)
              </button>
              <button type="button" class="btn btn-success" :disabled="isSubmitting" @click="promptSubmit">
                <span>{{ isSubmitting ? 'Saving...' : '💾 Accept Voucher' }}</span>
                <kbd style="background: rgba(255,255,255,0.25); color: #fff; border-color: rgba(255,255,255,0.4);">Enter</kbd>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Sales Voucher (F8)"
      :items="menuItems"
      :active-index="1"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import { openConfirm, showToast, openGlobalBrokerModal, openGlobalRateModal } from '../composables/useKeyboardEngine'
import TypeaheadSelect from '../components/TypeaheadSelect.vue'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { searchEntities, getBrokerItemRate, saveSalesEntry } = useFrappeApi()

// Field refs for Enter traversal
const postingDateInput = ref(null)
const brokerSelect = ref(null)
const itemSelect = ref(null)
const quantityInput = ref(null)
const bagsInput = ref(null)
const rateInput = ref(null)
const gstRateInput = ref(null)
const methodSelect = ref(null)
const rateValueInput = ref(null)
const remarksInput = ref(null)

const isSubmitting = ref(false)
const appliedRuleNotice = ref('')

const form = reactive({
  posting_date: bootState.today || new Date().toISOString().split('T')[0],
  broker: '',
  broker_name: '',
  item: '',
  item_name: '',
  stock_group: 'Sugar',
  stock_group_name: 'Sugar',
  quantity: 50,
  bags: 100,
  rate: 3950,
  gst_rate: 5.0,
  brokerage_method: 'Percentage',
  brokerage_rate: 1.0,
  percentage: 1.0,
  per_bag: 0,
  per_quintal: 0,
  rate_source: '',
  remarks: '',
})

// Tally Enter-based focus navigation
const focusField = (fieldName) => {
  const map = {
    date: postingDateInput,
    broker: brokerSelect,
    item: itemSelect,
    quantity: quantityInput,
    bags: bagsInput,
    rate: rateInput,
    gstRate: gstRateInput,
    method: methodSelect,
    rateValue: rateValueInput,
    remarks: remarksInput,
  }
  const target = map[fieldName]
  if (target && target.value) {
    nextTick(() => {
      if (typeof target.value.focus === 'function') {
        target.value.focus()
      } else if (target.value.$el && typeof target.value.$el.focus === 'function') {
        target.value.$el.focus()
      }
    })
  }
}

const calculatedTradeAmount = computed(() => {
  return Math.round((Number(form.quantity) || 0) * (Number(form.rate) || 0) * 100) / 100
})

const calculatedCgstRate = computed(() => {
  return Math.round(((Number(form.gst_rate) || 0) / 2.0) * 100) / 100
})

const calculatedSgstRate = computed(() => {
  return Math.round(((Number(form.gst_rate) || 0) / 2.0) * 100) / 100
})

const calculatedCgstAmount = computed(() => {
  return Math.round((calculatedTradeAmount.value * (calculatedCgstRate.value / 100.0)) * 100) / 100
})

const calculatedSgstAmount = computed(() => {
  return Math.round((calculatedTradeAmount.value * (calculatedSgstRate.value / 100.0)) * 100) / 100
})

const calculatedTotalGstAmount = computed(() => {
  return Math.round((calculatedCgstAmount.value + calculatedSgstAmount.value) * 100) / 100
})

const calculatedGrandTotal = computed(() => {
  return Math.round((calculatedTradeAmount.value + calculatedTotalGstAmount.value) * 100) / 100
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

// STRICT FILTER: Returns ONLY brokers where applicable_for_sales == 1
const searchSellBrokers = async (q) => {
  return await searchEntities('Brokers', q, { for_sales: 1 })
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
}

const onBrokerSelected = (item) => {
  if (item) {
    form.broker_name = item.label || item.broker_name || item.name
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
    if (item.stock_group) {
      form.stock_group = item.stock_group
      form.stock_group_name = item.stock_group
    }
    if (item.gst_rate !== undefined && item.gst_rate !== null) {
      form.gst_rate = item.gst_rate
    }
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

// Auto-fetch broker rule for Sell by Stock Group
const triggerAutoRateFetch = async () => {
  if (!form.broker || !form.item) return

  try {
    const res = await getBrokerItemRate(form.broker, form.item, form.stock_group, 'Sell', form.posting_date)
    if (res) {
      if (res.stock_group) {
        form.stock_group = res.stock_group
        form.stock_group_name = res.stock_group_name || res.stock_group
      }
      if (res.gst_rate !== undefined && res.gst_rate !== null) {
        form.gst_rate = res.gst_rate
      }

      if (res.found) {
        form.brokerage_method = res.brokerage_method
        form.brokerage_rate = res.rate
        form.percentage = res.percentage || 0
        form.per_bag = res.per_bag || 0
        form.per_quintal = res.per_quintal || 0
        form.rate_source = res.source

        const symbol = res.brokerage_method === 'Percentage' ? `${res.rate}%` : (res.brokerage_method === 'Per Bag' ? `₹${res.rate}/bag` : `₹${res.rate}/qtl`)
        appliedRuleNotice.value = `${res.brokerage_method} @ ${symbol} [Group: ${res.stock_group_name || res.stock_group}] (${res.source})`
      } else {
        appliedRuleNotice.value = ''
      }
    }
  } catch (e) {
    console.error('Failed to auto-fetch broker sell rate:', e)
  }
}

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

const recalculate = () => {}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const resetForm = () => {
  form.broker = ''
  form.broker_name = ''
  form.item = ''
  form.item_name = ''
  form.stock_group = 'Sugar'
  form.stock_group_name = 'Sugar'
  form.quantity = 50
  form.bags = 100
  form.rate = 3950
  form.gst_rate = 5.0
  form.brokerage_method = 'Percentage'
  form.percentage = 1.0
  form.per_bag = 0
  form.per_quintal = 0
  form.remarks = ''
  appliedRuleNotice.value = ''
}

const promptSubmit = () => {
  if (!form.broker) {
    showToast('Please select a Sell Broker')
    focusField('broker')
    return
  }
  if (!form.item) {
    showToast('Please select a Commodity/Item')
    focusField('item')
    return
  }
  if (!form.quantity || form.quantity <= 0) {
    showToast('Please enter a valid Quantity')
    focusField('quantity')
    return
  }
  if (!form.rate || form.rate <= 0) {
    showToast('Please enter a valid Rate')
    focusField('rate')
    return
  }

  const title = 'Accept Sales Voucher?'
  const body = `Record Sales of ${form.quantity} Qtl @ ₹${form.rate} (Grand Total: ₹${formatCurrency(calculatedGrandTotal.value)} incl GST ${form.gst_rate}%, Brokerage: ₹${formatCurrency(calculatedBrokerageAmount.value)}) for Broker ${form.broker_name || form.broker}?`
  openConfirm(title, body, submitEntry)
}

const submitEntry = async () => {
  isSubmitting.value = true
  try {
    const payload = {
      posting_date: form.posting_date,
      company: bootState.defaultCompany,
      broker: form.broker,
      broker_name: form.broker_name,
      item: form.item,
      stock_group: form.stock_group,
      quantity: form.quantity,
      bags: form.bags,
      rate: form.rate,
      gst_rate: form.gst_rate,
      cgst_rate: calculatedCgstRate.value,
      cgst_amount: calculatedCgstAmount.value,
      sgst_rate: calculatedSgstRate.value,
      sgst_amount: calculatedSgstAmount.value,
      total_gst_amount: calculatedTotalGstAmount.value,
      grand_total: calculatedGrandTotal.value,
      brokerage_method: form.brokerage_method,
      brokerage_rate: form.brokerage_method === 'Percentage' ? form.percentage : (form.brokerage_method === 'Per Bag' ? form.per_bag : form.per_quintal),
      percentage: form.percentage,
      per_bag: form.per_bag,
      per_quintal: form.per_quintal,
      rate_source: form.rate_source || 'Sell Entry',
      remarks: form.remarks,
      submit: true,
    }

    const res = await saveSalesEntry(payload)
    showToast(`✅ Sales Voucher ${res.name} accepted & saved!`)
    resetForm()
    router.push('/registers?type=Sales')
  } catch (e) {
    showToast('Submission failed: ' + e.message, 4000)
  } finally {
    isSubmitting.value = false
  }
}

// Right-Side Gateway Menu Items for Sales View
const menuItems = [
  { isHeader: true, label: '⚡ VOUCHER ACTIONS' },
  { key: 'Enter', label: 'Accept Voucher (Save)', action: () => promptSubmit() },
  { key: 'F9', label: 'Switch to Purchase Voucher', action: () => router.push('/purchase') },
  { key: 'Esc', label: 'Gateway of Brokerage', action: () => router.push('/') },

  { isHeader: true, label: '📋 REGISTERS' },
  { key: 'O', label: 'Sales Outstandings (Due)', action: () => router.push('/registers?type=SalesOutstanding') },
  { key: 'S', label: 'Sales Register', action: () => router.push('/registers?type=Sales') },
  { key: 'P', label: 'Purchase Register', action: () => router.push('/registers?type=Purchase') },
  { key: 'L', label: 'All Registers', action: () => router.push('/registers') },

  { isHeader: true, label: '🏢 MASTERS' },
  { key: 'I', label: 'Commodity & Stock Groups', action: () => router.push('/items') },
  { key: 'B', label: '+ New Broker (Full Screen)', action: () => openGlobalBrokerModal('') },
  { key: 'R', label: 'Date-Wise Rate Cards', action: () => router.push('/rate-configs') },
]

const handleSelect = (idx) => {
  if (menuItems[idx].isHeader) return
  menuItems[idx].action()
}

onMounted(() => {
  nextTick(() => {
    if (postingDateInput.value) postingDateInput.value.focus()
  })
})
</script>
