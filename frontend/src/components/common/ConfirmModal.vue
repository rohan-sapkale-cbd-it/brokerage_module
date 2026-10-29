<template>
  <div v-if="globalUiState.isConfirmModalOpen.value" class="modal-overlay" @click.self="closeConfirm(false)">
    <div class="modal-box" style="width: 440px; padding: 22px;">
      <div style="font-weight: 700; font-size: 16px; color: var(--navy); margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
        <span>💾</span>
        <span>{{ data?.title || 'Accept Voucher?' }}</span>
      </div>
      <div style="font-size: 13.5px; color: var(--text); margin-bottom: 22px; line-height: 1.55;">
        {{ data?.body || 'Do you want to accept and save this transaction?' }}
      </div>
      <div style="display: flex; justify-content: flex-end; gap: 10px; align-items: center;">
        <button
          type="button"
          style="padding: 7px 14px; border: 1px solid var(--line-dark); background: var(--panel); color: var(--text); border-radius: 4px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 5px;"
          @click="closeConfirm(false)"
        >
          <span>No</span>
          <kbd style="font-size: 10px;">Esc / N</kbd>
        </button>
        <button
          type="button"
          style="padding: 7px 18px; border: none; background: var(--blue); color: #fff; border-radius: 4px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 5px;"
          @click="closeConfirm(true)"
        >
          <span>Yes, Accept</span>
          <kbd style="font-size: 10px; background: rgba(255,255,255,0.25); color: #fff; border-color: rgba(255,255,255,0.4);">Enter / Y</kbd>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { globalUiState, closeConfirm } from '../../composables/useKeyboardEngine'

const data = computed(() => globalUiState.confirmModalData.value)
</script>

