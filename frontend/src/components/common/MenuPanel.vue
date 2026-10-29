<template>
  <div id="menu-panel">
    <div class="menu-section-label">{{ sectionTitle }}</div>
    <template v-for="(item, idx) in items" :key="idx">
      <div v-if="item.isHeader" class="menu-group-header">
        {{ item.label }}
      </div>
      <div
        v-else
        :class="['menu-item', { active: activeIndex === idx }]"
        @click="$emit('select', idx)"
      >
        <span class="key">{{ item.key }}</span>
        <span class="label">{{ item.label }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  sectionTitle: {
    type: String,
    default: 'Gateway of Brokerage',
  },
  items: {
    type: Array,
    default: () => [],
  },
  activeIndex: {
    type: Number,
    default: 0,
  },
})

defineEmits(['select'])
</script>

<style scoped>
#menu-panel {
  width: 270px;
  border-left: 1px solid var(--line);
  background: var(--panel);
  padding: 12px 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  user-select: none;
}

.menu-section-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--muted);
  padding: 8px 18px 6px;
  font-weight: 700;
}

.menu-group-header {
  font-size: 10.5px;
  font-weight: 800;
  color: var(--blue, #2563eb);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 10px 18px 4px;
  border-top: 1px solid var(--line);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--panel-soft, transparent);
}

.menu-group-header:first-of-type {
  border-top: none;
  margin-top: 0;
}

.menu-item {
  padding: 8px 18px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text);
  border-left: 3px solid transparent;
  transition: background 0.12s ease;
}

.menu-item:hover {
  background: #f0f4fa;
}

.menu-item .key {
  color: var(--amber);
  font-weight: 700;
  min-width: 28px;
  font-family: monospace;
  font-size: 13px;
}

.menu-item.active {
  background: var(--blue-soft);
  color: var(--navy);
  border-left: 3px solid var(--blue);
  font-weight: 600;
}

.menu-item.active .key {
  color: var(--blue);
}

body.dark-mode #menu-panel {
  background: var(--panel);
  border-left-color: var(--line);
}

body.dark-mode .menu-group-header {
  color: #60a5fa;
  border-top-color: #1e293b;
}

body.dark-mode .menu-item:hover {
  background: #16223b;
  color: #ffffff;
}

body.dark-mode .menu-item.active {
  background: #1e293b;
  color: #93c5fd;
  border-left-color: #3b82f6;
}
</style>

