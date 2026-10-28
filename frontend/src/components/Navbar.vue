<template>
  <header class="top-nav">
    <div style="display: flex; align-items: center; gap: 20px;">
      <router-link to="/" class="brand">
        <div class="brand-icon">💼</div>
        <div>
          <div class="brand-title">Brokerage Desk</div>
          <div class="brand-subtitle">Shop Purchase &amp; Sell Brokerage Management</div>
        </div>
      </router-link>

      <nav class="nav-links">
        <router-link to="/" class="nav-item" active-class="active" exact>
          <span>📊</span>
          <span>Dashboard</span>
        </router-link>

        <router-link to="/purchase" class="nav-item" active-class="active">
          <span>🛒</span>
          <span>Purchase Entry</span>
          <kbd>F9</kbd>
        </router-link>

        <router-link to="/sell" class="nav-item" active-class="active">
          <span>🏷️</span>
          <span>Sell Entry</span>
          <kbd>F8</kbd>
        </router-link>

        <router-link to="/brokers" class="nav-item" active-class="active">
          <span>👥</span>
          <span>Brokers Setup</span>
        </router-link>

        <router-link to="/rate-configs" class="nav-item" active-class="active">
          <span>📅</span>
          <span>Date-Wise Rates</span>
        </router-link>

        <router-link to="/registers" class="nav-item" active-class="active">
          <span>📋</span>
          <span>Registers</span>
        </router-link>
      </nav>
    </div>

    <div style="display: flex; align-items: center; gap: 14px;">
      <div class="user-badge">
        <span style="font-size: 11px; background: rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 4px;">
          🏢 {{ bootState.defaultCompany || 'ERPNext' }}
        </span>
        <span style="font-weight: 600;">{{ bootState.fullName || bootState.user }}</span>
      </div>

      <a
        href="/app"
        class="btn btn-secondary btn-sm"
        style="background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); color: #fff;"
        title="Return to Frappe Desk"
      >
        <span>↩ Frappe Desk</span>
      </a>
    </div>
  </header>
</template>

<script setup>
import { bootState } from '../composables/useFrappeApi'
</script>
