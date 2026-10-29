import { ref, reactive } from 'vue'

export const bootState = reactive({
  user: 'Guest',
  fullName: 'User',
  userImage: null,
  companies: [],
  defaultCompany: '',
  today: new Date().toISOString().split('T')[0],
  isBooted: false,
})

export const csrfToken = ref('')

export function useFrappeApi() {
  const getCsrf = () => {
    if (csrfToken.value) return csrfToken.value
    if (typeof window !== 'undefined') {
      if (window.csrf_token) return window.csrf_token
      if (window.frappe_boot && window.frappe_boot.csrf_token) return window.frappe_boot.csrf_token
    }
    const match = document.cookie.match(/csrf_token=([^;]+)/)
    return match ? decodeURIComponent(match[1]) : ''
  }

  const call = async (method, args = {}, httpMethod = 'POST') => {
    const csrf = getCsrf()
    const headers = {
      'Accept': 'application/json',
      'X-Frappe-Site-Name': 'sugar.local',
    }

    if (csrf) {
      headers['X-Frappe-CSRF-Token'] = csrf
    }

    let url = `/api/method/${method}`
    let body = null

    if (httpMethod === 'GET') {
      const params = new URLSearchParams()
      for (const key in args) {
        if (args[key] !== undefined && args[key] !== null) {
          params.append(key, typeof args[key] === 'object' ? JSON.stringify(args[key]) : args[key])
        }
      }
      const qs = params.toString()
      if (qs) url += `?${qs}`
    } else {
      headers['Content-Type'] = 'application/json'
      body = JSON.stringify(args)
    }

    const res = await fetch(url, {
      method: httpMethod,
      headers,
      body,
      credentials: 'include',
    })

    if (!res.ok) {
      let errText = ''
      try {
        const errJson = await res.json()
        errText = errJson._server_messages
          ? JSON.parse(errJson._server_messages).map((m) => JSON.parse(m).message).join('\n')
          : (errJson.exception || errJson.message || res.statusText)
      } catch (e) {
        errText = await res.text()
      }
      throw new Error(errText || `Server error (${res.status})`)
    }

    const data = await res.json()
    return data.message !== undefined ? data.message : data
  }

  const boot = async () => {
    try {
      const data = await call('brokerage_module.brokerage_module.api.get_boot', {}, 'GET')
      bootState.user = data.user
      bootState.fullName = data.full_name
      bootState.userImage = data.user_image
      bootState.companies = data.companies || []
      bootState.defaultCompany = data.default_company || (data.companies?.[0]?.name || '')
      bootState.today = data.today || new Date().toISOString().split('T')[0]
      csrfToken.value = data.csrf_token || ''
      bootState.isBooted = true
    } catch (e) {
      console.warn('Boot failed, using fallback mock / guest values:', e)
      bootState.isBooted = true
    }
  }

  const searchEntities = async (doctype, query = '', extra = {}) => {
    return await call('brokerage_module.brokerage_module.api.search_entities', {
      doctype,
      query,
      ...extra,
    }, 'GET')
  }

  const getBrokerDetails = async (broker) => {
    return await call('brokerage_module.brokerage_module.api.get_broker_details', { broker }, 'GET')
  }

  const saveBroker = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_broker', { data }, 'POST')
  }

  const getBrokerItemRate = async (broker, item, stockGroup = null, entryType = 'Purchase', postingDate = null) => {
    return await call('brokerage_module.brokerage_module.api.get_broker_item_rate', {
      broker,
      item,
      stock_group: stockGroup,
      entry_type: entryType,
      posting_date: postingDate || bootState.today,
    }, 'GET')
  }

  const getStockGroups = async (query = '') => {
    return await call('brokerage_module.brokerage_module.api.get_stock_groups', { query }, 'GET')
  }

  const saveStockGroup = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_stock_group', { data }, 'POST')
  }

  const getItems = async (query = '', stockGroup = null) => {
    return await call('brokerage_module.brokerage_module.api.get_items', {
      query,
      stock_group: stockGroup,
    }, 'GET')
  }

  const saveItem = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_item', { data }, 'POST')
  }

  const saveRateConfiguration = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_rate_configuration', { data }, 'POST')
  }

  const getRateConfigurations = async (broker = null) => {
    return await call('brokerage_module.brokerage_module.api.get_rate_configurations', { broker }, 'GET')
  }

  const savePurchaseEntry = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_purchase_entry', { data }, 'POST')
  }

  const saveSalesEntry = async (data) => {
    return await call('brokerage_module.brokerage_module.api.save_sales_entry', { data }, 'POST')
  }

  const getEntries = async (entryType = 'Purchase', filters = {}) => {
    return await call('brokerage_module.brokerage_module.api.get_entries', {
      entry_type: entryType,
      ...filters,
    }, 'GET')
  }

  const getDashboardSummary = async () => {
    return await call('brokerage_module.brokerage_module.api.get_dashboard_summary', {}, 'GET')
  }

  const getSalesOutstandingRegister = async (filters = {}) => {
    return await call('brokerage_module.brokerage_module.api.get_sales_outstanding_register', filters, 'GET')
  }

  const settleSalesEntry = async (payload = {}) => {
    return await call('brokerage_module.brokerage_module.api.settle_sales_entry', payload, 'POST')
  }

  return {
    bootState,
    boot,
    call,
    searchEntities,
    getBrokerDetails,
    saveBroker,
    getBrokerItemRate,
    saveRateConfiguration,
    getRateConfigurations,
    savePurchaseEntry,
    saveSalesEntry,
    getEntries,
    getDashboardSummary,
    getSalesOutstandingRegister,
    settleSalesEntry,
    getStockGroups,
    saveStockGroup,
    getItems,
    saveItem,
  }
}

