<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-dialog stock-group-dialog">
      <div class="modal-header" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);">
        <div class="modal-title" style="display: flex; align-items: center; gap: 8px; color: #fff;">
          <span>📦</span>
          <span>{{ form.name ? 'Edit Stock Group' : 'New Stock Group' }}</span>
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

      <div class="modal-body">
        <div class="notice-banner notice-info" style="margin-bottom: 20px;">
          <span>💡 Stock Groups (e.g., <strong>Sugar</strong>, <strong>Edible Oil</strong>, <strong>Grains</strong>) allow brokers to have unified brokerage terms across all grades and items belonging to that commodity class.</span>
        </div>

        <form @submit.prevent="submitSave">
          <div class="form-group" style="margin-bottom: 16px;">
            <label style="font-weight: 700; color: #1e293b;">Stock Group Name *</label>
            <input
              ref="nameInput"
              v-model="form.stock_group_name"
              type="text"
              required
              placeholder="e.g. Sugar, Edible Oil, Grains, Pulses"
              style="font-size: 14px; font-weight: 600;"
              @keydown.enter.prevent="focusField('gstRate')"
            />
          </div>

          <div class="modal-grid-2col">
            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Default GST Rate (%) *</label>
              <div style="position: relative; display: flex; align-items: center;">
                <input
                  ref="gstRateInput"
                  v-model.number="form.default_gst_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  required
                  placeholder="5.0"
                  style="padding-right: 28px; font-weight: 700;"
                  @keydown.enter.prevent="focusField('status')"
                />
                <span style="position: absolute; right: 10px; font-size: 13px; color: #64748b; font-weight: 700;">%</span>
              </div>
              <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">
                Intra-state: <strong>{{ ((form.default_gst_rate || 0) / 2).toFixed(2) }}% CGST</strong> + <strong>{{ ((form.default_gst_rate || 0) / 2).toFixed(2) }}% SGST</strong>
              </div>
            </div>

            <div class="form-group">
              <label style="font-weight: 700; color: #1e293b;">Status</label>
              <select
                ref="statusSelect"
                v-model="form.is_active"
                style="font-size: 13.5px;"
                @keydown.enter.prevent="focusField('description')"
              >
                <option :value="1">Active</option>
                <option :value="0">Inactive</option>
              </select>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 22px;">
            <label style="font-weight: 700; color: #1e293b;">Description (Optional)</label>
            <textarea
              ref="descInput"
              v-model="form.description"
              rows="2"
              placeholder="Commodity category description..."
              style="font-size: 13px;"
              @keydown.ctrl.enter="submitSave"
            ></textarea>
          </div>

          <div class="modal-footer-actions">
            <button type="button" class="btn btn-secondary" @click="close">
              Cancel (<kbd>Esc</kbd>)
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSaving"
              style="padding: 9px 24px; font-weight: 700;"
            >
              {{ isSaving ? 'Saving...' : '💾 Save Stock Group' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'

const props = defineProps({
  show: Boolean,
  groupData: Object,
})

const emit = defineEmits(['close', 'saved'])

const { saveStockGroup } = useFrappeApi()
const isSaving = ref(false)

const nameInput = ref(null)
const gstRateInput = ref(null)
const statusSelect = ref(null)
const descInput = ref(null)

const form = reactive({
  name: '',
  stock_group_name: '',
  default_gst_rate: 5.0,
  is_active: 1,
  description: '',
})

watch(
  () => props.show,
  (val) => {
    if (val) {
      if (props.groupData) {
        form.name = props.groupData.name || ''
        form.stock_group_name = props.groupData.stock_group_name || props.groupData.name || ''
        form.default_gst_rate = props.groupData.default_gst_rate !== undefined ? props.groupData.default_gst_rate : 5.0
        form.is_active = props.groupData.is_active !== undefined ? props.groupData.is_active : 1
        form.description = props.groupData.description || ''
      } else {
        form.name = ''
        form.stock_group_name = ''
        form.default_gst_rate = 5.0
        form.is_active = 1
        form.description = ''
      }
      nextTick(() => {
        if (nameInput.value) nameInput.value.focus()
      })
    }
  }
)

const focusField = (field) => {
  if (field === 'gstRate' && gstRateInput.value) gstRateInput.value.focus()
  else if (field === 'status' && statusSelect.value) statusSelect.value.focus()
  else if (field === 'description' && descInput.value) descInput.value.focus()
}

const close = () => {
  emit('close')
}

const submitSave = async () => {
  if (!form.stock_group_name.trim()) {
    showToast('Stock Group Name is required!')
    return
  }
  isSaving.value = true
  try {
    const res = await saveStockGroup(form)
    showToast(`Stock Group "${res.stock_group_name || res.name}" saved!`)
    emit('saved', res)
    close()
  } catch (err) {
    showToast(`Error: ${err.message}`)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.stock-group-dialog {
  max-width: 580px;
  width: 95%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: var(--panel);
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

@media (max-width: 640px) {
  .stock-group-dialog {
    width: 96% !important;
    max-height: 94vh !important;
  }

  .modal-body {
    padding: 14px 14px !important;
  }

  .modal-header {
    padding: 10px 14px !important;
  }

  .modal-grid-2col {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }

  .modal-footer-actions {
    flex-direction: column-reverse;
    gap: 8px;
  }

  .modal-footer-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

