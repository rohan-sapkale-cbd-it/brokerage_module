<template>
  <div v-if="globalUiState.isDateModalOpen.value" class="modal-overlay" @click.self="close">
    <div class="modal-box" style="width: 360px; padding: 20px;">
      <div style="font-weight: 700; font-size: 15px; color: var(--navy); margin-bottom: 6px; display: flex; align-items: center; gap: 8px;">
        <span>📅</span>
        <span>Set System / Working Date</span>
      </div>
      <p style="font-size: 12px; color: var(--muted); margin-bottom: 16px;">
        Change current working date for new vouchers and register lookups.
      </p>

      <div style="margin-bottom: 18px;">
        <input
          ref="dateInput"
          v-model="tempDate"
          type="date"
          style="width: 100%; font-size: 14px; padding: 8px 10px;"
          @keydown.enter.prevent="saveDate"
          @keydown.esc="close"
        />
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button
          type="button"
          style="padding: 6px 12px; border: 1px solid var(--line-dark); background: var(--panel); color: var(--text); border-radius: 4px; font-weight: 600; cursor: pointer;"
          @click="close"
        >
          Cancel (Esc)
        </button>
        <button
          type="button"
          style="padding: 6px 16px; border: none; background: var(--blue); color: #fff; border-radius: 4px; font-weight: 700; cursor: pointer;"
          @click="saveDate"
        >
          Update Date (Enter)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { globalUiState, showToast } from '../../composables/useKeyboardEngine'
import { bootState } from '../../composables/useFrappeApi'

const tempDate = ref(bootState.today || new Date().toISOString().split('T')[0])
const dateInput = ref(null)

watch(() => globalUiState.isDateModalOpen.value, (open) => {
  if (open) {
    tempDate.value = bootState.today
    nextTick(() => dateInput.value && dateInput.value.focus())
  }
})

const saveDate = () => {
  if (tempDate.value) {
    bootState.today = tempDate.value
    showToast(`Working date set to ${tempDate.value}`)
  }
  close()
}

const close = () => {
  globalUiState.isDateModalOpen.value = false
}
</script>

