import { ref } from 'vue'
import { router } from '../router'

export const VOUCHER_TYPE_MAP = {
  F8: { name: 'Sell Entry', title: 'Broker Sales Entry', route: '/sell' },
  F9: { name: 'Purchase Entry', title: 'Broker Purchase Entry', route: '/purchase' },
}

// Global shared UI state for modals, overlays and quick actions
export const globalUiState = {
  isHelpOpen: ref(false),
  isDateModalOpen: ref(false),
  isConfirmModalOpen: ref(false),
  confirmModalData: ref(null),
  toastMessage: ref(''),
  toastVisible: ref(false),
  isBrokerModalOpen: ref(false),
  brokerModalId: ref(''),
  isRateModalOpen: ref(false),
  rateModalId: ref(''),
}

export function openGlobalBrokerModal(brokerId = '') {
  globalUiState.brokerModalId.value = brokerId
  globalUiState.isBrokerModalOpen.value = true
}

export function openGlobalRateModal(configId = '') {
  globalUiState.rateModalId.value = configId
  globalUiState.isRateModalOpen.value = true
}

let toastTimer = null
export function showToast(msg, duration = 2200) {
  clearTimeout(toastTimer)
  globalUiState.toastMessage.value = msg
  globalUiState.toastVisible.value = true
  toastTimer = setTimeout(() => {
    globalUiState.toastVisible.value = false
  }, duration)
}

export function openConfirm(title, body, onYes, onNo) {
  globalUiState.confirmModalData.value = { title, body, onYes, onNo }
  globalUiState.isConfirmModalOpen.value = true
}

export function closeConfirm(isConfirmed) {
  const data = globalUiState.confirmModalData.value
  globalUiState.isConfirmModalOpen.value = false
  globalUiState.confirmModalData.value = null
  if (isConfirmed && data && data.onYes) {
    data.onYes()
  } else if (!isConfirmed && data && data.onNo) {
    data.onNo()
  }
}

export function handleFunctionKey(fk) {
  if (fk === 'F1') {
    globalUiState.isHelpOpen.value = true
    return
  }
  if (fk === 'F2') {
    globalUiState.isDateModalOpen.value = true
    return
  }
  if (fk === 'F8') {
    if (router) router.push('/sell')
    return
  }
  if (fk === 'F9') {
    if (router) router.push('/purchase')
    return
  }
  if (fk === 'Esc') {
    handleEscape()
    return
  }
}

export function handleEscape() {
  // 1. Confirm modal
  if (globalUiState.isConfirmModalOpen.value) {
    closeConfirm(false)
    return
  }
  // 2. Fullscreen broker / rate modal
  if (globalUiState.isBrokerModalOpen.value) {
    globalUiState.isBrokerModalOpen.value = false
    return
  }
  if (globalUiState.isRateModalOpen.value) {
    globalUiState.isRateModalOpen.value = false
    return
  }
  // 3. Help or Date modal
  if (globalUiState.isHelpOpen.value || globalUiState.isDateModalOpen.value) {
    globalUiState.isHelpOpen.value = false
    globalUiState.isDateModalOpen.value = false
    return
  }
  // 4. Global search dropdown
  if (document.querySelector('.search-dropdown-menu')) {
    window.dispatchEvent(new CustomEvent('close-global-search'))
    return
  }
  if (document.querySelector('.modal-overlay')) {
    return
  }
  // 5. Active input element
  if (document.activeElement && ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
    document.activeElement.blur()
    return
  }
  // 6. Return to Gateway if not already there
  if (router && router.currentRoute.value.path !== '/') {
    router.push('/')
  }
}

let isGlobalListenerAttached = false

function initGlobalKeyboardListener() {
  if (isGlobalListenerAttached || typeof window === 'undefined') return
  isGlobalListenerAttached = true

  window.addEventListener('keydown', (e) => {
    // 1. Ctrl+K or '/' -> Focus Search
    const isKKey = e.key === 'k' || e.key === 'K' || e.code === 'KeyK'
    if ((e.ctrlKey || e.metaKey) && isKKey) {
      e.preventDefault()
      e.stopPropagation()
      window.dispatchEvent(new CustomEvent('focus-global-search'))
      return
    }

    if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
      e.preventDefault()
      e.stopPropagation()
      window.dispatchEvent(new CustomEvent('focus-global-search'))
      return
    }

    // 2. Confirm Modal handling (Enter/Y = Yes, Esc/N = No)
    if (globalUiState.isConfirmModalOpen.value) {
      if (e.key === 'Enter' || e.key.toLowerCase() === 'y') {
        e.preventDefault()
        e.stopPropagation()
        closeConfirm(true)
      } else if (e.key === 'Escape' || e.key.toLowerCase() === 'n') {
        e.preventDefault()
        e.stopPropagation()
        closeConfirm(false)
      }
      return
    }

    // 3. Broker / Rate modal Esc
    if (globalUiState.isBrokerModalOpen.value || globalUiState.isRateModalOpen.value) {
      if (e.key === 'Escape') {
        e.preventDefault()
        e.stopPropagation()
        globalUiState.isBrokerModalOpen.value = false
        globalUiState.isRateModalOpen.value = false
        return
      }
    }

    // 4. Help / Date modal
    if (globalUiState.isHelpOpen.value || globalUiState.isDateModalOpen.value) {
      if (e.key === 'Escape' || e.key === 'Enter') {
        e.preventDefault()
        e.stopPropagation()
        globalUiState.isHelpOpen.value = false
        globalUiState.isDateModalOpen.value = false
        return
      }
    }

    // 5. Function keys F1-F12
    if (e.key.startsWith('F') && /^F([1-9]|1[0-2])$/.test(e.key)) {
      e.preventDefault()
      handleFunctionKey(e.key)
      return
    }

    // 6. Single-key shortcuts on Gateway screen (when not typing in an input)
    const isTyping = document.activeElement && ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)
    if (!isTyping && router && router.currentRoute.value.path === '/') {
      const key = e.key.toUpperCase()
      if (key === 'P') {
        e.preventDefault()
        router.push('/purchase')
        return
      }
      if (key === 'S') {
        e.preventDefault()
        router.push('/sell')
        return
      }
      if (key === 'O') {
        e.preventDefault()
        router.push('/registers?type=SalesOutstanding')
        return
      }
      if (key === 'L') {
        e.preventDefault()
        router.push('/registers')
        return
      }
      if (key === 'B') {
        e.preventDefault()
        openGlobalBrokerModal('')
        return
      }
      if (key === 'I') {
        e.preventDefault()
        router.push('/items')
        return
      }
      if (key === 'R') {
        e.preventDefault()
        openGlobalRateModal('')
        return
      }
    }

    // 7. Global Escape
    if (e.key === 'Escape') {
      e.preventDefault()
      e.stopPropagation()
      handleEscape()
      return
    }
  }, { capture: true })
}

initGlobalKeyboardListener()

export function useKeyboardEngine() {
  return {
    globalUiState,
    handleFunctionKey,
    handleEscape,
    showToast,
    openConfirm,
    closeConfirm,
    openGlobalBrokerModal,
    openGlobalRateModal,
  }
}

