<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="content-card">
        <!-- Header -->
        <div class="page-header items-page-header">
          <div>
            <div class="page-title">
              <span>🌾 Commodity &amp; Stock Group Masters</span>
              <span class="badge badge-blue">{{ items.length }} Items</span>
              <span class="badge badge-purple">{{ stockGroups.length }} Groups</span>
            </div>
            <div class="page-subtitle">
              Every item belongs to a Stock Group (e.g. Sugar). In Broker Master, brokerage terms are assigned per Stock Group and automatically inherited during Purchase &amp; Sell.
            </div>
          </div>

          <div class="items-header-actions">
            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="openStockGroupModal(null)"
            >
              📦 + New Stock Group (<kbd>G</kbd>)
            </button>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              style="font-weight: 700;"
              @click="openItemModal(null)"
            >
              🌾 + Add Commodity / Item (<kbd>N</kbd>)
            </button>
          </div>
        </div>

        <!-- Filter & Search Toolbar -->
        <div class="items-filter-bar">
          <div class="filter-search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by commodity name, code, HSN, or description... (Press / to focus)"
              @input="onFilterChange"
            />
            <span class="search-icon">🔍</span>
          </div>

          <div class="filter-group-select">
            <label>Stock Group:</label>
            <select
              v-model="selectedGroupFilter"
              @change="onFilterChange"
            >
              <option value="">All Groups ({{ items.length }})</option>
              <option v-for="g in stockGroups" :key="g.name" :value="g.name">
                {{ g.stock_group_name || g.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Stock Group Quick Stats Bar -->
        <div class="stock-groups-bar">
          <div
            v-for="g in stockGroups"
            :key="g.name"
            class="stock-group-chip"
            :class="{ active: selectedGroupFilter === g.name }"
            @click="filterByGroup(g.name)"
          >
            <span class="chip-name">{{ g.stock_group_name || g.name }}</span>
            <span class="badge badge-blue" style="font-size: 10px;">GST {{ g.default_gst_rate || 5 }}%</span>
            <span class="chip-count">({{ g.item_count || 0 }} items)</span>
            <button
              type="button"
              class="chip-edit-btn"
              title="Edit Stock Group"
              @click.stop="openStockGroupModal(g)"
            >
              ✏️
            </button>
          </div>
        </div>

        <!-- Mobile Scroll Cue Banner -->
        <div class="mobile-scroll-cue">
          <span class="cue-icon">↔</span>
          <span>Scroll horizontally to view all commodity details</span>
        </div>

        <!-- Table View -->
        <div v-if="loading" class="empty-state-box">
          ⏳ Loading commodities &amp; items...
        </div>

        <div v-else-if="filteredItems.length === 0" class="empty-state-box">
          <div style="font-size: 38px; margin-bottom: 8px;">🌾</div>
          <div style="font-weight: 700; font-size: 15px; color: #334155;">No Commodities Found</div>
          <div style="font-size: 13px; margin-top: 4px;">Click <strong>"+ Add Commodity / Item"</strong> to create your first stock item.</div>
        </div>

        <div v-else class="items-table-wrapper">
          <table class="data-table items-data-table">
            <thead>
              <tr>
                <th style="width: 40px; text-align: center;">#</th>
                <th style="min-width: 130px;">Item Code / ID</th>
                <th style="min-width: 180px;">Commodity / Item Name</th>
                <th style="min-width: 95px;">HSN Code</th>
                <th style="min-width: 130px;">Stock Group</th>
                <th style="min-width: 90px;">Stock UOM</th>
                <th style="min-width: 140px;">GST Rate (CGST + SGST)</th>
                <th style="min-width: 110px; text-align: right;">Std Rate (₹)</th>
                <th style="min-width: 150px;">Description / Packaging</th>
                <th style="min-width: 80px; text-align: center;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(it, idx) in filteredItems"
                :key="it.name"
                style="cursor: pointer;"
                @click="openItemModal(it)"
              >
                <td style="text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">
                  {{ idx + 1 }}
                </td>

                <td style="font-weight: 700; color: #1e3a8a; font-family: var(--font-mono); font-size: 12.5px;">
                  {{ it.item_code || it.name }}
                </td>

                <td style="font-weight: 600; color: #0f172a;">
                  {{ it.item_name || it.item_code }}
                </td>

                <td>
                  <span
                    v-if="it.hsn_code"
                    class="badge badge-purple"
                    style="font-family: var(--font-mono); font-size: 11px; font-weight: 700;"
                  >
                    {{ it.hsn_code }}
                  </span>
                  <span v-else style="color: #94a3b8; font-size: 12px;">—</span>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="it.stock_group === 'Sugar' ? 'badge-blue' : (it.stock_group === 'Edible Oil' ? 'badge-amber' : 'badge-green')"
                    style="font-size: 11.5px; font-weight: 700;"
                  >
                    🏷️ {{ it.stock_group || 'Sugar' }}
                  </span>
                </td>

                <td style="color: #475569; font-weight: 600;">
                  {{ it.stock_uom || 'Quintal' }}
                </td>

                <td>
                  <div style="display: flex; flex-direction: column;">
                    <span style="font-weight: 700; color: #0f172a; font-size: 12.5px;">
                      {{ it.gst_rate !== undefined ? it.gst_rate : 5.0 }}%
                    </span>
                    <span style="font-size: 10.5px; color: #64748b;">
                      (CGST: {{ ((it.gst_rate || 5.0) / 2).toFixed(2) }}% + SGST: {{ ((it.gst_rate || 5.0) / 2).toFixed(2) }}%)
                    </span>
                  </div>
                </td>

                <td style="text-align: right; font-weight: 700; color: #047857; font-family: var(--font-mono);">
                  {{ it.standard_rate ? `₹ ${Number(it.standard_rate).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—' }}
                </td>

                <td style="color: #64748b; font-size: 12px; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ it.description || '—' }}
                </td>

                <td style="text-align: center;" @click.stop>
                  <button
                    type="button"
                    class="btn btn-secondary btn-sm"
                    style="padding: 3px 8px; font-size: 11.5px;"
                    @click="openItemModal(it)"
                  >
                    ✏️ Edit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Items Master Gateway"
      :items="menuItems"
      :active-index="0"
      @select="handleSelect"
    />

    <!-- Item Modal -->
    <ItemModal
      :show="showItemModal"
      :item-data="activeItemData"
      @close="showItemModal = false"
      @saved="onItemSaved"
    />

    <!-- Stock Group Modal -->
    <StockGroupModal
      :show="showGroupModal"
      :group-data="activeGroupData"
      @close="showGroupModal = false"
      @saved="onGroupSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'
import ItemModal from '../components/ItemModal.vue'
import StockGroupModal from '../components/StockGroupModal.vue'

const router = useRouter()
const { getItems, getStockGroups } = useFrappeApi()

const items = ref([])
const stockGroups = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedGroupFilter = ref('')

const showItemModal = ref(false)
const activeItemData = ref(null)

const showGroupModal = ref(false)
const activeGroupData = ref(null)

const menuItems = [
  { label: 'Add Commodity / Item', key: 'N', action: () => openItemModal(null) },
  { label: 'Add Stock Group', key: 'G', action: () => openStockGroupModal(null) },
  { label: 'Brokers Directory', key: 'B', action: () => router.push('/brokers') },
  { label: 'Purchase Entry', key: 'F9', action: () => router.push('/purchase') },
  { label: 'Sell Entry', key: 'F8', action: () => router.push('/sell') },
  { label: 'Return to Gateway', key: 'Esc', action: () => router.push('/') },
]

const handleSelect = (item) => {
  if (item && item.action) item.action()
}

const loadData = async () => {
  loading.value = true
  try {
    const [itList, sgList] = await Promise.all([
      getItems('', selectedGroupFilter.value || null),
      getStockGroups(),
    ])
    items.value = itList || []
    stockGroups.value = sgList || []
  } catch (err) {
    showToast(`Error loading items: ${err.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('keydown', onKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeyDown)
})

const onKeyDown = (e) => {
  if (showItemModal.value || showGroupModal.value) return
  const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)
  if (isTyping) return

  const key = e.key.toUpperCase()
  if (key === 'N') {
    e.preventDefault()
    openItemModal(null)
  } else if (key === 'G') {
    e.preventDefault()
    openStockGroupModal(null)
  } else if (key === 'ESCAPE') {
    e.preventDefault()
    router.push('/')
  }
}

const filteredItems = computed(() => {
  let list = items.value
  if (selectedGroupFilter.value) {
    list = list.filter((it) => (it.stock_group || 'Sugar') === selectedGroupFilter.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter((it) => {
      const code = (it.item_code || it.name || '').toLowerCase()
      const name = (it.item_name || '').toLowerCase()
      const hsn = (it.hsn_code || '').toLowerCase()
      const grp = (it.stock_group || '').toLowerCase()
      const desc = (it.description || '').toLowerCase()
      return code.includes(q) || name.includes(q) || hsn.includes(q) || grp.includes(q) || desc.includes(q)
    })
  }
  return list
})

const filterByGroup = (groupName) => {
  if (selectedGroupFilter.value === groupName) {
    selectedGroupFilter.value = ''
  } else {
    selectedGroupFilter.value = groupName
  }
}

const onFilterChange = () => {
  // filteredItems is reactive
}

const openItemModal = (it) => {
  activeItemData.value = it
  showItemModal.value = true
}

const onItemSaved = () => {
  loadData()
}

const openStockGroupModal = (g) => {
  activeGroupData.value = g
  showGroupModal.value = true
}

const onGroupSaved = () => {
  loadData()
}
</script>

<style scoped>
.items-page-header {
  border-bottom: 2px solid var(--blue);
  padding-bottom: 12px;
  margin-bottom: 16px;
}

.items-header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.items-filter-bar {
  padding: 12px 16px;
  background: var(--panel-soft);
  border: 1px solid var(--line);
  border-radius: 6px;
  margin-bottom: 14px;
  display: flex;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-search-box {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.filter-search-box input {
  width: 100%;
  padding: 7px 10px 7px 32px;
  font-size: 13px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 13px;
  pointer-events: none;
}

.filter-group-select {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-group-select label {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  white-space: nowrap;
}

.filter-group-select select {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 12px;
  background: var(--input-bg);
  min-width: 160px;
}

.stock-groups-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  padding: 4px 2px 14px 2px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--line);
}

.stock-group-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--panel);
  cursor: pointer;
  white-space: nowrap;
  font-size: 12px;
  transition: all 0.12s ease;
  flex-shrink: 0;
}

.stock-group-chip:hover {
  border-color: var(--blue);
  background: var(--blue-soft);
}

.stock-group-chip.active {
  border-color: var(--blue);
  background: var(--blue-soft);
  box-shadow: 0 0 0 1px var(--blue);
}

.chip-name {
  font-weight: 700;
  color: var(--navy);
}

.chip-count {
  color: var(--muted);
  font-size: 11px;
}

.chip-edit-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--muted);
  padding: 0 2px;
  font-size: 11px;
}

.chip-edit-btn:hover {
  color: var(--blue);
}

.items-table-wrapper {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.items-data-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
  font-size: 12.5px;
}

.items-data-table th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--navy);
  color: #ffffff;
  padding: 9px 12px;
  font-weight: 700;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-right: 1px solid rgba(255, 255, 255, 0.12);
  white-space: nowrap;
}

.items-data-table th:last-child {
  border-right: none;
}

.items-data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--line);
  border-right: 1px solid var(--line);
  color: var(--text);
  vertical-align: middle;
}

.items-data-table td:last-child {
  border-right: none;
}

.items-data-table tr:hover {
  background: var(--table-hover);
}

.empty-state-box {
  padding: 40px 20px;
  text-align: center;
  color: var(--muted);
}

/* Mobile Scroll Cue Banner */
.mobile-scroll-cue {
  display: none;
  background: var(--blue-soft, #eff6ff);
  color: var(--blue, #2563eb);
  font-size: 11.5px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  border: 1px solid rgba(37, 99, 235, 0.15);
  align-items: center;
  gap: 6px;
}

.cue-icon {
  font-size: 14px;
  animation: nudgeHorizontal 1.5s infinite ease-in-out;
}

@keyframes nudgeHorizontal {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

@media (max-width: 1024px) {
  .mobile-scroll-cue {
    display: flex;
  }
}

@media (max-width: 768px) {
  .items-page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .items-header-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    width: 100%;
  }

  .items-header-actions .btn {
    width: 100%;
    justify-content: center;
  }

  .items-filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 10px;
  }

  .filter-search-box {
    width: 100%;
    min-width: 0;
  }

  .filter-group-select {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group-select select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .items-header-actions {
    grid-template-columns: 1fr;
  }
}
</style>
