<template>
  <div v-if="globalUiState.isHelpOpen.value" class="modal-overlay" @click.self="close">
    <div class="modal-box" style="width: 560px; max-width: 92%; max-height: 85vh; display: flex; flex-direction: column;">
      <div style="padding: 14px 18px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: center;">
        <div style="font-weight: 700; font-size: 15px; color: var(--navy); display: flex; align-items: center; gap: 8px;">
          <span>⌨️</span>
          <span>Brokerage Desk Keyboard Shortcuts &amp; Tally Guide</span>
        </div>
        <kbd style="font-size: 11px;">Esc</kbd>
      </div>

      <div style="padding: 16px 18px; overflow-y: auto; font-size: 13px;">
        <h4 style="font-size: 11.5px; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; font-weight: 700;">Transaction Function Keys</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px;">
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Purchase Voucher</span>
            <kbd>F9 / P</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Sales Voucher</span>
            <kbd>F8 / S</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Change Working Date</span>
            <kbd>F2</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Keyboard Shortcuts</span>
            <kbd>F1</kbd>
          </div>
        </div>

        <h4 style="font-size: 11.5px; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; font-weight: 700;">Gateway Single-Key Shortcuts (From Dashboard)</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px;">
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Purchase Voucher Entry</span>
            <kbd>P</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Sales Voucher Entry</span>
            <kbd>S</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Brokers Directory / Setup</span>
            <kbd>B</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Date-Wise Rate Configurations</span>
            <kbd>R</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Trade Registers &amp; Audit</span>
            <kbd>L</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 7px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Return to Gateway</span>
            <kbd>Esc</kbd>
          </div>
        </div>

        <h4 style="font-size: 11.5px; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; font-weight: 700;">Tally Enter &amp; Escape Behavior</h4>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px;">
          <div style="background: var(--panel-soft); padding: 8px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Next Field Progression</span>
            <kbd>Enter</kbd>
          </div>
          <div style="background: var(--panel-soft); padding: 8px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Confirm Voucher Submission</span>
            <div><kbd>Enter</kbd> or <kbd>Y</kbd></div>
          </div>
          <div style="background: var(--panel-soft); padding: 8px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Cancel Confirm / Blur / Go to Gateway</span>
            <div><kbd>Esc</kbd> or <kbd>N</kbd></div>
          </div>
          <div style="background: var(--panel-soft); padding: 8px 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span>Global Feature Search</span>
            <div><kbd>Ctrl+K</kbd> or <kbd>/</kbd></div>
          </div>
        </div>
      </div>

      <div style="padding: 10px 18px; border-top: 1px solid var(--line); background: var(--panel-soft); display: flex; justify-content: flex-end;">
        <button
          type="button"
          style="padding: 6px 16px; border: 1px solid var(--line-dark); background: var(--panel); color: var(--text); border-radius: 4px; font-weight: 600; cursor: pointer;"
          @click="close"
        >
          Close (Esc)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { globalUiState } from '../../composables/useKeyboardEngine'

const close = () => {
  globalUiState.isHelpOpen.value = false
}
</script>

