<template>
  <div class="typeahead-wrap" ref="wrapRef">
    <div class="input-inner-wrap">
      <input
        ref="inputRef"
        type="text"
        :value="modelValue ? displayLabel : searchQuery"
        :placeholder="placeholder"
        :disabled="disabled"
        autocomplete="off"
        @focus="onFocus"
        @input="onInput"
        @keydown.down.prevent="onKeyDown"
        @keydown.up.prevent="onKeyUp"
        @keydown.enter.prevent="onKeyEnter"
        @keydown.esc="closeDropdown"
      />
      <button
        v-if="modelValue && !disabled"
        type="button"
        class="clear-btn"
        title="Clear selection"
        @click.stop="clearSelection"
      >
        ×
      </button>
      <span v-else class="search-icon">🔍</span>
    </div>

    <!-- Dropdown menu -->
    <div v-if="isOpen && (items.length > 0 || isLoading)" class="dropdown-panel">
      <div v-if="isLoading" class="dropdown-item loading">Searching...</div>
      <template v-else>
        <div
          v-for="(item, idx) in items"
          :key="item.id || item.name || idx"
          class="dropdown-item"
          :class="{ active: idx === activeIndex }"
          @mousedown.prevent="selectItem(item)"
        >
          <div class="item-primary">
            <span class="item-label">{{ item.label || item.name }}</span>
            <span v-if="item.id && item.label !== item.id" class="item-id">({{ item.id }})</span>
          </div>
          <div v-if="item.sub" class="item-sub">{{ item.sub }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Type to search...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  fetchFn: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue', 'update:label', 'change'])

const wrapRef = ref(null)
const inputRef = ref(null)
const isOpen = ref(false)
const searchQuery = ref('')
const displayLabel = ref(props.label || props.modelValue || '')
const items = ref([])
const activeIndex = ref(-1)
const isLoading = ref(false)
let debounceTimer = null

watch(
  () => props.label,
  (val) => {
    displayLabel.value = val || props.modelValue || ''
  }
)

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      displayLabel.value = ''
      searchQuery.value = ''
    }
  }
)

const onFocus = () => {
  if (props.disabled) return
  isOpen.value = true
  fetchData(searchQuery.value)
}

const onInput = (e) => {
  const q = e.target.value
  searchQuery.value = q
  displayLabel.value = ''
  emit('update:modelValue', '')
  emit('update:label', '')
  isOpen.value = true
  activeIndex.value = -1

  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchData(q)
  }, 200)
}

const fetchData = async (q = '') => {
  isLoading.value = true
  try {
    const res = await props.fetchFn(q)
    items.value = res || []
  } catch (err) {
    console.error('Typeahead fetch error:', err)
    items.value = []
  } finally {
    isLoading.value = false
  }
}

const selectItem = (item) => {
  const val = item.id || item.name
  const lbl = item.label || item.name || val
  displayLabel.value = lbl
  searchQuery.value = ''
  emit('update:modelValue', val)
  emit('update:label', lbl)
  emit('change', item)
  closeDropdown()
}

const clearSelection = () => {
  displayLabel.value = ''
  searchQuery.value = ''
  items.value = []
  emit('update:modelValue', '')
  emit('update:label', '')
  emit('change', null)
  closeDropdown()
}

const closeDropdown = () => {
  isOpen.value = false
  activeIndex.value = -1
}

const onKeyDown = () => {
  if (!isOpen.value) {
    isOpen.value = true
    return
  }
  if (items.value.length === 0) return
  activeIndex.value = (activeIndex.value + 1) % items.value.length
}

const onKeyUp = () => {
  if (!isOpen.value) return
  if (items.value.length === 0) return
  activeIndex.value = (activeIndex.value - 1 + items.value.length) % items.value.length
}

const onKeyEnter = () => {
  if (isOpen.value && activeIndex.value >= 0 && items.value[activeIndex.value]) {
    selectItem(items.value[activeIndex.value])
  } else if (!isOpen.value) {
    isOpen.value = true
    fetchData('')
  }
}

const handleClickOutside = (e) => {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

defineExpose({
  focus: () => inputRef.value?.focus(),
})
</script>

<style scoped>
.typeahead-wrap {
  position: relative;
  width: 100%;
}

.input-inner-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-inner-wrap input {
  width: 100%;
  padding-right: 32px;
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
  padding: 2px 6px;
  border-radius: 4px;
}
.clear-btn:hover {
  color: #334155;
  background: #f1f5f9;
}

.search-icon {
  position: absolute;
  right: 10px;
  font-size: 12px;
  color: #94a3b8;
  pointer-events: none;
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  max-height: 240px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.1s ease;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover,
.dropdown-item.active {
  background: #eff6ff;
}

.dropdown-item.loading {
  color: #64748b;
  font-size: 12px;
  text-align: center;
  cursor: default;
}

.item-primary {
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.item-id {
  font-size: 11px;
  color: #64748b;
  font-family: var(--font-mono);
}

.item-sub {
  font-size: 11.5px;
  color: #64748b;
  margin-top: 2px;
}
</style>
