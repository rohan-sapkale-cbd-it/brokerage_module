<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-dialog" style="max-width: 680px; width: 95%;">
      <div class="modal-header" style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);">
        <div class="modal-title" style="display: flex; align-items: center; gap: 8px; color: #fff;">
          <span>🌾</span>
          <span>{{ form.isEdit ? 'Edit Commodity / Item Master' : 'Create Commodity / Item Master' }}</span>
        </div>
        <button
          type="button"
          class="btn btn-sm"
          style="background: rgba(255,255,255,0.15); color: #fff; border: none; font-weight: 700;"
          @click="close"
        >
          ✕
        </button>
      </div>

      <div class="modal-body" style="padding: 22px 26px;">
        <div class="notice-banner notice-info" style="margin-bottom: 20px;">
          <span>💡 Select the <strong>Stock Group</strong> (e.g., <strong>Sugar</strong>). When this item is traded in Purchase or Sell entries, the broker's brokerage rate configured for that Stock Group will automatically apply!</span>
        </div>

        <form @submit.prevent="submitSave">
          <!-- Item Code & Name -->
          <div class="form-grid" style="grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Item Code / Identifier *</label>
              <input
                ref="codeRef"
                v-model="form.item_code"
                type="text"
                required
                :readonly="form.isEdit"
                placeholder="e.g. Sugar M30, Sugar S-30"
                style="font-size: 13.5px; font-weight: 600;"
                @keydown.enter.prevent="focusField('name')"
              />
            </div>

            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Item / Commodity Name *</label>
              <input
                ref="nameRef"
                v-model="form.item_name"
                type="text"
                required
                placeholder="e.g. Medium Grade Sugar M30"
                style="font-size: 13.5px;"
                @keydown.enter.prevent="focusField('stockGroup')"
              />
            </div>
          </div>

          <!-- Stock Group Selection (with inline quick Add Group) -->
          <div style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 8px; padding: 14px 18px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <label style="font-weight: 800; color: #1e40af; margin-bottom: 0;">
                🏷️ Belonging Stock Group *
              </label>
              <button
                type="button"
                class="btn btn-sm"
                style="background: #2563eb; color: #fff; font-size: 11px; padding: 4px 10px; font-weight: 700;"
                @click="openAddStockGroup"
              >
                + New Stock Group
              </button>
            </div>

            <div style="display: flex; gap: 10px; align-items: center;">
              <select
                ref="stockGroupRef"
                v-model="form.stock_group"
                style="font-size: 14px; font-weight: 700; color: #1e40af; background: #fff;"
                @change="onStockGroupChange"
                @keydown.enter.prevent="focusField('uom')"
              >
                <option v-for="g in stockGroups" :key="g.name" :value="g.name">
                  {{ g.stock_group_name || g.name }} (Default GST: {{ g.default_gst_rate || 5.0 }}%)
                </option>
              </select>
            </div>
            <div style="font-size: 12px; color: #3b82f6; margin-top: 6px;">
              Brokerage method &amp; rate will inherit automatically from Broker Master for <strong>{{ form.stock_group || 'Selected Group' }}</strong>.
            </div>
          </div>

          <!-- UOM, HSN Code, GST Rate & Standard Rate -->
          <div class="form-grid" style="grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Stock UOM *</label>
              <select
                ref="uomRef"
                v-model="form.stock_uom"
                style="font-size: 13.5px;"
                @keydown.enter.prevent="focusField('hsn')"
              >
                <option value="Quintal">Quintal (Qtl)</option>
                <option value="Bag">Bag (Bags)</option>
                <option value="Nos">Nos</option>
                <option value="Kg">Kg</option>
                <option value="Ton">Ton</option>
                <option value="Box">Box</option>
                <option value="Litre">Litre</option>
              </select>
            </div>

            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">HSN / SAC Code</label>
              <input
                ref="hsnRef"
                v-model="form.hsn_code"
                type="text"
                placeholder="e.g. 1701, 0802"
                style="font-size: 13.5px; font-weight: 600; font-family: var(--font-mono);"
                @keydown.enter.prevent="focusField('gst')"
              />
              <div style="font-size: 11px; color: #64748b; margin-top: 3px;">
                GST HSN code (e.g. 1701 for Sugar/Jaggery, 0802 for Almonds)
              </div>
            </div>
          </div>

          <div class="form-grid" style="grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">GST Rate (%) *</label>
              <div style="position: relative; display: flex; align-items: center;">
                <input
                  ref="gstRef"
                  v-model.number="form.gst_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  required
                  placeholder="5.0"
                  style="padding-right: 26px; font-weight: 700; color: #0f172a;"
                  @keydown.enter.prevent="focusField('stdRate')"
                />
                <span style="position: absolute; right: 10px; font-size: 13px; color: #64748b; font-weight: 700;">%</span>
              </div>
              <div style="font-size: 11px; color: #64748b; margin-top: 3px;">
                CGST: <strong>{{ ((form.gst_rate || 0) / 2).toFixed(2) }}%</strong> | SGST: <strong>{{ ((form.gst_rate || 0) / 2).toFixed(2) }}%</strong>
              </div>
            </div>

            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Standard Rate (₹)</label>
              <div style="position: relative; display: flex; align-items: center;">
                <span style="position: absolute; left: 10px; font-size: 13px; color: #64748b;">₹</span>
                <input
                  ref="stdRateRef"
                  v-model.number="form.standard_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  style="padding-left: 24px;"
                  @keydown.enter.prevent="focusField('desc')"
                />
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="form-group" style="margin-bottom: 22px;">
            <label style="font-weight: 700; color: #1e293b;">Description / Trade Notes</label>
            <textarea
              ref="descRef"
              v-model="form.description"
              rows="2"
              placeholder="e.g. Standard Sugar 50KG packaging (2.0 Bags = 1.0 Quintal)"
              style="font-size: 13px;"
              @keydown.ctrl.enter="submitSave"
            ></textarea>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 16px;">
            <div style="font-size: 12px; color: #64748b;">
              <span v-if="form.isEdit" style="font-family: var(--font-mono);">Editing: {{ form.item_code }}</span>
            </div>

            <div style="display: flex; gap: 10px; align-items: center;">
              <button type="button" class="btn btn-secondary" @click="close">
                Cancel (<kbd>Esc</kbd>)
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSaving"
                style="padding: 9px 26px; font-weight: 700;"
              >
                {{ isSaving ? 'Saving...' : '💾 Save Item Master' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Quick Stock Group Modal -->
    <StockGroupModal
      :show="showStockGroupModal"
      @close="showStockGroupModal = false"
      @saved="onStockGroupSaved"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import StockGroupModal from './StockGroupModal.vue'

const props = defineProps({
  show: Boolean,
  itemData: Object,
})

const emit = defineEmits(['close', 'saved'])

const { getStockGroups, saveItem } = useFrappeApi()
const isSaving = ref(false)
const stockGroups = ref([])
const showStockGroupModal = ref(false)

const codeRef = ref(null)
const nameRef = ref(null)
const stockGroupRef = ref(null)
const uomRef = ref(null)
const hsnRef = ref(null)
const gstRef = ref(null)
const stdRateRef = ref(null)
const descRef = ref(null)

const form = reactive({
  isEdit: false,
  item_code: '',
  item_name: '',
  hsn_code: '',
  stock_group: 'Sugar',
  stock_uom: 'Quintal',
  gst_rate: 5.0,
  standard_rate: 0,
  description: '',
})

const loadStockGroups = async () => {
  try {
    const list = await getStockGroups()
    stockGroups.value = list || []
    if (!form.stock_group && stockGroups.value.length > 0) {
      form.stock_group = stockGroups.value[0].name
      form.gst_rate = stockGroups.value[0].default_gst_rate || 5.0
    }
  } catch (e) {
    console.error('Failed to load stock groups:', e)
  }
}

watch(
  () => props.show,
  async (val) => {
    if (val) {
      await loadStockGroups()
      if (props.itemData) {
        form.isEdit = true
        form.item_code = props.itemData.item_code || props.itemData.name || ''
        form.item_name = props.itemData.item_name || props.itemData.name || ''
        form.hsn_code = props.itemData.hsn_code || props.itemData.gst_hsn_code || ''
        form.stock_group = props.itemData.stock_group || 'Sugar'
        form.stock_uom = props.itemData.stock_uom || 'Quintal'
        form.gst_rate = props.itemData.gst_rate !== undefined ? props.itemData.gst_rate : 5.0
        form.standard_rate = props.itemData.standard_rate || 0
        form.description = props.itemData.description || ''
      } else {
        form.isEdit = false
        form.item_code = ''
        form.item_name = ''
        form.hsn_code = ''
        form.stock_group = stockGroups.value.find((g) => g.name === 'Sugar')?.name || (stockGroups.value[0]?.name || 'Sugar')
        form.stock_uom = 'Quintal'
        form.gst_rate = 5.0
        form.standard_rate = 0
        form.description = ''
      }
      nextTick(() => {
        if (!form.isEdit && codeRef.value) codeRef.value.focus()
        else if (nameRef.value) nameRef.value.focus()
      })
    }
  }
)

const focusField = (field) => {
  if (field === 'name' && nameRef.value) nameRef.value.focus()
  else if (field === 'stockGroup' && stockGroupRef.value) stockGroupRef.value.focus()
  else if (field === 'uom' && uomRef.value) uomRef.value.focus()
  else if (field === 'hsn' && hsnRef.value) hsnRef.value.focus()
  else if (field === 'gst' && gstRef.value) gstRef.value.focus()
  else if (field === 'stdRate' && stdRateRef.value) stdRateRef.value.focus()
  else if (field === 'desc' && descRef.value) descRef.value.focus()
}

const onStockGroupChange = () => {
  const chosen = stockGroups.value.find((g) => g.name === form.stock_group)
  if (chosen && chosen.default_gst_rate !== undefined) {
    form.gst_rate = chosen.default_gst_rate
  }
}

const openAddStockGroup = () => {
  showStockGroupModal.value = true
}

const onStockGroupSaved = async (newGroup) => {
  await loadStockGroups()
  form.stock_group = newGroup.name || newGroup.stock_group_name
  if (newGroup.default_gst_rate !== undefined) {
    form.gst_rate = newGroup.default_gst_rate
  }
}

const close = () => {
  emit('close')
}

const submitSave = async () => {
  if (!form.item_code.trim()) {
    showToast('Item Code / Identifier is required!')
    return
  }
  if (!form.item_name.trim()) {
    form.item_name = form.item_code
  }
  isSaving.value = true
  try {
    const res = await saveItem(form)
    showToast(`Item "${res.item_name || res.item_code}" saved successfully!`)
    emit('saved', res)
    close()
  } catch (err) {
    showToast(`Error: ${err.message}`)
  } finally {
    isSaving.value = false
  }
}
</script>

