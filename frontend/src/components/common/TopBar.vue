<template>
  <div id="topbar">
    <div class="brand" @click="router.push('/')" style="cursor: pointer;" title="Go to Gateway of Brokerage">
      <div class="brand-badge">
        ⚖️
      </div>
      <strong>BROKERAGE DESK</strong>
      <span>· {{ companyName }}</span>
    </div>

    <!-- Global Feature Search Bar -->
    <div class="global-search-container" ref="searchContainerRef">
      <div class="search-input-wrapper" :class="{ 'is-focused': isSearchOpen }">
        <span class="search-icon">🔍</span>
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          placeholder="Search vouchers, brokers, rates... (Ctrl+K or /)"
          class="global-search-input"
          @focus="openSearch"
          @input="onSearchInput"
          @keydown="handleSearchKeyDown"
        />
        <div v-if="!searchQuery" class="search-hotkey-badge" @click="openSearch">
          <kbd>Ctrl+K</kbd>
        </div>
        <button
          v-else
          type="button"
          class="search-clear-btn"
          title="Clear search"
          @click="clearSearch"
        >
          ✕
        </button>
      </div>

      <!-- Floating Command Palette / Results Dropdown -->
      <div v-if="isSearchOpen" class="search-dropdown-menu">
        <div class="search-dropdown-header">
          <span>{{ filteredFeatures.length }} feature{{ filteredFeatures.length !== 1 ? 's' : '' }} found</span>
          <span class="search-nav-hint"><kbd>↑</kbd> <kbd>↓</kbd> navigate · <kbd>Enter</kbd> open · <kbd>Esc</kbd> close</span>
        </div>

        <div v-if="filteredFeatures.length === 0" class="search-empty-state">
          No matching features found for "<b>{{ searchQuery }}</b>"
        </div>

        <div v-else class="search-results-list" ref="resultsListRef">
          <div
            v-for="(item, idx) in filteredFeatures"
            :key="item.id || item.title"
            class="search-item"
            :class="{ active: idx === selectedIndex }"
            @mouseenter="selectedIndex = idx"
            @click="executeFeature(item)"
          >
            <div class="item-icon-col">{{ item.icon }}</div>
            <div class="item-info-col">
              <div class="item-title-row">
                <span class="item-title">{{ item.title }}</span>
                <span class="item-category-tag" :class="item.categoryClass">{{ item.category }}</span>
              </div>
              <div class="item-desc">{{ item.description }}</div>
            </div>
            <div v-if="item.shortcut" class="item-shortcut-col">
              <kbd>{{ item.shortcut }}</kbd>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="meta">
      <span class="user-name">👤 {{ userName }}</span>
      <span class="today-date">📅 {{ formattedDate }}</span>

      <!-- ERPNext Workspace Link -->
      <button
        class="admin-desk-btn"
        title="Go to ERPNext Brokerage Workspace"
        @click="goToErpNext"
      >
        <span class="admin-label">🏛️ Workspace</span>
      </button>

      <!-- Dark / Light Mode Toggle Button -->
      <button
        class="theme-toggle-btn"
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        @click="toggleTheme"
      >
        <span v-if="isDarkMode" class="theme-label">☀️ Light</span>
        <span v-else class="theme-label">🌙 Dark</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { bootState } from '../../composables/useFrappeApi'
import { globalUiState, openGlobalBrokerModal, openGlobalRateModal, showToast } from '../../composables/useKeyboardEngine'
import { useTheme } from '../../composables/useTheme'

const router = useRouter()
const { isDarkMode, toggleTheme } = useTheme()

const companyName = computed(() => {
  return bootState.defaultCompany || 'Rajendra Narahari Lokhande'
})

const userName = computed(() => {
  return bootState.fullName || bootState.user || 'Administrator'
})

const formattedDate = computed(() => {
  const d = bootState.today ? new Date(bootState.today) : new Date()
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
})

const goToErpNext = () => {
  window.location.href = '/desk/brokerage-module'
}

// Global Feature Registry
const searchQuery = ref('')
const isSearchOpen = ref(false)
const selectedIndex = ref(0)
const searchInputRef = ref(null)
const searchContainerRef = ref(null)
const resultsListRef = ref(null)

const allFeatures = [
  {
    id: 'voucher-purchase',
    title: 'Purchase Voucher Entry',
    category: 'Voucher',
    categoryClass: 'badge-blue',
    description: 'Purchase trade entry with auto broker calculation (% / Per Bag / Per Qtl)',
    route: '/purchase',
    shortcut: 'F9 / P',
    icon: '🛒',
    keywords: 'purchase entry voucher f9 p buy broker commodity',
  },
  {
    id: 'voucher-sell',
    title: 'Sales Voucher Entry',
    category: 'Voucher',
    categoryClass: 'badge-amber',
    description: 'Sales trade entry with auto broker commission terms',
    route: '/sell',
    shortcut: 'F8 / S',
    icon: '🏷️',
    keywords: 'sales sell entry voucher f8 s customer buyer broker',
  },
  {
    id: 'masters-brokers',
    title: 'Brokers Directory & Setup',
    category: 'Master',
    categoryClass: 'badge-green',
    description: 'View and manage brokers with purchase/sell checkboxes & default item rates',
    route: '/brokers',
    shortcut: 'B',
    icon: '👥',
    keywords: 'brokers list master directory setup add create',
  },
  {
    id: 'action-new-broker',
    title: 'Create New Broker Master (Full Screen)',
    category: 'Action',
    categoryClass: 'badge-green',
    description: 'Add a new broker with full screen table and commodity presets',
    action: () => openGlobalBrokerModal(''),
    icon: '➕',
    keywords: 'create add new broker modal screen master',
  },
  {
    id: 'masters-rates',
    title: 'Date-Wise Rate Configurations',
    category: 'Master',
    categoryClass: 'badge-blue',
    description: 'Maintain date-effective broker rates with automatic priority overrides',
    route: '/rate-configs',
    shortcut: 'R',
    icon: '📅',
    keywords: 'rate configs date wise rates pricing cards rules',
  },
  {
    id: 'action-new-rate',
    title: 'Create Date-Wise Rate Config (Full Screen)',
    category: 'Action',
    categoryClass: 'badge-blue',
    description: 'Add a date-effective pricing rule for a broker',
    action: () => openGlobalRateModal(''),
    icon: '⚡',
    keywords: 'create rate card config date effective',
  },
  {
    id: 'registers-sales-outstanding',
    title: 'Sales Outstanding Register',
    category: 'Register',
    categoryClass: 'badge-amber',
    description: 'Audit pending sales trade collections and broker commission outstandings',
    route: '/registers?type=SalesOutstanding',
    shortcut: 'O',
    icon: '⚠️',
    keywords: 'sales outstanding sell dues pending receivables commission balance ageing',
  },
  {
    id: 'registers-all',
    title: 'Unified Trade Registers',
    category: 'Register',
    categoryClass: 'badge-teal',
    description: 'Full purchase and sales registers with audit totals and export',
    route: '/registers',
    shortcut: 'L',
    icon: '📋',
    keywords: 'registers reports list audit purchase sales daybook',
  },
  {
    id: 'tool-date',
    title: 'Set Working Date',
    category: 'Tool',
    categoryClass: 'badge-blue',
    description: 'Set system posting date for new vouchers',
    action: () => { globalUiState.isDateModalOpen.value = true },
    shortcut: 'F2',
    icon: '📅',
    keywords: 'date set change working date f2 calendar',
  },
  {
    id: 'tool-help',
    title: 'Keyboard Shortcuts & Guide',
    category: 'Tool',
    categoryClass: 'badge-blue',
    description: 'View full guide of Tally shortcuts, Enter progression, and Esc behavior',
    action: () => { globalUiState.isHelpOpen.value = true },
    shortcut: 'F1',
    icon: '❓',
    keywords: 'help shortcuts f1 tally enter esc guide keys',
  },
  {
    id: 'tool-theme',
    title: 'Toggle Dark / Light Theme',
    category: 'Tool',
    categoryClass: 'badge-blue',
    description: 'Switch between Dark Mode and classic Tally light theme',
    action: () => toggleTheme(),
    icon: '🌓',
    keywords: 'theme dark mode light mode appearance color',
  },
  {
    id: 'nav-gateway',
    title: 'Gateway of Brokerage Desk',
    category: 'Navigation',
    categoryClass: 'badge-blue',
    description: 'Return to the main Gateway dashboard',
    route: '/',
    shortcut: 'Esc',
    icon: '🏛️',
    keywords: 'gateway home dashboard exit main esc',
  },
]

const filteredFeatures = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return allFeatures
  return allFeatures.filter((item) => {
    return (
      item.title.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.keywords.toLowerCase().includes(q) ||
      (item.shortcut && item.shortcut.toLowerCase().includes(q))
    )
  })
})

const openSearch = () => {
  isSearchOpen.value = true
  selectedIndex.value = 0
  nextTick(() => {
    if (searchInputRef.value) searchInputRef.value.focus()
  })
}

const closeSearch = () => {
  isSearchOpen.value = false
}

const clearSearch = () => {
  searchQuery.value = ''
  if (searchInputRef.value) searchInputRef.value.focus()
}

const onSearchInput = () => {
  isSearchOpen.value = true
  selectedIndex.value = 0
}

const executeFeature = (item) => {
  closeSearch()
  searchQuery.value = ''
  if (item.action) {
    item.action()
  } else if (item.route) {
    router.push(item.route)
  }
}

const handleSearchKeyDown = (e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (filteredFeatures.value.length > 0) {
      selectedIndex.value = (selectedIndex.value + 1) % filteredFeatures.value.length
      scrollToSelected()
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (filteredFeatures.value.length > 0) {
      selectedIndex.value = (selectedIndex.value - 1 + filteredFeatures.value.length) % filteredFeatures.value.length
      scrollToSelected()
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (filteredFeatures.value[selectedIndex.value]) {
      executeFeature(filteredFeatures.value[selectedIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    closeSearch()
  }
}

const scrollToSelected = () => {
  nextTick(() => {
    if (!resultsListRef.value) return
    const activeEl = resultsListRef.value.querySelector('.search-item.active')
    if (activeEl) {
      activeEl.scrollIntoView({ block: 'nearest' })
    }
  })
}

const handleDocumentClick = (e) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target)) {
    closeSearch()
  }
}

const onGlobalSearchTriggered = () => {
  openSearch()
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  window.addEventListener('focus-global-search', onGlobalSearchTriggered)
  window.addEventListener('close-global-search', closeSearch)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('focus-global-search', onGlobalSearchTriggered)
  window.removeEventListener('close-global-search', closeSearch)
})
</script>

<style scoped>
#topbar {
  background: var(--navy);
  color: #fff;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13.5px;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  user-select: none;
}

.brand {
  font-weight: 700;
  letter-spacing: 0.4px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-badge {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}

.brand span {
  color: #9fb8e8;
  font-weight: 400;
  font-size: 12.5px;
}

.global-search-container {
  flex: 1;
  max-width: 480px;
  margin: 0 16px;
  position: relative;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 6px;
  padding: 2px 10px;
  transition: all 0.15s ease;
  height: 30px;
}

.search-input-wrapper.is-focused,
.search-input-wrapper:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.45);
}

.search-input-wrapper.is-focused {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35);
}

.search-icon {
  font-size: 12px;
  margin-right: 6px;
  opacity: 0.75;
}

.global-search-input {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #ffffff !important;
  font-size: 12.5px !important;
  width: 100%;
  padding: 0 !important;
  outline: none;
}

.global-search-input::placeholder {
  color: rgba(255, 255, 255, 0.65) !important;
}

.search-hotkey-badge {
  cursor: pointer;
  margin-left: 6px;
  opacity: 0.85;
}

.search-hotkey-badge kbd {
  font-size: 10px;
  padding: 1px 5px;
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.28);
}

.search-clear-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  padding: 0 4px;
}

.search-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--panel);
  border: 1px solid var(--blue);
  border-radius: 8px;
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.3);
  z-index: 10000;
  max-height: 380px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalPop 0.12s ease-out;
}

.search-dropdown-header {
  padding: 7px 12px;
  background: var(--panel-soft);
  border-bottom: 1px solid var(--line);
  font-size: 11px;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-nav-hint kbd {
  font-size: 10px;
  padding: 1px 4px;
}

.search-results-list {
  overflow-y: auto;
  max-height: 320px;
}

.search-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid var(--line);
  color: var(--text);
  transition: background 0.1s ease;
}

.search-item:last-child {
  border-bottom: none;
}

.search-item.active,
.search-item:hover {
  background: var(--blue-soft);
  color: var(--navy);
}

.item-icon-col {
  font-size: 16px;
  flex-shrink: 0;
}

.item-info-col {
  flex: 1;
  min-width: 0;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-title {
  font-weight: 600;
  font-size: 13px;
}

.item-desc {
  font-size: 11.5px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}

.item-category-tag {
  font-size: 9.5px;
  padding: 1px 5px;
  border-radius: 3px;
  font-weight: 700;
  text-transform: uppercase;
}

.item-shortcut-col {
  flex-shrink: 0;
}

.search-empty-state {
  padding: 24px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #c7d5f0;
}

.admin-desk-btn,
.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.admin-desk-btn:hover,
.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.4);
}
</style>

