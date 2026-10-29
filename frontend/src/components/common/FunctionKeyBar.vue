<template>
  <div id="fkbar">
    <div
      v-for="fk in keys"
      :key="fk.key"
      class="fk"
      @click="triggerKey(fk.key)"
    >
      <b>{{ fk.key }}</b> {{ fk.label }}
    </div>
  </div>
</template>

<script setup>
import { useKeyboardEngine } from '../../composables/useKeyboardEngine'

const { handleFunctionKey, handleEscape } = useKeyboardEngine()

const keys = [
  { key: 'F1', label: 'Help' },
  { key: 'F2', label: 'Date' },
  { key: 'F8', label: 'Sell Entry' },
  { key: 'F9', label: 'Purchase Entry' },
  { key: 'Esc', label: 'Gateway / Quit' },
]

const triggerKey = (key) => {
  if (key === 'Esc') {
    handleEscape()
  } else {
    handleFunctionKey(key)
  }
}
</script>

<style scoped>
#fkbar {
  background: var(--panel);
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  flex-shrink: 0;
  font-size: 12px;
  border-top: 1px solid var(--line);
  user-select: none;
}

.fk {
  color: var(--text);
  padding: 8px 14px;
  cursor: pointer;
  border-right: 1px solid var(--line);
  display: flex;
  gap: 6px;
  align-items: center;
  white-space: nowrap;
  transition: all 0.12s ease;
}

.fk:hover {
  background: var(--blue-soft);
  color: var(--navy);
}

.fk:hover b {
  color: var(--blue);
}

.fk b {
  color: var(--amber);
  font-weight: 700;
  font-family: monospace;
}

body.dark-mode #fkbar {
  background: #0c1527;
  border-top-color: #1e293b;
}

body.dark-mode .fk {
  border-right-color: #1e293b;
}

body.dark-mode .fk:hover {
  background: #1e293b;
  color: #93c5fd;
}
</style>

