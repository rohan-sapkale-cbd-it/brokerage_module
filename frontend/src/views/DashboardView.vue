<template>
  <div id="main-layout">
    <div id="content-area">
      <div style="max-width: 900px; padding: 4px 0 20px;">
        <!-- Header -->
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: var(--navy); color: #fff; width: 42px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.15);">
              ⚖️
            </div>
            <div>
              <h2 style="font-size: 17px; color: var(--navy); margin-bottom: 2px; font-weight: 700;">Gateway of Brokerage Module</h2>
              <p style="font-size: 12.5px; color: var(--muted);">Fast keyboard commodity purchase &amp; sell vouchers with automated broker commission desk</p>
            </div>
          </div>

          <div class="category-toggle-group">
            <button
              type="button"
              class="cat-toggle-btn"
              :class="{ active: activeFilter === 'all' }"
              @click="activeFilter = 'all'"
            >
              All
            </button>
            <button
              type="button"
              class="cat-toggle-btn"
              :class="{ active: activeFilter === 'operations' }"
              @click="activeFilter = 'operations'"
            >
              ⚡ Operations
            </button>
            <button
              type="button"
              class="cat-toggle-btn"
              :class="{ active: activeFilter === 'registers' }"
              @click="activeFilter = 'registers'"
            >
              📋 Registers
            </button>
            <button
              type="button"
              class="cat-toggle-btn"
              :class="{ active: activeFilter === 'masters' }"
              @click="activeFilter = 'masters'"
            >
              🏢 Masters
            </button>
          </div>
        </div>

        <!-- 1. OPERATIONS (Daily Trade Vouchers) -->
        <div v-if="activeFilter === 'all' || activeFilter === 'operations'" class="dashboard-section">
          <div class="section-heading">
            <span class="section-title">⚡ Operations &amp; Vouchers</span>
            <span class="section-tag">Direct Entries</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">
            <div class="feature-card" @click="router.push('/purchase')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--blue);">Purchase Voucher 🛒</div>
                  <div class="card-title">{{ stats.purchase.count || 0 }} Entries (₹{{ formatCurrency(stats.purchase.total_trade) }})</div>
                  <div class="card-desc">Sole broker entity with auto-applied commission rates</div>
                </div>
                <kbd>F9 / P</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/sell')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--green);">Sales Voucher 🏷️</div>
                  <div class="card-title">{{ stats.sales.count || 0 }} Entries (₹{{ formatCurrency(stats.sales.total_trade) }})</div>
                  <div class="card-desc">Sales trade entry with auto-price terms &amp; bags count</div>
                </div>
                <kbd>F8 / S</kbd>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. REGISTERS & AUDIT -->
        <div v-if="activeFilter === 'all' || activeFilter === 'registers'" class="dashboard-section">
          <div class="section-heading">
            <span class="section-title">📋 Trade Registers &amp; Brokerage Audit</span>
            <span class="section-tag">Audit Registers</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px;">
            <div class="feature-card" style="border-color: #fde68a; background: #fff8eb;" @click="router.push('/registers?type=SalesOutstanding')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: #b45309;">Sales Outstandings ⚠️</div>
                  <div class="card-title" style="color: #d97706;">₹{{ formatCurrency(outStats.total_brokerage_outstanding) }}</div>
                  <div class="card-desc">{{ outStats.pending_vouchers }} pending · ₹{{ formatCurrency(outStats.total_trade_outstanding) }} trade</div>
                </div>
                <kbd style="background: #fff; color: #b45309; border-color: #fde68a;">O</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/registers?type=Purchase')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--blue);">Purchase Register</div>
                  <div class="card-title">₹{{ formatCurrency(stats.purchase.total_brokerage) }}</div>
                  <div class="card-desc">Purchase commission log</div>
                </div>
                <kbd>P</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/registers?type=Sales')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--green);">Sales Register</div>
                  <div class="card-title">₹{{ formatCurrency(stats.sales.total_brokerage) }}</div>
                  <div class="card-desc">Sales commission log</div>
                </div>
                <kbd>S</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/registers')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--teal);">Total Brokerage</div>
                  <div class="card-title">₹{{ formatCurrency((stats.purchase.total_brokerage || 0) + (stats.sales.total_brokerage || 0)) }}</div>
                  <div class="card-desc">Combined audit totals</div>
                </div>
                <kbd>L</kbd>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. MASTERS & CONFIGURATIONS -->
        <div v-if="activeFilter === 'all' || activeFilter === 'masters'" class="dashboard-section">
          <div class="section-heading">
            <span class="section-title">🏢 Master Directories &amp; Date-Wise Rates</span>
            <span class="section-tag">Rate Cards</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
            <div class="feature-card" @click="router.push('/brokers')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--navy);">Brokers Directory 👥</div>
                  <div class="card-title">{{ stats.brokers.total || 0 }} Active Brokers</div>
                  <div class="card-desc">🛒 {{ stats.brokers.purchase || 0 }} Purchase · 🏷️ {{ stats.brokers.sales || 0 }} Sell</div>
                </div>
                <kbd>B</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/items')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--teal);">Commodities &amp; Groups 🌾</div>
                  <div class="card-title">Stock Groups &amp; GST</div>
                  <div class="card-desc">Unified brokerage inheritance by Stock Group</div>
                </div>
                <kbd>I</kbd>
              </div>
            </div>

            <div class="feature-card" @click="router.push('/rate-configs')">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div class="card-subtitle" style="color: var(--amber);">Date-Wise Rate Cards 📅</div>
                  <div class="card-title">Effective Pricing Rules</div>
                  <div class="card-desc">Separate date-effective DocType records</div>
                </div>
                <kbd>R</kbd>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Info -->
        <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 10px 16px; font-size: 12px; color: var(--muted); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
          <div style="display: flex; gap: 18px; flex-wrap: wrap;">
            <div>🏢 <strong>Company:</strong> {{ defaultCompany }}</div>
            <div>👤 <strong>User:</strong> {{ currentUser }}</div>
            <div>🔄 Connected with Frappe DB (Brokerage Module)</div>
          </div>
          <div>
            <kbd>Esc</kbd> Returns to Gateway from any view
          </div>
        </div>
      </div>
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Gateway of Brokerage"
      :items="menuItems"
      :active-index="activeIndex"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi, bootState } from '../composables/useFrappeApi'
import { openGlobalBrokerModal, openGlobalRateModal, showToast } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getDashboardSummary, getSalesOutstandingRegister } = useFrappeApi()

const defaultCompany = computed(() => bootState.defaultCompany || 'Rajendra Narahari Lokhande')
const currentUser = computed(() => bootState.fullName || bootState.user || 'Administrator')

const activeIndex = ref(1)
const activeFilter = ref('all')

const stats = reactive({
  brokers: { total: 0, purchase: 0, sales: 0 },
  purchase: { count: 0, total_trade: 0, total_brokerage: 0 },
  sales: { count: 0, total_trade: 0, total_brokerage: 0 },
})

const outStats = reactive({
  total_trade_outstanding: 0,
  total_brokerage_outstanding: 0,
  pending_vouchers: 0,
})

const loadStats = async () => {
  try {
    const data = await getDashboardSummary()
    if (data) {
      stats.brokers = data.brokers || stats.brokers
      stats.purchase = data.purchase || stats.purchase
      stats.sales = data.sales || stats.sales
    }

    const outData = await getSalesOutstandingRegister({ limit: 1 })
    if (outData && outData.summary) {
      outStats.total_trade_outstanding = outData.summary.total_trade_outstanding || 0
      outStats.total_brokerage_outstanding = outData.summary.total_brokerage_outstanding || 0
      outStats.pending_vouchers = outData.summary.pending_vouchers || 0
    }
  } catch (e) {
    console.error('Failed to load dashboard stats:', e)
  }
}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Right-Side Gateway Menu Items
const menuItems = [
  // 1. OPERATIONS
  { isHeader: true, label: '⚡ OPERATIONS' },
  { key: 'P', label: 'Purchase Voucher Entry (F9)', action: () => router.push('/purchase') },
  { key: 'S', label: 'Sales Voucher Entry (F8)', action: () => router.push('/sell') },

  // 2. REGISTERS
  { isHeader: true, label: '📋 REGISTERS' },
  { key: 'O', label: 'Sales Outstanding Register (Due)', action: () => router.push('/registers?type=SalesOutstanding') },
  { key: 'L', label: 'All Trade Registers', action: () => router.push('/registers') },
  { key: 'U', label: 'Purchase Register', action: () => router.push('/registers?type=Purchase') },
  { key: 'K', label: 'Sales Register', action: () => router.push('/registers?type=Sales') },

  // 3. MASTERS
  { isHeader: true, label: '🏢 MASTERS' },
  { key: 'B', label: 'Brokers Directory', action: () => router.push('/brokers') },
  { key: 'I', label: 'Commodities & Stock Groups', action: () => router.push('/items') },
  { key: 'N', label: '+ New Broker (Full Screen)', action: () => openGlobalBrokerModal('') },
  { key: 'R', label: 'Date-Wise Rate Configs', action: () => router.push('/rate-configs') },
  { key: 'C', label: '+ New Rate Card', action: () => openGlobalRateModal('') },

  // 4. SYSTEM
  { isHeader: true, label: '⚙️ SYSTEM' },
  { key: 'F2', label: 'Set Working Date', action: () => { window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F2' })) } },
  { key: 'F1', label: 'Help & Shortcuts Guide', action: () => { window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1' })) } },
  { key: 'Q', label: 'Refresh Dashboard', action: () => { loadStats(); showToast('Dashboard refreshed') } },
]

const handleSelect = (idx) => {
  if (menuItems[idx].isHeader) return
  activeIndex.value = idx
  menuItems[idx].action()
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    let next = (activeIndex.value + 1) % menuItems.length
    while (menuItems[next].isHeader) {
      next = (next + 1) % menuItems.length
    }
    activeIndex.value = next
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    let prev = (activeIndex.value - 1 + menuItems.length) % menuItems.length
    while (menuItems[prev].isHeader) {
      prev = (prev - 1 + menuItems.length) % menuItems.length
    }
    activeIndex.value = prev
  } else if (e.key === 'Enter') {
    e.preventDefault()
    handleSelect(activeIndex.value)
  }
}

onMounted(() => {
  loadStats()
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('broker-master-updated', loadStats)
  window.addEventListener('rate-config-updated', loadStats)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('broker-master-updated', loadStats)
  window.removeEventListener('rate-config-updated', loadStats)
})
</script>

<style scoped>
.dashboard-section {
  margin-bottom: 14px;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.section-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--navy);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-tag {
  font-size: 10px;
  font-weight: 700;
  background: var(--blue-soft);
  color: var(--blue);
  padding: 1px 6px;
  border-radius: 3px;
}

.category-toggle-group {
  display: flex;
  gap: 3px;
  background: var(--panel-soft);
  padding: 2px;
  border-radius: 5px;
  border: 1px solid var(--line);
}

.cat-toggle-btn {
  padding: 4px 10px;
  font-size: 11.5px;
  font-weight: 600;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

.cat-toggle-btn:hover {
  color: var(--navy);
}

.cat-toggle-btn.active {
  background: #ffffff;
  color: var(--blue);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

body.dark-mode .cat-toggle-btn.active {
  background: #1e293b;
  color: #60a5fa;
}
</style>
