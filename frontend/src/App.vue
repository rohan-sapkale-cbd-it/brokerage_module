<template>
  <div id="app">
    <TopBar />
    <NavigationPillars />
    <RouterView :key="$route.fullPath" />
    <FunctionKeyBar />

    <!-- Modals & Overlays -->
    <ConfirmModal />
    <DateModal />
    <HelpModal />
    <Toast />
    <BrokerModal
      :show="globalUiState.isBrokerModalOpen.value"
      @close="globalUiState.isBrokerModalOpen.value = false"
      @saved="onBrokerSaved"
    />
    <RateConfigModal
      :show="globalUiState.isRateModalOpen.value"
      @close="globalUiState.isRateModalOpen.value = false"
      @saved="onRateSaved"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import TopBar from './components/common/TopBar.vue'
import NavigationPillars from './components/common/NavigationPillars.vue'
import FunctionKeyBar from './components/common/FunctionKeyBar.vue'
import ConfirmModal from './components/common/ConfirmModal.vue'
import DateModal from './components/common/DateModal.vue'
import HelpModal from './components/common/HelpModal.vue'
import Toast from './components/common/Toast.vue'
import BrokerModal from './components/BrokerModal.vue'
import RateConfigModal from './components/RateConfigModal.vue'
import { useFrappeApi } from './composables/useFrappeApi'
import { useTheme } from './composables/useTheme'
import { globalUiState, showToast } from './composables/useKeyboardEngine'

const { boot } = useFrappeApi()
const { initTheme } = useTheme()

const onBrokerSaved = () => {
  globalUiState.isBrokerModalOpen.value = false
  showToast('Broker master saved successfully!')
  window.dispatchEvent(new CustomEvent('broker-master-updated'))
}

const onRateSaved = () => {
  globalUiState.isRateModalOpen.value = false
  showToast('Rate configuration saved successfully!')
  window.dispatchEvent(new CustomEvent('rate-config-updated'))
}

onMounted(async () => {
  initTheme()
  await boot()
})
</script>
