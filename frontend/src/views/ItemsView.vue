<template>
  <div class="page-container page-with-menu">
    <div class="page-main">
      <div class="card" style="margin-bottom: 20px;">
        <!-- Header -->
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
          <div>
            <div class="card-title" style="display: flex; align-items: center; gap: 10px;">
              <span>🌾 Commodity &amp; Stock Group Masters</span>
              <span class="badge badge-blue">{{ items.length }} Items</span>
              <span class="badge badge-purple">{{ stockGroups.length }} Groups</span>
            </div>
            <div class="card-subtitle">
              Every item belongs to a Stock Group (e.g. Sugar). In Broker Master, brokerage terms are assigned per Stock Group and automatically inherited during Purchase &amp; Sell.
            </div>
          </div>

          <div style="display: flex; gap: 10px; align-items: center;">
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
        <div style="padding: 14px 20px; background: #f8fafc; border-bottom: 1px solid var(--border); display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 220px; position: relative;">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by commodity name, code, or description... (Press / to focus)"
              style="padding-left: 32px; font-size: 13.5px;"
              @input="onFilterChange"
            />
            <span style="position: absolute; left: 10px; top: 9px; color: #94a3b8;">🔍</span>
          </div>

          <div style="display: flex; gap: 8px; align-items: center;">
            <span style="font-size: 13px; font-weight: 700; color: #475569;">Stock Group:</span>
            <select
              v-model="selectedGroupFilter"
              style="font-size: 13px; font-weight: 600; padding: 6px 12px; background: #fff;"
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
        <div style="padding: 12px 20px; background: #fff; border-bottom: 1px solid var(--border); display: flex; gap: 16px; align-items: center; overflow-x: auto;">
          <div
            v-for="g in stockGroups"
            :key="g.name"
            style="display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 6px; border: 1px solid #e2e8f0; background: #f8fafc; cursor: pointer; white-space: nowrap; font-size: 12px;"
            :style="selectedGroupFilter === g.name ? 'border-color: #2563eb; background: #eff6ff;' : ''"
            @click="filterByGroup(g.name)"
          >
            <span style="font-weight: 700; color: #0f172a;">{{ g.stock_group_name || g.name }}</span>
            <span class="badge badge-blue" style="font-size: 10px;">GST {{ g.default_gst_rate || 5 }}%</span>
            <span style="color: #64748b; font-size: 11px;">({{ g.item_count || 0 }} items)</span>
            <button
              type="button"
              style="border: none; background: transparent; cursor: pointer; color: #64748b; padding: 0 2px;"
              title="Edit Stock Group"
              @click.stop="openStockGroupModal(g)"
            >
              ✏️
            </button>
          </div>
        </div>

        <!-- Table View -->
        <div v-if="loading" style="padding: 40px; text-align: center; color: #64748b;">
          ⏳ Loading commodities &amp; items...
        </div>

        <div v-else-if="filteredItems.length === 0" style="padding: 50px 20px; text-align: center; color: #64748b;">
          <div style="font-size: 38px; margin-bottom: 8px;">🌾</div>
          <div style="font-weight: 700; font-size: 15px; color: #334155;">No Commodities Found</div>
          <div style="font-size: 13px; margin-top: 4px;">Click <strong>"+ Add Commodity / Item"</strong> to create your first stock item.</div>
        </div>

        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 40px; text-align: center;">#</th>
                <th style="min-width: 140px;">Item Code / ID</th>
                <th style="min-width: 220px;">Commodity / Item Name</th>
                <th style="width: 160px;">Stock Group</th>
                <th style="width: 110px;">Stock UOM</th>
                <th style="width: 180px;">GST Rate (CGST + SGST)</th>
                <th style="width: 140px; text-align: right;">Std Rate (₹)</th>
                <th>Description / Packaging</th>
                <th style="width: 80px; text-align: center;">Action</th>
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

                <td style="font-weight: 700; color: #1e3a8a; font-family: var(--font-mono); font-size: 13px;">
                  {{ it.item_code || it.name }}
                </td>

                <td style="font-weight: 600; color: #0f172a;">
                  {{ it.item_name || it.item_code }}
                </td>

                <td>
                  <span
                    class="badge"
                    :class="it.stock_group === 'Sugar' ? 'badge-blue' : (it.stock_group === 'Edible Oil' ? 'badge-amber' : 'badge-green')"
                    style="font-size: 12px; font-weight: 700;"
                  >
                    🏷️ {{ it.stock_group || 'Sugar' }}
                  </span>
                </td>

                <td style="color: #475569; font-weight: 600;">
                  {{ it.stock_uom || 'Quintal' }}
                </td>

                <td>
                  <div style="display: flex; flex-direction: column;">
                    <span style="font-weight: 700; color: #0f172a; font-size: 13px;">
                      {{ it.gst_rate !== undefined ? it.gst_rate : 5.0 }}%
                    </span>
                    <span style="font-size: 11px; color: #64748b;">
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
                    style="padding: 4px 8px; font-size: 12px;"
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
      const grp = (it.stock_group || '').toLowerCase()
      const desc = (it.description || '').toLowerCase()
      return code.includes(q) || name.includes(q) || grp.includes(q) || desc.includes(q)
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

