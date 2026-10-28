import { createRouter, createWebHashHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import PurchaseEntryView from '../views/PurchaseEntryView.vue'
import SalesEntryView from '../views/SalesEntryView.vue'
import BrokersView from '../views/BrokersView.vue'
import RateConfigsView from '../views/RateConfigsView.vue'
import RegistersView from '../views/RegistersView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'Dashboard — Brokerage Desk' },
  },
  {
    path: '/purchase',
    name: 'PurchaseEntry',
    component: PurchaseEntryView,
    meta: { title: 'Purchase Entry — Brokerage Desk' },
  },
  {
    path: '/sell',
    name: 'SalesEntry',
    component: SalesEntryView,
    meta: { title: 'Sell Entry — Brokerage Desk' },
  },
  {
    path: '/brokers',
    name: 'Brokers',
    component: BrokersView,
    meta: { title: 'Brokers Directory — Brokerage Desk' },
  },
  {
    path: '/rate-configs',
    name: 'RateConfigs',
    component: RateConfigsView,
    meta: { title: 'Date-Wise Rate Configurations — Brokerage Desk' },
  },
  {
    path: '/registers',
    name: 'Registers',
    component: RegistersView,
    meta: { title: 'Registers — Brokerage Desk' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

