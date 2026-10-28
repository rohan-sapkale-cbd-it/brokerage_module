<template>
  <div v-if="show" class="modal-overlay" :class="{ 'fullscreen-overlay': isFullscreen }" @click.self="close">
    <div
      class="modal-dialog"
      :class="{ 'modal-fullscreen': isFullscreen }"
      :style="isFullscreen ? '' : 'max-width: 1100px; width: 95%; max-height: 92vh;'"
    >
      <!-- Fullscreen Header -->
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
          <div class="modal-title" style="display: flex; align-items: center; gap: 10px;">
            <span>{{ form.name ? '✏️ Edit Broker Master' : '➕ Create New Broker Master' }}</span>
            <span v-if="form.name" class="badge badge-blue" style="font-size: 11px;">{{ form.name }}</span>
            <span v-if="isFullscreen" class="badge badge-purple" style="font-size: 11px;">⛶ Full Screen Mode</span>
          </div>

          <div style="display: flex; gap: 8px;">
            <span
              class="badge"
              :class="form.applicable_for_purchase ? 'badge-blue' : 'badge-gray'"
              style="font-size: 11px;"
            >
              {{ form.applicable_for_purchase ? '🛒 Purchase Checkpoint ON' : '🛒 Purchase OFF' }}
            </span>
            <span
              class="badge"
              :class="form.applicable_for_sales ? 'badge-green' : 'badge-gray'"
              style="font-size: 11px;"
            >
              {{ form.applicable_for_sales ? '🏷️ Sell Checkpoint ON' : '🏷️ Sell OFF' }}
            </span>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 10px;">
          <!-- Toggle Fullscreen / Standard View -->
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            style="background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.25);"
            @click="isFullscreen = !isFullscreen"
            :title="isFullscreen ? 'Switch to Standard Dialog' : 'Switch to Full Screen'"
          >
            {{ isFullscreen ? '🗗 Standard Window' : '⛶ Full Screen' }}
          </button>

          <!-- Close Button -->
          <button
            type="button"
            class="btn btn-sm"
            style="background: #ef4444; color: #fff; font-weight: 700; border: none; padding: 6px 12px;"
            @click="close"
            title="Close dialog (Esc)"
          >
            ✕ Close
          </button>
        </div>
      </div>

      <div class="modal-body">
        <!-- Section 1: Basic Profile & Contact Details (Wide Grid) -->
        <div style="background: #ffffff; padding: 20px 24px; border-radius: 10px; border: 1px solid var(--border); margin-bottom: 24px; box-shadow: var(--shadow-sm);">
          <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span>👤</span>
            <span>Broker Identity &amp; Contact Details</span>
          </div>

          <div class="form-grid" style="grid-template-columns: 2fr 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div class="form-group">
              <label>Broker Full Name *</label>
              <input
                v-model="form.broker_name"
                type="text"
                placeholder="e.g. Chirag Trading Co. / Nitin Bhai"
                required
                style="font-weight: 600; font-size: 14px;"
              />
            </div>

            <div class="form-group">
              <label>Mobile Number (10 digits)</label>
              <input
                v-model="form.mobile_no"
                type="text"
                maxlength="10"
                placeholder="e.g. 9876543210"
              />
            </div>

            <div class="form-group">
              <label>City / Location</label>
              <input
                v-model="form.city"
                type="text"
                placeholder="e.g. Pune, Kolhapur"
              />
            </div>

            <div class="form-group">
              <label>State</label>
              <input
                v-model="form.state"
                type="text"
                placeholder="e.g. Maharashtra"
              />
            </div>
          </div>

          <div class="form-grid" style="grid-template-columns: 1fr 1fr 1fr; gap: 16px;">
            <div class="form-group">
              <label>GST Number (Optional)</label>
              <input
                v-model="form.gst_number"
                type="text"
                placeholder="e.g. 27AAAAA0000A1Z5"
              />
            </div>

            <div class="form-group">
              <label>Email Address (Optional)</label>
              <input
                v-model="form.email"
                type="email"
                placeholder="e.g. broker@example.com"
              />
            </div>

            <div class="form-group">
              <label>Active Status</label>
              <select v-model="form.status">
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section 2: Operational Role Checkpoints (Purchase & Sell) -->
        <div style="background: #ffffff; padding: 20px 24px; border-radius: 10px; border: 1px solid var(--border); margin-bottom: 24px; box-shadow: var(--shadow-sm);">
          <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 6px; display: flex; align-items: center; gap: 8px;">
            <span>📌</span>
            <span>Broker Operational Checkpoints (Select Applicable Trading Roles)</span>
          </div>
          <div style="font-size: 12.5px; color: #64748b; margin-bottom: 16px;">
            Each checkpoint dynamically enables or disables the respective commission table. A broker can participate in Purchase, Sell, or Both.
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <!-- Checkpoint 1: Purchase -->
            <label
              style="display: flex; gap: 14px; padding: 16px 20px; border-radius: 8px; border: 2px solid; cursor: pointer; transition: all 0.15s ease;"
              :style="form.applicable_for_purchase ? 'border-color: #2563eb; background: #eff6ff;' : 'border-color: #e2e8f0; background: #f8fafc;'"
            >
              <input
                type="checkbox"
                v-model="form.applicable_for_purchase"
                style="width: 22px; height: 22px; accent-color: #2563eb; margin-top: 2px;"
              />
              <div>
                <div style="font-size: 15px; font-weight: 700; color: #1e40af; display: flex; align-items: center; gap: 8px;">
                  <span>🛒 Applicable for Purchase</span>
                  <span v-if="form.applicable_for_purchase" class="badge badge-blue">Table Active</span>
                </div>
                <div style="font-size: 12px; color: #475569; margin-top: 4px;">
                  Check this if the shop purchases commodities through this broker. Activates the Purchase Brokerage Table below.
                </div>
              </div>
            </label>

            <!-- Checkpoint 2: Sell -->
            <label
              style="display: flex; gap: 14px; padding: 16px 20px; border-radius: 8px; border: 2px solid; cursor: pointer; transition: all 0.15s ease;"
              :style="form.applicable_for_sales ? 'border-color: #059669; background: #ecfdf5;' : 'border-color: #e2e8f0; background: #f8fafc;'"
            >
              <input
                type="checkbox"
                v-model="form.applicable_for_sales"
                style="width: 22px; height: 22px; accent-color: #059669; margin-top: 2px;"
              />
              <div>
                <div style="font-size: 15px; font-weight: 700; color: #065f46; display: flex; align-items: center; gap: 8px;">
                  <span>🏷️ Applicable for Sell</span>
                  <span v-if="form.applicable_for_sales" class="badge badge-green">Table Active</span>
                </div>
                <div style="font-size: 12px; color: #475569; margin-top: 4px;">
                  Check this if the shop sells commodities through this broker. Activates the Sell Brokerage Table below.
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Section 3: Purchase Brokerage Rules Table -->
        <div
          v-if="form.applicable_for_purchase"
          style="background: #ffffff; border: 2px solid #93c5fd; border-radius: 10px; padding: 22px 26px; margin-bottom: 28px; box-shadow: var(--shadow-sm);"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 12px;">
            <div>
              <div style="font-size: 16px; font-weight: 800; color: #1e40af; display: flex; align-items: center; gap: 8px;">
                <span>🛒 Purchase Brokerage Commission Rates</span>
                <span class="badge badge-blue">{{ form.purchase_brokerage_rules.length }} Rules</span>
              </div>
              <div style="font-size: 12.5px; color: #64748b; margin-top: 3px;">
                Strict mutual exclusivity: Each item row supports exactly ONE active calculation method (Percentage %, Per Bag ₹, or Per Quintal ₹).
              </div>
            </div>

            <div style="display: flex; gap: 10px; align-items: center;">
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="quickAddAllCommodities('purchase_brokerage_rules')"
                title="Populate all available commodities in 1 click"
              >
                ⚡ Add All Commodities ({{ availableItems.length }})
              </button>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                style="background: #2563eb;"
                @click="addPurchaseRow"
              >
                + Add Item Row
              </button>
            </div>
          </div>

          <div v-if="form.purchase_brokerage_rules.length === 0" style="text-align: center; padding: 36px 20px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1; color: #64748b;">
            <div style="font-size: 32px; margin-bottom: 8px;">🛒</div>
            <div style="font-size: 14px; font-weight: 700; color: #334155;">No Purchase Commission Rules Added Yet</div>
            <div style="font-size: 12.5px; margin-top: 4px;">Click <strong>"+ Add Item Row"</strong> or <strong>"⚡ Add All Commodities"</strong> to configure rates.</div>
          </div>

          <div v-else class="modal-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 36px; text-align: center;">#</th>
                  <th style="min-width: 380px;">Commodity / Item Name *</th>
                  <th style="width: 170px;">Calculation Method</th>
                  <th style="width: 150px;">Per Bag (₹)</th>
                  <th style="width: 150px;">Per Quintal (₹)</th>
                  <th style="width: 150px;">Percentage (%)</th>
                  <th>Remarks</th>
                  <th style="width: 44px; text-align: center;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.purchase_brokerage_rules" :key="idx">
                  <td style="text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">
                    {{ idx + 1 }}
                  </td>

                  <!-- Commodity / Item Selection Column with Search AND Direct Dropdown Picker -->
                  <td>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <div style="flex: 1; min-width: 240px;">
                        <TypeaheadSelect
                          v-model="row.item"
                          :label="row.item_name || row.item"
                          placeholder="Type or click to search item..."
                          :fetch-fn="searchItems"
                          @change="(it) => { if(it) row.item_name = it.label || it.name }"
                        />
                      </div>
                      <select
                        v-if="availableItems.length > 0"
                        style="width: 150px; font-size: 12px; padding: 7px 8px; background: #f1f5f9; border-color: #cbd5e1; cursor: pointer;"
                        title="Quick Pick from list of all items"
                        @change="(e) => onQuickPickItem(row, e)"
                      >
                        <option value="">▼ Pick Item...</option>
                        <option v-for="it in availableItems" :key="it.id || it.name" :value="it.id || it.name">
                          {{ it.label || it.name }}
                        </option>
                      </select>
                    </div>
                  </td>

                  <!-- Method Selection -->
                  <td>
                    <select
                      v-model="row.brokerage_method"
                      style="font-weight: 600; color: #1e40af;"
                      @change="onMethodChange(row)"
                    >
                      <option value="Percentage">Percentage (%)</option>
                      <option value="Per Bag">Per Bag (₹)</option>
                      <option value="Per Quintal">Per Quintal (₹)</option>
                    </select>
                  </td>

                  <!-- Per Bag Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <span style="position: absolute; left: 10px; font-size: 12px; color: #64748b;">₹</span>
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.per_bag"
                        placeholder="0.00"
                        style="padding-left: 24px;"
                        :style="row.brokerage_method === 'Per Bag' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700; color: #1e40af;' : 'opacity: 0.45;'"
                        @input="onPerBagInput(row)"
                      />
                    </div>
                  </td>

                  <!-- Per Quintal Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <span style="position: absolute; left: 10px; font-size: 12px; color: #64748b;">₹</span>
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.per_quintal"
                        placeholder="0.00"
                        style="padding-left: 24px;"
                        :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700; color: #1e40af;' : 'opacity: 0.45;'"
                        @input="onPerQuintalInput(row)"
                      />
                    </div>
                  </td>

                  <!-- Percentage Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.percentage"
                        placeholder="0.00"
                        style="padding-right: 24px;"
                        :style="row.brokerage_method === 'Percentage' ? 'border-color: #2563eb; background: #eff6ff; font-weight: 700; color: #1e40af;' : 'opacity: 0.45;'"
                        @input="onPercentageInput(row)"
                      />
                      <span style="position: absolute; right: 10px; font-size: 12px; color: #64748b;">%</span>
                    </div>
                  </td>

                  <!-- Remarks -->
                  <td>
                    <input
                      type="text"
                      v-model="row.remarks"
                      placeholder="e.g. Regular terms"
                      style="font-size: 12px;"
                    />
                  </td>

                  <!-- Remove -->
                  <td style="text-align: center;">
                    <button
                      type="button"
                      class="btn btn-sm"
                      style="background: transparent; color: #ef4444; border: none; font-size: 16px; padding: 4px;"
                      @click="removePurchaseRow(idx)"
                      title="Delete row"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section 4: Sell Brokerage Rules Table -->
        <div
          v-if="form.applicable_for_sales"
          style="background: #ffffff; border: 2px solid #86efac; border-radius: 10px; padding: 22px 26px; margin-bottom: 28px; box-shadow: var(--shadow-sm);"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 12px;">
            <div>
              <div style="font-size: 16px; font-weight: 800; color: #065f46; display: flex; align-items: center; gap: 8px;">
                <span>🏷️ Sell Brokerage Commission Rates</span>
                <span class="badge badge-green">{{ form.sales_brokerage_rules.length }} Rules</span>
              </div>
              <div style="font-size: 12.5px; color: #64748b; margin-top: 3px;">
                Strict mutual exclusivity: Each item row supports exactly ONE active calculation method (Percentage %, Per Bag ₹, or Per Quintal ₹).
              </div>
            </div>

            <div style="display: flex; gap: 10px; align-items: center;">
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="quickAddAllCommodities('sales_brokerage_rules')"
                title="Populate all available commodities in 1 click"
              >
                ⚡ Add All Commodities ({{ availableItems.length }})
              </button>
              <button
                type="button"
                class="btn btn-success btn-sm"
                style="background: #059669;"
                @click="addSalesRow"
              >
                + Add Item Row
              </button>
            </div>
          </div>

          <div v-if="form.sales_brokerage_rules.length === 0" style="text-align: center; padding: 36px 20px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1; color: #64748b;">
            <div style="font-size: 32px; margin-bottom: 8px;">🏷️</div>
            <div style="font-size: 14px; font-weight: 700; color: #334155;">No Sell Commission Rules Added Yet</div>
            <div style="font-size: 12.5px; margin-top: 4px;">Click <strong>"+ Add Item Row"</strong> or <strong>"⚡ Add All Commodities"</strong> to configure rates.</div>
          </div>

          <div v-else class="modal-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 36px; text-align: center;">#</th>
                  <th style="min-width: 380px;">Commodity / Item Name *</th>
                  <th style="width: 170px;">Calculation Method</th>
                  <th style="width: 150px;">Per Bag (₹)</th>
                  <th style="width: 150px;">Per Quintal (₹)</th>
                  <th style="width: 150px;">Percentage (%)</th>
                  <th>Remarks</th>
                  <th style="width: 44px; text-align: center;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in form.sales_brokerage_rules" :key="idx">
                  <td style="text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">
                    {{ idx + 1 }}
                  </td>

                  <!-- Commodity / Item Selection Column with Search AND Direct Dropdown Picker -->
                  <td>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <div style="flex: 1; min-width: 240px;">
                        <TypeaheadSelect
                          v-model="row.item"
                          :label="row.item_name || row.item"
                          placeholder="Type or click to search item..."
                          :fetch-fn="searchItems"
                          @change="(it) => { if(it) row.item_name = it.label || it.name }"
                        />
                      </div>
                      <select
                        v-if="availableItems.length > 0"
                        style="width: 150px; font-size: 12px; padding: 7px 8px; background: #f1f5f9; border-color: #cbd5e1; cursor: pointer;"
                        title="Quick Pick from list of all items"
                        @change="(e) => onQuickPickItem(row, e)"
                      >
                        <option value="">▼ Pick Item...</option>
                        <option v-for="it in availableItems" :key="it.id || it.name" :value="it.id || it.name">
                          {{ it.label || it.name }}
                        </option>
                      </select>
                    </div>
                  </td>

                  <!-- Method Selection -->
                  <td>
                    <select
                      v-model="row.brokerage_method"
                      style="font-weight: 600; color: #059669;"
                      @change="onMethodChange(row)"
                    >
                      <option value="Percentage">Percentage (%)</option>
                      <option value="Per Bag">Per Bag (₹)</option>
                      <option value="Per Quintal">Per Quintal (₹)</option>
                    </select>
                  </td>

                  <!-- Per Bag Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <span style="position: absolute; left: 10px; font-size: 12px; color: #64748b;">₹</span>
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.per_bag"
                        placeholder="0.00"
                        style="padding-left: 24px;"
                        :style="row.brokerage_method === 'Per Bag' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700; color: #065f46;' : 'opacity: 0.45;'"
                        @input="onPerBagInput(row)"
                      />
                    </div>
                  </td>

                  <!-- Per Quintal Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <span style="position: absolute; left: 10px; font-size: 12px; color: #64748b;">₹</span>
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.per_quintal"
                        placeholder="0.00"
                        style="padding-left: 24px;"
                        :style="row.brokerage_method === 'Per Quintal' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700; color: #065f46;' : 'opacity: 0.45;'"
                        @input="onPerQuintalInput(row)"
                      />
                    </div>
                  </td>

                  <!-- Percentage Rate -->
                  <td>
                    <div style="position: relative; display: flex; align-items: center;">
                      <input
                        type="number"
                        step="0.01"
                        v-model.number="row.percentage"
                        placeholder="0.00"
                        style="padding-right: 24px;"
                        :style="row.brokerage_method === 'Percentage' ? 'border-color: #059669; background: #ecfdf5; font-weight: 700; color: #065f46;' : 'opacity: 0.45;'"
                        @input="onPercentageInput(row)"
                      />
                      <span style="position: absolute; right: 10px; font-size: 12px; color: #64748b;">%</span>
                    </div>
                  </td>

                  <!-- Remarks -->
                  <td>
                    <input
                      type="text"
                      v-model="row.remarks"
                      placeholder="e.g. Sell commission"
                      style="font-size: 12px;"
                    />
                  </td>

                  <!-- Remove -->
                  <td style="text-align: center;">
                    <button
                      type="button"
                      class="btn btn-sm"
                      style="background: transparent; color: #ef4444; border: none; font-size: 16px; padding: 4px;"
                      @click="removeSalesRow(idx)"
                      title="Delete row"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Sticky Fullscreen Footer -->
      <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 13px; color: #64748b; display: flex; gap: 16px; align-items: center;">
          <span>
            Total Rules: <strong>{{ (form.purchase_brokerage_rules.length + form.sales_brokerage_rules.length) }}</strong>
          </span>
          <span v-if="form.name" style="font-family: var(--font-mono); font-size: 12px;">ID: {{ form.name }}</span>
        </div>

        <div style="display: flex; gap: 12px; align-items: center;">
          <button type="button" class="btn btn-secondary" @click="close">
            Cancel (<kbd>Esc</kbd>)
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="isSaving"
            style="padding: 10px 28px; font-size: 14px; font-weight: 700;"
            @click="submitSave"
          >
            {{ isSaving ? 'Saving...' : '💾 Save Broker Master' }}
            <kbd style="background: rgba(255,255,255,0.25); color: #fff; border: none; margin-left: 6px;">Ctrl+Enter</kbd>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import TypeaheadSelect from './TypeaheadSelect.vue'

const props = defineProps({
  show: Boolean,
  brokerData: Object,
})

const emit = defineEmits(['close', 'saved'])

const { saveBroker, searchEntities } = useFrappeApi()
const isSaving = ref(false)
const isFullscreen = ref(true) // DEFAULTS TO FULL SCREEN AS REQUESTED
const availableItems = ref([])

const form = reactive({
  name: '',
  broker_name: '',
  mobile_no: '',
  city: '',
  state: '',
  gst_number: '',
  email: '',
  status: 'Active',
  applicable_for_purchase: true,
  applicable_for_sales: true,
  purchase_brokerage_rules: [],
  sales_brokerage_rules: [],
})

// Load available commodities on open
const loadAvailableCommodities = async () => {
  try {
    const res = await searchEntities('Item', '', { limit: 100 })
    availableItems.value = res || []
  } catch (err) {
    console.error('Failed to load items:', err)
  }
}

watch(
  () => props.show,
  (val) => {
    if (val) {
      loadAvailableCommodities()
    }
  }
)

watch(
  () => props.brokerData,
  (val) => {
    if (val) {
      form.name = val.name || ''
      form.broker_name = val.broker_name || ''
      form.mobile_no = val.mobile_no || ''
      form.city = val.city || ''
      form.state = val.state || ''
      form.gst_number = val.gst_number || ''
      form.email = val.email || ''
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
  form.gst_number = ''
  form.email = ''
  form.status = 'Active'
  form.applicable_for_purchase = true
  form.applicable_for_sales = true
  form.purchase_brokerage_rules = []
  form.sales_brokerage_rules = []
}

const searchItems = async (q) => {
  return await searchEntities('Item', q)
}

const onQuickPickItem = (row, e) => {
  const chosenVal = e.target.value
  if (!chosenVal) return
  const it = availableItems.value.find((i) => (i.id || i.name) === chosenVal)
  if (it) {
    row.item = it.id || it.name
    row.item_name = it.label || it.name
  }
  e.target.value = ''
}

const quickAddAllCommodities = (tableField) => {
  if (availableItems.value.length === 0) return
  const currentTable = form[tableField]
  const existingItems = new Set(currentTable.map((r) => r.item))

  for (const it of availableItems.value) {
    const itemCode = it.id || it.name
    if (!existingItems.has(itemCode)) {
      currentTable.push({
        item: itemCode,
        item_name: it.label || it.name,
        brokerage_method: 'Percentage',
        percentage: 1.0,
        per_bag: 0,
        per_quintal: 0,
        remarks: '',
      })
      existingItems.add(itemCode)
    }
  }
}

const addPurchaseRow = () => {
  form.purchase_brokerage_rules.push({
    item: '',
    item_name: '',
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
  form.sales_brokerage_rules.push({
    item: '',
    item_name: '',
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

const handleKeydown = (e) => {
  if (!props.show) return
  if (e.key === 'Escape') {
    close()
  } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    submitSave()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  loadAvailableCommodities()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

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
