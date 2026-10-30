<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="content-card">
        <div class="page-header">
          <div>
            <div class="page-title">
              <span>🛒 Purchase Voucher (Broker Trade)</span>
              <span class="badge badge-blue">Purchase Mode</span>
              <span class="badge badge-purple" style="font-size: 11px;">Multi-Item Supported</span>
            </div>
            <div class="page-subtitle">
              Supplier &amp; Buyer are one entity: <strong>Broker</strong>. Showing only brokers where <strong>[Purchase]</strong> checkpoint is ON.
            </div>
          </div>

          <!-- Quick Toggle between Purchase & Sell -->
          <div style="display: flex; gap: 8px; align-items: center;">
            <div style="background: var(--panel-soft); padding: 3px; border-radius: 6px; border: 1px solid var(--line); display: inline-flex; gap: 4px;">
              <button
                type="button"
                class="btn btn-sm"
                style="background: var(--blue); color: #fff; font-weight: 700;"
              >
                🛒 Purchase (<kbd style="background: rgba(255,255,255,0.25); color: #fff; border: none;">F9</kbd>)
              </button>
              <router-link
                to="/sell"
                class="btn btn-sm"
                style="background: transparent; color: var(--muted); font-weight: 600;"
              >
                🏷️ Sell (<kbd>F8</kbd>)
              </router-link>
            </div>

            <router-link to="/registers?type=Purchase" class="btn btn-secondary btn-sm">
              📋 Register (<kbd>P</kbd>)
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
                @keydown.enter.prevent="focusBroker"
              />
            </div>

            <div class="form-group">
              <label>Company</label>
              <input type="text" :value="bootState.defaultCompany" readonly />
            </div>

            <!-- Single Entity Field: Broker (Purchase) -->
            <div class="form-group">
              <label style="display: flex; justify-content: space-between; align-items: center;">
                <span>Broker Name (Purchase Entity) *</span>
                <span class="badge badge-blue" style="font-size: 10px;">✓ Filter: Purchase Checkbox ON</span>
              </label>
              <TypeaheadSelect
                ref="brokerSelect"
                v-model="form.broker"
                :label="form.broker_name"
                placeholder="Click or Enter to select Purchase Broker..."
                :fetch-fn="searchPurchaseBrokers"
                @change="onBrokerSelected"
                @enter="focusFirstItem"
              />
            </div>

            <!-- Optional Party Name & Bill/Ref No for Purchase Register -->
            <div class="form-group">
              <label>Supplier / Party Name (Optional)</label>
              <input
                v-model="form.party_name"
                type="text"
                placeholder="e.g. AIRINOX TECHNOLOGIES, SHRI SAI SHANAY"
              />
            </div>

            <div class="form-group">
              <label>Bill / Ref No (Optional)</label>
              <input
                v-model="form.ref_no"
                type="text"
                placeholder="e.g. CBD/25-260013, 11, 12"
              />
            </div>
          </div>

          <!-- Section: Multi-Item Commodity Grid -->
          <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 14px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-weight: 700; font-size: 13.5px; color: var(--navy);">
                  📦 Commodity Line Items ({{ items.length }})
                </span>
                <span class="badge badge-blue" style="font-size: 11px;">Multi-Commodity Voucher</span>
              </div>
              <button
                type="button"
                class="btn btn-sm btn-primary"
                style="font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;"
                @click="addRow"
              >
                <span>➕ Add Commodity / Item</span>
                <kbd style="background: rgba(255,255,255,0.25); color: #fff; border: none; font-size: 10px;">Alt+A</kbd>
              </button>
            </div>

            <!-- Items Table -->
            <div style="min-height: 320px; overflow: visible; position: relative; border: 1px solid var(--line); border-radius: 6px; background: #fff;">
              <table class="data-table" style="width: 100%; border-collapse: separate; border-spacing: 0; font-size: 12px;">
                <thead style="background: var(--panel-soft);">
                  <tr>
                    <th style="width: 32px; text-align: center;">#</th>
                    <th style="min-width: 220px;">Commodity / Item *</th>
                    <th style="min-width: 100px;">Group</th>
                    <th style="width: 105px; text-align: right;">Qty (Qtl) *</th>
                    <th style="width: 85px; text-align: right;">Bags</th>
                    <th style="width: 110px; text-align: right;">Rate (₹) *</th>
                    <th style="width: 120px; text-align: right;">Trade (₹)</th>
                    <th style="width: 80px; text-align: right;">GST %</th>
                    <th style="min-width: 190px;">Brokerage Terms *</th>
                    <th style="width: 110px; text-align: right;">Brokerage (₹)</th>
                    <th style="width: 44px; text-align: center;">✕</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in items" :key="row.id" style="border-bottom: 1px solid var(--line); position: relative;">
                    <td style="text-align: center; color: var(--muted); font-weight: 700; vertical-align: middle;">
                      {{ idx + 1 }}
                    </td>

                    <!-- Commodity Selector -->
                    <td style="vertical-align: middle; padding: 6px 8px; position: relative; overflow: visible;">
                      <TypeaheadSelect
                        v-model="row.item"
                        :label="row.item_name"
                        placeholder="Search item..."
                        :fetch-fn="searchItems"
                        @change="(val) => onRowItemSelected(row, val)"
                        @enter="() => focusRowField(idx, 'quantity')"
                      />
                      <div v-if="row.ruleNotice" style="font-size: 10px; color: #166534; margin-top: 2px;">
                        ⚡ {{ row.ruleNotice }}
                      </div>
                    </td>

                    <!-- Stock Group Badge -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <span class="badge badge-purple" style="font-size: 10.5px;">
                        {{ row.stock_group || 'Sugar' }}
                      </span>
                    </td>

                    <!-- Quantity -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <input
                        data-field="quantity"
                        v-model.number="row.quantity"
                        type="number"
                        step="0.01"
                        min="0.01"
                        required
                        style="width: 100%; text-align: right; padding: 4px 6px; font-weight: 600;"
                        @input="() => onRowQtyInput(row)"
                        @keydown.enter.prevent="() => focusRowField(idx, 'bags')"
                      />
                    </td>

                    <!-- Bags -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <input
                        data-field="bags"
                        v-model.number="row.bags"
                        type="number"
                        step="1"
                        min="0"
                        style="width: 100%; text-align: right; padding: 4px 6px;"
                        @input="() => onRowBagsInput(row)"
                        @keydown.enter.prevent="() => focusRowField(idx, 'rate')"
                      />
                    </td>

                    <!-- Rate -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <input
                        data-field="rate"
                        v-model.number="row.rate"
                        type="number"
                        step="0.01"
                        min="0"
                        required
                        style="width: 100%; text-align: right; padding: 4px 6px; font-weight: 600;"
                        @input="() => calculateRow(row)"
                        @keydown.enter.prevent="() => focusRowField(idx, 'gst_rate')"
                      />
                    </td>

                    <!-- Trade Subtotal -->
                    <td style="text-align: right; vertical-align: middle; font-weight: 700; color: var(--navy); padding: 6px 8px;">
                      ₹{{ formatCurrency(row.trade_amount) }}
                    </td>

                    <!-- GST % -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <input
                        data-field="gst_rate"
                        v-model.number="row.gst_rate"
                        type="number"
                        step="0.01"
                        min="0"
                        max="100"
                        style="width: 100%; text-align: right; padding: 4px 6px; color: #166534; font-weight: 600;"
                        @input="() => calculateRow(row)"
                        @keydown.enter.prevent="() => focusRowField(idx, 'brokerage_rate')"
                      />
                    </td>

                    <!-- Brokerage Method & Rate -->
                    <td style="vertical-align: middle; padding: 6px 8px;">
                      <div style="display: flex; gap: 4px; align-items: center;">
                        <select
                          v-model="row.brokerage_method"
                          style="font-size: 11px; padding: 3px 4px; border-radius: 4px; border: 1px solid var(--line);"
                          @change="() => onRowMethodChange(row)"
                        >
                          <option value="Percentage">%</option>
                          <option value="Per Bag">₹/Bag</option>
                          <option value="Per Quintal">₹/Qtl</option>
                        </select>
                        <input
                          data-field="brokerage_rate"
                          v-model.number="row.brokerage_rate"
                          type="number"
                          step="0.01"
                          min="0"
                          style="width: 70px; text-align: right; padding: 4px 6px; font-size: 11.5px;"
                          @input="() => calculateRow(row)"
                          @keydown.enter.prevent="() => onRowEnd(idx)"
                        />
                      </div>
                    </td>

                    <!-- Brokerage Amount -->
                    <td style="text-align: right; vertical-align: middle; font-weight: 800; color: var(--green); padding: 6px 8px;">
                      ₹{{ formatCurrency(row.brokerage_amount) }}
                    </td>

                    <!-- Delete Row Button -->
                    <td style="text-align: center; vertical-align: middle; padding: 6px 4px;">
                      <button
                        type="button"
                        class="btn btn-sm"
                        style="background: transparent; color: #dc2626; border: none; font-size: 14px; cursor: pointer; padding: 2px 6px;"
                        :disabled="items.length <= 1"
                        title="Remove row"
                        @click="() => removeRow(idx)"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Net Multi-Item Summary Ribbon -->
            <div style="margin-top: 14px; padding: 14px 18px; background: var(--green-soft); border: 1px solid rgba(27, 135, 63, 0.2); border-radius: 6px; display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; align-items: center;">
              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: var(--muted); font-weight: 700;">Total Quantity</div>
                <div style="font-size: 16px; font-weight: 800; color: var(--navy);">
                  {{ formatNumber(totalQuantity) }} Qtl
                </div>
                <div style="font-size: 11px; color: var(--muted);">{{ formatNumber(totalBags) }} Bags</div>
              </div>

              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: var(--navy); font-weight: 700;">Trade Subtotal</div>
                <div style="font-size: 16px; font-weight: 800; color: var(--navy);">
                  ₹ {{ formatCurrency(totalTradeAmount) }}
                </div>
              </div>

              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 700;">Total GST</div>
                <div style="font-size: 16px; font-weight: 800; color: #166534;">
                  ₹ {{ formatCurrency(totalGstAmount) }}
                </div>
              </div>

              <div>
                <div style="font-size: 11px; text-transform: uppercase; color: var(--blue); font-weight: 700;">Grand Invoice Total</div>
                <div style="font-size: 18px; font-weight: 800; color: var(--blue);">
                  ₹ {{ formatCurrency(totalGrandAmount) }}
                </div>
              </div>

              <div style="text-align: right;">
                <div style="font-size: 11px; text-transform: uppercase; color: var(--green); font-weight: 700;">Brokerage Payable</div>
                <div style="font-size: 18px; font-weight: 800; color: var(--green);">
                  ₹ {{ formatCurrency(totalBrokerageAmount) }}
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
              <button type="button" class="btn btn-primary" :disabled="isSubmitting" @click="promptSubmit">
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
      section-title="Purchase Voucher (F9)"
      :items="menuItems"
      :active-index="0"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import { openConfirm, showToast, openGlobalBrokerModal } from '../composables/useKeyboardEngine'
import TypeaheadSelect from '../components/TypeaheadSelect.vue'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { searchEntities, getBrokerItemRate, savePurchaseEntry } = useFrappeApi()

// Field refs for Enter traversal
const postingDateInput = ref(null)
const brokerSelect = ref(null)
const remarksInput = ref(null)

const isSubmitting = ref(false)

const form = reactive({
  posting_date: bootState.today || new Date().toISOString().split('T')[0],
  broker: '',
  broker_name: '',
  party_name: '',
  ref_no: '',
  remarks: '',
})

// Calculate line item totals
const calculateRow = (row) => {
  const qty = Number(row.quantity) || 0
  const rate = Number(row.rate) || 0
  const bags = Number(row.bags) || 0
  const tradeAmt = Math.round(qty * rate * 100) / 100
  row.trade_amount = tradeAmt

  const gstRate = Number(row.gst_rate) || 0
  const halfPct = gstRate / 2.0
  row.cgst_rate = halfPct
  row.sgst_rate = halfPct
  row.cgst_amount = Math.round(tradeAmt * (halfPct / 100.0) * 100) / 100
  row.sgst_amount = Math.round(tradeAmt * (halfPct / 100.0) * 100) / 100
  row.total_gst_amount = Math.round((row.cgst_amount + row.sgst_amount) * 100) / 100
  row.grand_total = Math.round((tradeAmt + row.total_gst_amount) * 100) / 100

  let brkAmt = 0
  const bRate = Number(row.brokerage_rate) || 0
  if (row.brokerage_method === 'Percentage') {
    row.percentage = bRate
    row.per_bag = 0
    row.per_quintal = 0
    brkAmt = Math.round(tradeAmt * (bRate / 100.0) * 100) / 100
  } else if (row.brokerage_method === 'Per Bag') {
    row.percentage = 0
    row.per_bag = bRate
    row.per_quintal = 0
    brkAmt = Math.round(bags * bRate * 100) / 100
  } else if (row.brokerage_method === 'Per Quintal') {
    row.percentage = 0
    row.per_bag = 0
    row.per_quintal = bRate
    brkAmt = Math.round(qty * bRate * 100) / 100
  }
  row.brokerage_amount = brkAmt
}

// Helper to create an item row
let rowSeq = 0
const createRow = (defaultQty = 100, defaultRate = 3800) => {
  rowSeq++
  const row = reactive({
    id: `row-${Date.now()}-${rowSeq}`,
    item: '',
    item_name: '',
    hsn_code: '',
    stock_group: 'Sugar',
    quantity: defaultQty,
    bags: Math.round(defaultQty * 2),
    rate: defaultRate,
    trade_amount: defaultQty * defaultRate,
    gst_rate: 5.0,
    cgst_rate: 2.5,
    cgst_amount: 0,
    sgst_rate: 2.5,
    sgst_amount: 0,
    total_gst_amount: 0,
    grand_total: 0,
    brokerage_method: 'Percentage',
    brokerage_rate: 1.0,
    percentage: 1.0,
    per_bag: 0,
    per_quintal: 0,
    brokerage_amount: 0,
    rate_source: '',
    ruleNotice: '',
    remarks: '',
  })
  calculateRow(row)
  return row
}

// Multi-item rows array
const items = ref([createRow(100, 3800)])

const onRowQtyInput = (row) => {
  row.bags = Math.round(Number(row.quantity || 0) * 2.0)
  calculateRow(row)
}

const onRowBagsInput = (row) => {
  calculateRow(row)
}

const onRowMethodChange = (row) => {
  if (row.brokerage_method === 'Percentage' && (!row.brokerage_rate || row.brokerage_rate > 10)) {
    row.brokerage_rate = 1.0
  } else if (row.brokerage_method === 'Per Bag' && !row.brokerage_rate) {
    row.brokerage_rate = 10.0
  } else if (row.brokerage_method === 'Per Quintal' && !row.brokerage_rate) {
    row.brokerage_rate = 20.0
  }
  calculateRow(row)
}

// Add and remove rows
const addRow = () => {
  const newRow = createRow(100, 3800)
  items.value.push(newRow)
}

const removeRow = (idx) => {
  if (items.value.length > 1) {
    items.value.splice(idx, 1)
  }
}

// Grand aggregate computeds
const totalQuantity = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.quantity) || 0), 0) * 100) / 100
})

const totalBags = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.bags) || 0), 0) * 100) / 100
})

const totalTradeAmount = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.trade_amount) || 0), 0) * 100) / 100
})

const totalGstAmount = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.total_gst_amount) || 0), 0) * 100) / 100
})

const totalGrandAmount = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.grand_total) || 0), 0) * 100) / 100
})

const totalBrokerageAmount = computed(() => {
  return Math.round(items.value.reduce((s, r) => s + (Number(r.brokerage_amount) || 0), 0) * 100) / 100
})

// Search APIs
const searchPurchaseBrokers = async (q) => {
  return await searchEntities('Brokers', q, { for_purchase: 1 })
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
}

// Auto-rate fetching for a specific row
const fetchRowBrokerRate = async (row) => {
  if (!form.broker || !row.item) return
  try {
    const res = await getBrokerItemRate(form.broker, row.item, row.stock_group, 'Purchase', form.posting_date)
    if (res) {
      if (res.stock_group) row.stock_group = res.stock_group
      if (res.gst_rate !== undefined && res.gst_rate !== null) row.gst_rate = Number(res.gst_rate)
      if (res.found) {
        row.brokerage_method = res.brokerage_method
        row.brokerage_rate = Number(res.rate) || 0
        row.rate_source = res.source
        const symbol = res.brokerage_method === 'Percentage' ? `${res.rate}%` : (res.brokerage_method === 'Per Bag' ? `₹${res.rate}/bag` : `₹${res.rate}/qtl`)
        row.ruleNotice = `${res.brokerage_method} @ ${symbol} (${res.source})`
      } else {
        row.ruleNotice = ''
      }
    }
  } catch (e) {
    console.error('Failed to fetch broker rate for row:', e)
  }
}

const onBrokerSelected = async (b) => {
  if (b) {
    form.broker = b.id || b.name
    form.broker_name = b.label || b.broker_name || b.name
    for (const row of items.value) {
      if (row.item) {
        await fetchRowBrokerRate(row)
        calculateRow(row)
      }
    }
  } else {
    form.broker = ''
    form.broker_name = ''
  }
}

const onRowItemSelected = async (row, itm) => {
  if (itm) {
    row.item = itm.value || itm.id || itm.name
    row.item_name = itm.label || itm.item_name || itm.name
    row.hsn_code = itm.hsn_code || ''
    if (itm.stock_group) row.stock_group = itm.stock_group
    if (itm.gst_rate !== undefined && itm.gst_rate !== null) row.gst_rate = Number(itm.gst_rate)
    await fetchRowBrokerRate(row)
    calculateRow(row)
  } else {
    row.item = ''
    row.item_name = ''
    row.hsn_code = ''
    row.ruleNotice = ''
  }
}

const onDateChange = async () => {
  for (const row of items.value) {
    if (row.item) {
      await fetchRowBrokerRate(row)
      calculateRow(row)
    }
  }
}

const focusBroker = () => {
  if (brokerSelect.value && typeof brokerSelect.value.focus === 'function') {
    brokerSelect.value.focus()
  } else if (brokerSelect.value && brokerSelect.value.$el) {
    const inp = brokerSelect.value.$el.querySelector('input')
    if (inp) inp.focus()
  }
}

const focusFirstItem = () => {
  nextTick(() => {
    const firstItemInp = document.querySelector('.data-table tbody tr:first-child .typeahead-wrap input')
    if (firstItemInp) firstItemInp.focus()
  })
}

const focusRowField = (idx, field) => {
  nextTick(() => {
    const inp = document.querySelector(`.data-table tbody tr:nth-child(${idx + 1}) input[data-field="${field}"]`)
    if (inp) {
      inp.focus()
      inp.select?.()
    }
  })
}

const onRowEnd = (idx) => {
  if (idx < items.value.length - 1) {
    const nextItemInp = document.querySelector(`.data-table tbody tr:nth-child(${idx + 2}) .typeahead-wrap input`)
    if (nextItemInp) nextItemInp.focus()
  } else {
    if (remarksInput.value) remarksInput.value.focus()
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

const resetForm = () => {
  form.broker = ''
  form.broker_name = ''
  form.party_name = ''
  form.ref_no = ''
  form.remarks = ''
  items.value = [createRow(100, 3800)]
}

const promptSubmit = () => {
  if (!form.broker) {
    showToast('Please select a Purchase Broker')
    focusBroker()
    return
  }

  for (let i = 0; i < items.value.length; i++) {
    const row = items.value[i]
    if (!row.item) {
      showToast(`Please select a Commodity for row #${i + 1}`)
      return
    }
    if (!row.quantity || row.quantity <= 0) {
      showToast(`Please enter a valid Quantity for row #${i + 1}`)
      return
    }
    if (!row.rate || row.rate <= 0) {
      showToast(`Please enter a valid Rate for row #${i + 1}`)
      return
    }
  }

  const title = 'Accept Purchase Voucher?'
  const body = `Record Purchase of ${totalQuantity.value} Qtl across ${items.value.length} commodities (Grand Total: ₹${formatCurrency(totalGrandAmount.value)}, Brokerage: ₹${formatCurrency(totalBrokerageAmount.value)}) for Broker ${form.broker_name || form.broker}?`
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
      party_name: form.party_name || form.broker_name || '',
      supplier_name: form.party_name || '',
      ref_no: form.ref_no || '',
      items: items.value.map((it) => ({
        item: it.item,
        item_name: it.item_name,
        hsn_code: it.hsn_code || '',
        stock_group: it.stock_group,
        quantity: Number(it.quantity) || 0,
        bags: Number(it.bags) || 0,
        rate: Number(it.rate) || 0,
        gst_rate: Number(it.gst_rate) || 0,
        brokerage_method: it.brokerage_method,
        brokerage_rate: Number(it.brokerage_rate) || 0,
        percentage: it.brokerage_method === 'Percentage' ? Number(it.brokerage_rate) || 0 : 0,
        per_bag: it.brokerage_method === 'Per Bag' ? Number(it.brokerage_rate) || 0 : 0,
        per_quintal: it.brokerage_method === 'Per Quintal' ? Number(it.brokerage_rate) || 0 : 0,
        rate_source: it.rate_source || 'Purchase Entry',
        remarks: it.remarks || '',
      })),
      remarks: form.ref_no ? `Ref: ${form.ref_no}${form.remarks ? ' | ' + form.remarks : ''}` : form.remarks,
      submit: true,
    }

    const res = await savePurchaseEntry(payload)
    showToast(`✅ Purchase Voucher ${res.name} accepted & saved!`)
    resetForm()
    router.push('/registers?type=Purchase')
  } catch (e) {
    showToast('Submission failed: ' + e.message, 4000)
  } finally {
    isSubmitting.value = false
  }
}

// Right-Side Gateway Menu Items for Purchase View
const menuItems = [
  { isHeader: true, label: '⚡ VOUCHER ACTIONS' },
  { key: 'Enter', label: 'Accept Voucher (Save)', action: () => promptSubmit() },
  { key: 'A', label: '+ Add Commodity Row', action: () => addRow() },
  { key: 'F8', label: 'Switch to Sales Voucher', action: () => router.push('/sell') },
  { key: 'Esc', label: 'Gateway of Brokerage', action: () => router.push('/') },

  { isHeader: true, label: '📋 REGISTERS' },
  { key: 'O', label: 'Sales Outstandings (Due)', action: () => router.push('/registers?type=SalesOutstanding') },
  { key: 'I', label: 'Item-Wise Register', action: () => router.push('/registers?type=ItemWise') },
  { key: 'P', label: 'Purchase Register', action: () => router.push('/registers?type=Purchase') },
  { key: 'S', label: 'Sales Register', action: () => router.push('/registers?type=Sales') },

  { isHeader: true, label: '🏢 MASTERS' },
  { key: 'B', label: '+ New Broker (Full Screen)', action: () => openGlobalBrokerModal('') },
  { key: 'R', label: 'Date-Wise Rate Cards', action: () => router.push('/rate-configs') },
]

const handleSelect = (idx) => {
  if (menuItems[idx].isHeader) return
  menuItems[idx].action()
}

// Global Alt+A shortcut to add row
const handleKeyDown = (e) => {
  if (e.altKey && (e.key === 'a' || e.key === 'A')) {
    e.preventDefault()
    addRow()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  nextTick(() => {
    if (postingDateInput.value) postingDateInput.value.focus()
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
