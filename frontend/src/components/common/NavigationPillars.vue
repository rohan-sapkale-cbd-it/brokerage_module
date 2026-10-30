<template>
  <div id="sub-nav-bar">
    <!-- 3 Core Section Tabs -->
    <div class="mode-tabs">
      <button
        type="button"
        class="mode-btn"
        :class="{ active: currentSection === 'operations' }"
        title="Operations: Purchase & Sales Voucher Entries"
        @click="selectSection('operations')"
      >
        <span>⚡ Operations</span>
      </button>

      <button
        type="button"
        class="mode-btn"
        :class="{ active: currentSection === 'registers' }"
        title="Trade Registers & Day Logs"
        @click="selectSection('registers')"
      >
        <span>📋 Registers</span>
      </button>

      <button
        type="button"
        class="mode-btn"
        :class="{ active: currentSection === 'masters' }"
        title="Brokers Directory & Date-Wise Rates"
        @click="selectSection('masters')"
      >
        <span>🏢 Masters</span>
      </button>
    </div>

    <div class="divider-v"></div>

    <!-- Contextual Sub-Items for Active Section -->
    <div class="sub-links-wrap">
      <!-- Sub-items for OPERATIONS -->
      <template v-if="currentSection === 'operations'">
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/purchase' }"
          @click="navigate('/purchase')"
        >
          <span>Purchase Entry</span>
          <kbd>F9</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/sell' }"
          @click="navigate('/sell')"
        >
          <span>Sell Entry</span>
          <kbd>F8</kbd>
        </button>
      </template>

      <!-- Sub-items for REGISTERS -->
      <template v-else-if="currentSection === 'registers'">
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/registers' && (route.query.type === 'Purchase' || !route.query.type) }"
          @click="navigate('/registers?type=Purchase')"
        >
          <span>Purchase Register</span>
          <kbd>P</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/registers' && (route.query.type === 'Sales' || route.query.type === 'Sell') }"
          @click="navigate('/registers?type=Sales')"
        >
          <span>Sales Register</span>
          <kbd>S</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/registers' && (route.query.type === 'ItemWise' || route.query.type === 'item-wise') }"
          @click="navigate('/registers?type=ItemWise')"
        >
          <span>Item-Wise Register</span>
          <kbd>I</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.query.type === 'SalesOutstanding' || route.path === '/sales-outstanding' }"
          @click="navigate('/registers?type=SalesOutstanding')"
        >
          <span>Sales Outstanding</span>
          <kbd>O</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/registers' && !route.query.type }"
          @click="navigate('/registers')"
        >
          <span>All Registers</span>
          <kbd>L</kbd>
        </button>
      </template>

      <!-- Sub-items for MASTERS -->
      <template v-else-if="currentSection === 'masters'">
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/brokers' }"
          @click="navigate('/brokers')"
        >
          <span>Brokers Directory</span>
          <kbd>B</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/items' }"
          @click="navigate('/items')"
        >
          <span>Items &amp; Stock Groups</span>
          <kbd>I</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          :class="{ active: route.path === '/rate-configs' }"
          @click="navigate('/rate-configs')"
        >
          <span>Rate Configurations</span>
          <kbd>R</kbd>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          style="color: var(--green); font-weight: 700;"
          @click="openGlobalBrokerModal('')"
        >
          <span>+ New Broker (Full Screen)</span>
        </button>
        <button
          type="button"
          class="sub-link-btn"
          style="color: var(--blue); font-weight: 700;"
          @click="openGlobalRateModal('')"
        >
          <span>+ New Rate Card</span>
        </button>
      </template>
    </div>

    <!-- Gateway Home Shortcut -->
    <div class="home-btn-wrap">
      <button
        type="button"
        class="home-btn"
        :class="{ active: route.path === '/' }"
        title="Gateway of Brokerage (Esc)"
        @click="navigate('/')"
      >
        <span>🏛️ Gateway</span>
        <kbd>Esc</kbd>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { openGlobalBrokerModal, openGlobalRateModal } from '../../composables/useKeyboardEngine'

const route = useRoute()
const router = useRouter()

const currentSection = computed(() => {
  const p = route.path
  if (p === '/purchase' || p === '/sell') return 'operations'
  if (p.startsWith('/registers')) return 'registers'
  if (p.startsWith('/brokers') || p.startsWith('/rate-configs')) return 'masters'
  return 'operations'
})

const navigate = (path) => {
  if (route.fullPath === path) return
  router.push(path)
}

const selectSection = (sec) => {
  if (sec === 'operations') {
    if (route.path === '/purchase' || route.path === '/sell') return
    navigate('/purchase')
  } else if (sec === 'registers') {
    if (route.path.startsWith('/registers')) return
    navigate('/registers')
  } else if (sec === 'masters') {
    if (route.path.startsWith('/brokers') || route.path.startsWith('/rate-configs')) return
    navigate('/brokers')
  }
}
</script>

<style scoped>
#sub-nav-bar {
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  padding: 4px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 36px;
  flex-shrink: 0;
  user-select: none;
  font-size: 12px;
  z-index: 90;
}

.mode-tabs {
  display: flex;
  align-items: center;
  gap: 3px;
  background: var(--panel-soft, #f1f5f9);
  padding: 2px;
  border-radius: 5px;
  border: 1px solid var(--line);
  flex-shrink: 0;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 4px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--muted);
  font-weight: 700;
  font-size: 11.5px;
  cursor: pointer;
  transition: all 0.12s ease;
  white-space: nowrap;
}

.mode-btn:hover {
  color: var(--navy);
}

.mode-btn.active {
  background: #ffffff;
  color: var(--blue, #2563eb);
  border-color: rgba(37, 99, 235, 0.2);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

body.dark-mode .mode-btn.active {
  background: #1e293b;
  color: #60a5fa;
  border-color: #3b82f6;
}

.divider-v {
  width: 1px;
  height: 18px;
  background: var(--line);
  flex-shrink: 0;
}

.sub-links-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
  overflow-x: auto;
  flex: 1;
  padding: 1px 0;
  scrollbar-width: none;
}

.sub-links-wrap::-webkit-scrollbar {
  display: none;
}

.sub-link-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.12s ease;
}

.sub-link-btn:hover {
  background: var(--blue-soft, #eff6ff);
  color: var(--blue, #2563eb);
}

.sub-link-btn.active {
  background: var(--navy, #1e3a8a);
  color: #ffffff;
  font-weight: 700;
}

.sub-link-btn kbd {
  font-size: 10px;
  padding: 0 4px;
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.1);
  color: inherit;
}

.sub-link-btn.active kbd {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.home-btn-wrap {
  flex-shrink: 0;
}

.home-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 4px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--navy);
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.12s ease;
}

.home-btn:hover {
  background: var(--blue-soft);
  border-color: var(--blue);
}

.home-btn.active {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}

.home-btn kbd {
  font-size: 10px;
  padding: 0 4px;
}
</style>

