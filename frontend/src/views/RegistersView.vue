<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="content-card">
        <!-- Page Header with 3 Core Register Tabs -->
        <div class="page-header">
          <div>
            <div class="page-title">
              <span>📋 Trade &amp; Brokerage Audit Registers</span>
              <span
                class="badge"
                :class="currentType === 'Purchase' ? 'badge-blue' : ((currentType === 'Sell' || currentType === 'Sales') ? 'badge-green' : (currentType === 'ItemWise' ? 'badge-purple' : 'badge-amber'))"
              >
                {{ currentType === 'SalesOutstanding' ? 'Sales Outstanding Register' : (currentType === 'ItemWise' ? 'Item-Wise Register' : ((currentType === 'Sell' || currentType === 'Sales') ? 'Sales Register' : 'Purchase Register')) }}
              </span>
            </div>
            <div class="page-subtitle">
              {{
                currentType === 'SalesOutstanding'
                  ? 'Audit pending sales trade collections, broker commission outstandings, and ageing dues.'
                  : (currentType === 'ItemWise'
                    ? 'Audit commodity and item-wise trading volumes, net quintals, and total brokerage earnings.'
                    : 'View all booked ' + ((currentType === 'Sell' || currentType === 'Sales') ? 'Sales' : currentType) + ' entries with exact brokerage calculations and source audit.')
              }}
            </div>
          </div>

          <!-- Register Mode Tabs -->
          <div class="register-tabs-group">
            <button
              type="button"
              class="btn btn-sm"
              :class="currentType === 'Purchase' ? 'btn-primary' : 'btn-secondary'"
              @click="switchType('Purchase')"
            >
              🛒 Purchase Register (<kbd style="font-size: 10px;">P</kbd>)
            </button>
            <button
              type="button"
              class="btn btn-sm"
              :class="currentType === 'Sell' ? 'btn-success' : 'btn-secondary'"
              @click="switchType('Sell')"
            >
              🏷️ Sales Register (<kbd style="font-size: 10px;">S</kbd>)
            </button>
            <button
              type="button"
              class="btn btn-sm"
              :class="currentType === 'ItemWise' ? 'btn-primary' : 'btn-secondary'"
              style="border-color: #8b5cf6;"
              @click="switchType('ItemWise')"
            >
              📦 Item-Wise Register (<kbd style="font-size: 10px; background: #f5f3ff; color: #7c3aed;">I</kbd>)
            </button>
            <button
              type="button"
              class="btn btn-sm"
              :class="currentType === 'SalesOutstanding' ? 'btn-primary' : 'btn-secondary'"
              style="border-color: var(--amber);"
              @click="switchType('SalesOutstanding')"
            >
              ⚠️ Sales Outstanding Register (<kbd style="font-size: 10px; background: #fff8eb; color: var(--amber);">O</kbd>)
            </button>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- VIEW 1 & 2: STANDARD PURCHASE / SALES REGISTERS          -->
        <!-- ======================================================== -->
        <template v-if="currentType === 'Purchase' || currentType === 'Sell' || currentType === 'Sales'">
          <!-- Filter Bar -->
          <div class="register-filter-bar">
            <div class="form-group filter-date">
              <label>From Date</label>
              <input v-model="filters.from_date" type="date" @change="loadData" />
            </div>

            <div class="form-group filter-date">
              <label>To Date</label>
              <input v-model="filters.to_date" type="date" @change="loadData" />
            </div>

            <div class="form-group filter-broker">
              <label>Filter by Broker</label>
              <TypeaheadSelect
                v-model="filters.broker"
                :label="filters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchBrokers"
                @change="onBrokerFilter"
              />
            </div>

            <div class="filter-actions">
              <button type="button" class="btn btn-secondary btn-sm" @click="resetFilters">
                Reset Filters
              </button>
            </div>
          </div>

          <!-- Metric Summary Ribbon -->
          <div class="register-metric-ribbon">
            <div class="register-metric-card">
              <div class="metric-card-label">Total Vouchers</div>
              <div class="metric-card-val navy-val">
                {{ summary.total_count }}
              </div>
            </div>

            <div class="register-metric-card">
              <div class="metric-card-label">Total Quantity (Qtl)</div>
              <div class="metric-card-val navy-val">
                {{ formatNumber(summary.total_qty) }} Qtl
              </div>
            </div>

            <div class="register-metric-card">
              <div class="metric-card-label">Trade Subtotal</div>
              <div class="metric-card-val navy-val">
                ₹ {{ formatCurrency(summary.total_trade) }}
              </div>
            </div>

            <div class="register-metric-card metric-card-gst">
              <div class="metric-card-label green-text">Total GST</div>
              <div class="metric-card-val green-text">
                ₹ {{ formatCurrency(summary.total_gst || 0) }}
              </div>
            </div>

            <div class="register-metric-card metric-card-grand">
              <div class="metric-card-label blue-text">Grand Total</div>
              <div class="metric-card-val blue-text">
                ₹ {{ formatCurrency(summary.total_grand || summary.total_trade) }}
              </div>
            </div>

            <div class="register-metric-card metric-card-brokerage">
              <div class="metric-card-label brk-text">Total Brokerage</div>
              <div class="metric-card-val brk-text">
                ₹ {{ formatCurrency(summary.total_brokerage) }}
              </div>
            </div>
          </div>

          <!-- Mobile Scroll Cue Banner -->
          <div class="mobile-scroll-cue">
            <span class="cue-icon">↔</span>
            <span>Scroll horizontally to view all register columns</span>
          </div>

          <!-- Table of Entries -->
          <div class="register-table-wrapper">
            <table class="data-table register-data-table">
              <thead>
                <tr>
                  <th class="col-id">Entry ID</th>
                  <th class="col-date">Date</th>
                  <th class="col-broker">Broker (Sole Party)</th>
                  <th class="col-commodity">Commodity &amp; Group</th>
                  <th class="col-num">Trade Subtotal (₹)</th>
                  <th class="col-gst">GST Rate</th>
                  <th class="col-grand">Grand Total (₹)</th>
                  <th class="col-method">Method</th>
                  <th class="col-rate">Brokerage Rate</th>
                  <th class="col-brk">Brokerage (₹)</th>
                  <th class="col-status">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="records.length === 0">
                  <td colspan="11" class="empty-cell">
                    No {{ currentType }} entries found for selected criteria.
                  </td>
                </tr>
                <tr v-for="r in records" :key="r.name">
                  <td class="col-id">
                    <a :href="`/app/${(currentType === 'Sell' || currentType === 'Sales') ? 'broker-sales-entry' : 'broker-purchase-entry'}/${r.name}`" target="_blank" class="entry-link">
                      {{ r.name }} ↗
                    </a>
                  </td>
                  <td class="col-date">{{ r.posting_date }}</td>
                  <td class="col-broker">
                    <div class="broker-name-cell">{{ r.broker_name || r.broker }}</div>
                    <div v-if="r.broker_name && r.broker && r.broker_name !== r.broker" class="broker-id-sub">{{ r.broker }}</div>
                  </td>
                  <td class="col-commodity cell-commodity">
                    <div class="commodity-cell">
                      <!-- 1. If child items exist: list every item and its stock group -->
                      <div v-if="r.items && r.items.length > 0" class="commodity-items-wrap">
                        <div
                          v-for="(it, idx) in r.items"
                          :key="idx"
                          class="commodity-item-row"
                        >
                          <span class="commodity-item-title">{{ it.item_name || it.item }}</span>
                          <span v-if="it.stock_group" class="badge badge-purple group-pill">
                            🏷️ {{ cleanItemText(it.stock_group) }}
                          </span>
                        </div>
                      </div>

                      <!-- 2. Fallback if child items not available: clean parent item name -->
                      <div v-else class="commodity-fallback-wrap">
                        <span class="commodity-item-title">{{ cleanItemText(r.item_name || r.item) }}</span>
                      </div>

                      <!-- 3. Explicit list of all selected stock groups (always visible, no '+1' or hidden groups) -->
                      <div v-if="getStockGroups(r).length > 0" class="selected-groups-row">
                        <span class="selected-groups-caption">Groups:</span>
                        <span
                          v-for="grp in getStockGroups(r)"
                          :key="grp"
                          class="badge badge-purple group-pill"
                        >
                          🏷️ {{ grp }}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td class="col-num subtotal-cell">
                    ₹{{ formatCurrency(r.trade_amount) }}
                  </td>
                  <td class="col-gst gst-cell">
                    {{ r.gst_rate !== undefined ? r.gst_rate : 5 }}% (₹{{ formatCurrency(r.total_gst_amount || 0) }})
                  </td>
                  <td class="col-grand grand-cell">
                    ₹{{ formatCurrency(r.grand_total || r.trade_amount) }}
                  </td>
                  <td class="col-method">
                    <span v-if="r.items_count > 1" class="badge badge-purple">Multi-Item</span>
                    <span v-else class="badge" :class="(currentType === 'Sell' || currentType === 'Sales') ? 'badge-green' : 'badge-blue'">{{ r.brokerage_method }}</span>
                  </td>
                  <td class="col-rate">
                    <span v-if="r.items_count > 1" class="muted-note">Multi-Terms</span>
                    <span v-else>{{ r.brokerage_method === 'Percentage' ? `${r.brokerage_rate}%` : (r.brokerage_method === 'Per Bag' ? `₹${r.brokerage_rate}/bag` : `₹${r.brokerage_rate}/qtl`) }}</span>
                  </td>
                  <td class="col-brk brokerage-cell">
                    ₹{{ formatCurrency(r.brokerage_amount) }}
                  </td>
                  <td class="col-status">
                    <span class="badge badge-green">{{ r.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ======================================================== -->
        <!-- VIEW 2.5: ITEM-WISE COMMODITY REGISTER                   -->
        <!-- ======================================================== -->
        <template v-else-if="currentType === 'ItemWise'">
          <!-- Filter Bar -->
          <div class="register-filter-bar">
            <div class="form-group filter-date">
              <label>From Date</label>
              <input v-model="itemFilters.from_date" type="date" @change="loadItemWiseData" />
            </div>

            <div class="form-group filter-date">
              <label>To Date</label>
              <input v-model="itemFilters.to_date" type="date" @change="loadItemWiseData" />
            </div>

            <div class="form-group filter-broker">
              <label>Filter by Broker</label>
              <TypeaheadSelect
                v-model="itemFilters.broker"
                :label="itemFilters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchBrokers"
                @change="onItemBrokerFilter"
              />
            </div>

            <div class="filter-actions">
              <button type="button" class="btn btn-secondary btn-sm" @click="resetItemFilters">
                Reset Filters
              </button>
            </div>
          </div>

          <!-- Metric Summary Ribbon -->
          <div class="register-metric-ribbon">
            <div class="register-metric-card">
              <div class="metric-card-label">Total Commodities</div>
              <div class="metric-card-val" style="color: #7c3aed;">
                {{ itemSummary.total_items }}
              </div>
            </div>

            <div class="register-metric-card metric-card-grand">
              <div class="metric-card-label blue-text">Purchase Volume</div>
              <div class="metric-card-val blue-text">
                {{ formatNumber(itemSummary.total_purchase_qty) }} Qtl
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">
                Trade: ₹{{ formatCurrency(itemSummary.total_purchase_trade) }}
              </div>
            </div>

            <div class="register-metric-card metric-card-gst">
              <div class="metric-card-label green-text">Sales Volume</div>
              <div class="metric-card-val green-text">
                {{ formatNumber(itemSummary.total_sales_qty) }} Qtl
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">
                Trade: ₹{{ formatCurrency(itemSummary.total_sales_trade) }}
              </div>
            </div>

            <div class="register-metric-card">
              <div class="metric-card-label">Overall Trade Volume</div>
              <div class="metric-card-val navy-val">
                ₹ {{ formatCurrency(itemSummary.overall_trade) }}
              </div>
            </div>

            <div class="register-metric-card metric-card-brokerage">
              <div class="metric-card-label brk-text">Combined Brokerage</div>
              <div class="metric-card-val brk-text">
                ₹ {{ formatCurrency(itemSummary.overall_brokerage) }}
              </div>
            </div>

            <div class="register-metric-card">
              <div class="metric-card-label">Total Vouchers</div>
              <div class="metric-card-val navy-val">
                {{ itemSummary.total_vouchers }}
              </div>
            </div>
          </div>

          <!-- Mobile Scroll Cue Banner -->
          <div class="mobile-scroll-cue">
            <span class="cue-icon">↔</span>
            <span>Scroll horizontally to view all item columns</span>
          </div>

          <!-- Table of Item-Wise Entries -->
          <div class="register-table-wrapper">
            <table class="data-table register-data-table">
              <thead>
                <tr>
                  <th>Commodity / Item</th>
                  <th>Stock Group</th>
                  <th style="text-align: right;">Purchase Qty (Qtl)</th>
                  <th style="text-align: right;">Purchase Trade (₹)</th>
                  <th style="text-align: right;">Purchase Brk (₹)</th>
                  <th style="text-align: right;">Sales Qty (Qtl)</th>
                  <th style="text-align: right;">Sales Trade (₹)</th>
                  <th style="text-align: right;">Sales Brk (₹)</th>
                  <th style="text-align: right;">Net Qty (Qtl)</th>
                  <th style="text-align: right;">Total Trade (₹)</th>
                  <th style="text-align: right;">Total Brk (₹)</th>
                  <th style="text-align: center;">Transactions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="itemRecords.length === 0">
                  <td colspan="12" style="text-align: center; padding: 36px; color: var(--muted);">
                    No item-wise data found for selected criteria.
                  </td>
                </tr>
                <template v-for="itm in itemRecords" :key="itm.item_code">
                  <tr>
                    <td>
                      <div style="font-weight: 700; color: var(--navy);">{{ itm.item_name }}</div>
                      <div style="font-size: 11px; color: var(--muted); font-family: var(--font-mono);">{{ itm.item_code }}</div>
                    </td>
                    <td>
                      <span class="badge badge-purple" style="font-size: 11px;">🏷️ {{ itm.stock_group }}</span>
                    </td>
                    <td style="text-align: right; color: var(--blue); font-weight: 600;">
                      {{ formatNumber(itm.purchase_qty) }}
                    </td>
                    <td style="text-align: right;">₹{{ formatCurrency(itm.purchase_trade) }}</td>
                    <td style="text-align: right; color: var(--blue);">₹{{ formatCurrency(itm.purchase_brokerage) }}</td>
                    <td style="text-align: right; color: #166534; font-weight: 600;">
                      {{ formatNumber(itm.sales_qty) }}
                    </td>
                    <td style="text-align: right;">₹{{ formatCurrency(itm.sales_trade) }}</td>
                    <td style="text-align: right; color: #166534;">₹{{ formatCurrency(itm.sales_brokerage) }}</td>
                    <td style="text-align: right; font-weight: 700;" :style="itm.net_qty >= 0 ? 'color: var(--blue);' : 'color: #dc2626;'">
                      {{ formatNumber(itm.net_qty) }}
                    </td>
                    <td style="text-align: right; font-weight: 700; color: var(--navy);">
                      ₹{{ formatCurrency(itm.total_trade) }}
                    </td>
                    <td style="text-align: right; font-weight: 800; color: var(--green);">
                      ₹{{ formatCurrency(itm.total_brokerage) }}
                    </td>
                    <td style="text-align: center;">
                      <button
                        type="button"
                        class="btn btn-secondary btn-sm"
                        style="font-size: 11px;"
                        @click="toggleItemExpand(itm.item_code)"
                      >
                        {{ expandedItems[itm.item_code] ? '▲ Hide' : `▼ View (${itm.vouchers.length})` }}
                      </button>
                    </td>
                  </tr>

                  <!-- Collapsible Item Transactions Table -->
                  <tr v-if="expandedItems[itm.item_code]">
                    <td colspan="12" style="background: var(--panel-soft); padding: 12px 18px;">
                      <div style="font-weight: 700; font-size: 12.5px; color: var(--navy); margin-bottom: 8px;">
                        📜 Booked Vouchers for {{ itm.item_name }} ({{ itm.item_code }}):
                      </div>
                      <table class="data-table" style="background: var(--panel); border: 1px solid var(--line);">
                        <thead>
                          <tr>
                            <th>Voucher ID</th>
                            <th>Type</th>
                            <th>Date</th>
                            <th>Broker (Sole Party)</th>
                            <th style="text-align: right;">Qty (Qtl)</th>
                            <th style="text-align: right;">Bags</th>
                            <th style="text-align: right;">Rate (₹)</th>
                            <th style="text-align: right;">Trade Amount (₹)</th>
                            <th style="text-align: right;">Brokerage (₹)</th>
                            <th style="text-align: center;">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="v in itm.vouchers" :key="v.voucher + v.voucher_type">
                            <td style="font-family: var(--font-mono); font-weight: 600;">
                              <a :href="`/app/${v.voucher_type === 'Purchase' ? 'broker-purchase-entry' : 'broker-sales-entry'}/${v.voucher}`" target="_blank" style="color: var(--blue); text-decoration: none;">
                                {{ v.voucher }} ↗
                              </a>
                            </td>
                            <td>
                              <span class="badge" :class="v.voucher_type === 'Purchase' ? 'badge-blue' : 'badge-green'">
                                {{ v.voucher_type }}
                              </span>
                            </td>
                            <td>{{ v.posting_date }}</td>
                            <td style="font-weight: 600;">{{ v.broker_name || v.broker }}</td>
                            <td style="text-align: right;">{{ formatNumber(v.quantity) }}</td>
                            <td style="text-align: right;">{{ formatNumber(v.bags) }}</td>
                            <td style="text-align: right;">₹{{ formatCurrency(v.rate) }}</td>
                            <td style="text-align: right; font-weight: 600; color: var(--navy);">
                              ₹{{ formatCurrency(v.trade_amount) }}
                            </td>
                            <td style="text-align: right; font-weight: 800; color: var(--green);">
                              ₹{{ formatCurrency(v.brokerage_amount) }}
                            </td>
                            <td style="text-align: center;">
                              <span class="badge badge-green">{{ v.status }}</span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ======================================================== -->
        <!-- VIEW 3: SALES OUTSTANDING REGISTER (DEDICATED)           -->
        <!-- ======================================================== -->
        <template v-else-if="currentType === 'SalesOutstanding'">
          <!-- Sub-Tab Navigation Bar -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 2px solid var(--line); padding-bottom: 8px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; gap: 6px;">
              <button
                type="button"
                class="btn btn-sm"
                :class="outstandingSubTab === 'brokers' ? 'btn-primary' : 'btn-secondary'"
                @click="outstandingSubTab = 'brokers'"
              >
                <span>🏢 Broker-Wise Outstandings</span>
                <span class="badge badge-amber" style="margin-left: 4px;">{{ outSummary.brokers_with_dues }} Due</span>
              </button>

              <button
                type="button"
                class="btn btn-sm"
                :class="outstandingSubTab === 'vouchers' ? 'btn-primary' : 'btn-secondary'"
                @click="outstandingSubTab = 'vouchers'"
              >
                <span>📋 Voucher-Wise Detailed Log</span>
                <span class="badge badge-blue" style="margin-left: 4px;">{{ outSummary.pending_vouchers }} Pending</span>
              </button>

              <button
                type="button"
                class="btn btn-sm"
                :class="outstandingSubTab === 'ageing' ? 'btn-primary' : 'btn-secondary'"
                @click="outstandingSubTab = 'ageing'"
              >
                <span>⏳ Ageing Breakdown</span>
              </button>
            </div>

            <div style="display: flex; gap: 8px; align-items: center;">
              <span style="font-size: 11.5px; color: var(--muted); font-weight: 600;">Status:</span>
              <select
                v-model="outFilters.settlement_status"
                style="padding: 4px 8px; font-size: 12px; border-radius: 4px;"
                @change="loadSalesOutstanding"
              >
                <option value="All">All Vouchers</option>
                <option value="Pending">Pending Dues Only</option>
                <option value="Partially Settled">Partially Settled</option>
                <option value="Settled">Settled Only</option>
              </select>
            </div>
          </div>

          <!-- Outstanding Filter Bar -->
          <div class="register-filter-bar">
            <div class="form-group filter-date">
              <label>From Date</label>
              <input v-model="outFilters.from_date" type="date" @change="loadSalesOutstanding" />
            </div>

            <div class="form-group filter-date">
              <label>To Date</label>
              <input v-model="outFilters.to_date" type="date" @change="loadSalesOutstanding" />
            </div>

            <div class="form-group filter-broker">
              <label>Filter Broker</label>
              <TypeaheadSelect
                v-model="outFilters.broker"
                :label="outFilters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchSellBrokers"
                @change="onOutBrokerFilter"
              />
            </div>

            <div class="form-group" style="flex: 1 1 200px; min-width: 180px;">
              <label>Instant Search (Voucher / Broker / Item)</label>
              <input
                v-model="outFilters.query"
                type="text"
                placeholder="Filter results..."
                @input="loadSalesOutstanding"
              />
            </div>

            <div class="filter-actions">
              <button type="button" class="btn btn-secondary btn-sm" @click="resetOutFilters">
                Reset
              </button>
            </div>
          </div>

          <!-- Outstanding KPI Ribbon -->
          <div class="register-metric-ribbon">
            <!-- Total Brokerage Due (Highlighted in Amber/Red) -->
            <div class="register-metric-card" style="background: #fff8eb; border-color: #fde68a;">
              <div class="metric-card-label" style="color: #b45309;">Brokerage Due (Sell)</div>
              <div class="metric-card-val" style="color: #d97706;">
                ₹ {{ formatCurrency(outSummary.total_brokerage_outstanding) }}
              </div>
              <div style="font-size: 11px; color: #92400e; margin-top: 4px;">
                Settled: ₹{{ formatCurrency(outSummary.total_brokerage_settled) }}
              </div>
            </div>

            <!-- Total Sales Trade Outstanding -->
            <div class="register-metric-card">
              <div class="metric-card-label">Trade Volume Outstanding</div>
              <div class="metric-card-val navy-val">
                ₹ {{ formatCurrency(outSummary.total_trade_outstanding) }}
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 4px;">
                Total Billed: ₹{{ formatCurrency(outSummary.total_trade_volume) }}
              </div>
            </div>

            <!-- Pending Vouchers Count -->
            <div class="register-metric-card">
              <div class="metric-card-label">Pending Sales Vouchers</div>
              <div class="metric-card-val navy-val">
                {{ outSummary.pending_vouchers }}
                <span style="font-size: 13px; font-weight: normal; color: var(--muted);">/ {{ outSummary.total_vouchers }}</span>
              </div>
              <div style="font-size: 11px; color: var(--green); margin-top: 4px;">
                ✓ {{ outSummary.settled_vouchers }} Settled
              </div>
            </div>

            <!-- Brokers with Dues -->
            <div class="register-metric-card">
              <div class="metric-card-label">Brokers With Pending Dues</div>
              <div class="metric-card-val navy-val">
                {{ outSummary.brokers_with_dues }}
                <span style="font-size: 13px; font-weight: normal; color: var(--muted);">/ {{ outSummary.total_brokers }}</span>
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 4px;">
                Volume: {{ formatNumber(outSummary.total_qty) }} Qtl
              </div>
            </div>
          </div>

          <!-- SUB-VIEW A: BROKER-WISE GROUPED SUMMARY -->
          <div v-if="outstandingSubTab === 'brokers'">
            <div class="mobile-scroll-cue">
              <span class="cue-icon">↔</span>
              <span>Scroll horizontally to view all broker summary columns</span>
            </div>
            <div class="register-table-wrapper">
              <table class="data-table register-data-table">
              <thead>
                <tr>
                  <th>Broker Name &amp; ID</th>
                  <th>Location</th>
                  <th>Contact</th>
                  <th style="text-align: right;">Sales Vouchers</th>
                  <th style="text-align: right;">Qty (Qtl)</th>
                  <th style="text-align: right;">Total Trade (₹)</th>
                  <th style="text-align: right;">Trade Due (₹)</th>
                  <th style="text-align: right;">Brokerage Billed (₹)</th>
                  <th style="text-align: right;">Brokerage Due (₹)</th>
                  <th style="text-align: center;">Status</th>
                  <th style="text-align: center;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="brokerSummary.length === 0">
                  <td colspan="11" style="text-align: center; padding: 36px; color: var(--muted);">
                    No sales broker outstandings found.
                  </td>
                </tr>
                <template v-for="b in brokerSummary" :key="b.broker">
                  <tr :style="b.total_brokerage_outstanding > 0 ? 'background: rgba(192, 122, 17, 0.03);' : ''">
                    <td>
                      <div style="font-weight: 700; color: var(--navy);">{{ b.broker_name }}</div>
                      <div style="font-size: 11px; color: var(--muted); font-family: var(--font-mono);">{{ b.broker }}</div>
                    </td>
                    <td>{{ b.city || '—' }}</td>
                    <td>{{ b.mobile_no || '—' }}</td>
                    <td style="text-align: right;">
                      <span style="font-weight: 700;">{{ b.vouchers_count }}</span>
                      <span v-if="b.pending_vouchers_count > 0" class="badge badge-amber" style="margin-left: 4px; font-size: 9.5px;">
                        {{ b.pending_vouchers_count }} due
                      </span>
                    </td>
                    <td style="text-align: right;">{{ formatNumber(b.total_quantity) }}</td>
                    <td style="text-align: right;">₹{{ formatCurrency(b.total_trade_amount) }}</td>
                    <td style="text-align: right; font-weight: 700; color: var(--navy);">
                      ₹{{ formatCurrency(b.total_trade_outstanding) }}
                    </td>
                    <td style="text-align: right;">₹{{ formatCurrency(b.total_brokerage) }}</td>
                    <td
                      style="text-align: right; font-weight: 800; font-size: 14px;"
                      :style="b.total_brokerage_outstanding > 0 ? 'color: #d97706;' : 'color: var(--green);'"
                    >
                      ₹{{ formatCurrency(b.total_brokerage_outstanding) }}
                    </td>
                    <td style="text-align: center;">
                      <span v-if="b.status === 'Settled'" class="badge badge-green">Settled</span>
                      <span v-else-if="b.status === 'High Due'" class="badge badge-red">High Due</span>
                      <span v-else class="badge badge-amber">Due</span>
                    </td>
                    <td style="text-align: center;">
                      <button
                        type="button"
                        class="btn btn-secondary btn-sm"
                        style="font-size: 11px;"
                        @click="toggleBrokerExpand(b.broker)"
                      >
                        {{ expandedBrokers[b.broker] ? '▲ Hide Vouchers' : '▼ View Vouchers (' + b.vouchers.length + ')' }}
                      </button>
                    </td>
                  </tr>

                  <!-- Expanded Voucher Rows for this Broker -->
                  <tr v-if="expandedBrokers[b.broker]">
                    <td colspan="11" style="background: var(--panel-soft); padding: 12px 18px;">
                      <div style="font-weight: 700; font-size: 12.5px; color: var(--navy); margin-bottom: 8px;">
                        📜 Sales Vouchers for {{ b.broker_name }} ({{ b.broker }}):
                      </div>
                      <table class="data-table" style="background: var(--panel); border: 1px solid var(--line);">
                        <thead>
                          <tr>
                            <th>Voucher ID</th>
                            <th>Date</th>
                            <th>Commodity / Item</th>
                            <th style="text-align: right;">Qty (Qtl)</th>
                            <th style="text-align: right;">Rate (₹)</th>
                            <th style="text-align: right;">Trade Due (₹)</th>
                            <th>Brokerage Method</th>
                            <th style="text-align: right;">Brokerage Due (₹)</th>
                            <th style="text-align: center;">Settlement</th>
                            <th style="text-align: center;">Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="v in b.vouchers" :key="v.name">
                            <td style="font-family: var(--font-mono); font-weight: 600;">
                              <a :href="`/app/broker-sales-entry/${v.name}`" target="_blank" style="color: var(--blue); text-decoration: none;">
                                {{ v.name }} ↗
                              </a>
                            </td>
                            <td>{{ v.posting_date }}</td>
                            <td>
                              <div style="font-weight: 600; color: var(--navy);">{{ cleanItemText(v.item_name || v.item) }}</div>
                              <div v-if="getStockGroups(v).length > 0" class="selected-groups-row" style="margin-top: 2px;">
                                <span v-for="grp in getStockGroups(v)" :key="grp" class="badge badge-purple group-pill" style="font-size: 9.5px;">
                                  🏷️ {{ grp }}
                                </span>
                              </div>
                            </td>
                            <td style="text-align: right;">{{ formatNumber(v.quantity) }}</td>
                            <td style="text-align: right;">₹{{ formatCurrency(v.rate) }}</td>
                            <td style="text-align: right; font-weight: 700;">₹{{ formatCurrency(v.outstanding_amount) }}</td>
                            <td>{{ v.brokerage_method }} ({{ v.brokerage_rate }})</td>
                            <td style="text-align: right; font-weight: 800; color: #d97706;">
                              ₹{{ formatCurrency(v.outstanding_brokerage) }}
                            </td>
                            <td style="text-align: center;">
                              <span
                                class="badge"
                                :class="v.settlement_status === 'Settled' ? 'badge-green' : (v.settlement_status === 'Partially Settled' ? 'badge-blue' : 'badge-amber')"
                              >
                                {{ v.settlement_status }}
                              </span>
                            </td>
                            <td style="text-align: center;">
                              <button
                                v-if="v.settlement_status !== 'Settled'"
                                type="button"
                                class="btn btn-sm"
                                style="background: var(--green); color: #fff; font-size: 11px;"
                                @click="openSettleModal(v)"
                              >
                                ⚡ Settle
                              </button>
                              <span v-else style="color: var(--green); font-size: 11px; font-weight: 700;">✓ Settled</span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>

        <!-- SUB-VIEW B: VOUCHER-WISE DETAILED LOG -->
          <div v-else-if="outstandingSubTab === 'vouchers'">
            <div class="mobile-scroll-cue">
              <span class="cue-icon">↔</span>
              <span>Scroll horizontally to view all voucher columns</span>
            </div>
            <div class="register-table-wrapper">
              <table class="data-table register-data-table">
                <thead>
                  <tr>
                    <th>Voucher ID</th>
                    <th>Date &amp; Ageing</th>
                    <th>Broker</th>
                    <th>Item / Commodity</th>
                    <th style="text-align: right;">Qty (Qtl)</th>
                    <th style="text-align: right;">Bags</th>
                    <th style="text-align: right;">Sale Rate (₹)</th>
                    <th style="text-align: right;">Total Trade (₹)</th>
                    <th style="text-align: right;">Trade Due (₹)</th>
                    <th>Method &amp; Rate</th>
                    <th style="text-align: right;">Brokerage (₹)</th>
                    <th style="text-align: right;">Brokerage Due (₹)</th>
                    <th style="text-align: center;">Settlement</th>
                    <th style="text-align: center;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="outRecords.length === 0">
                    <td colspan="14" style="text-align: center; padding: 36px; color: var(--muted);">
                      No sales vouchers found for selected filters.
                    </td>
                  </tr>
                  <tr
                    v-for="v in outRecords"
                    :key="v.name"
                    :style="v.outstanding_brokerage > 0 ? 'background: rgba(192, 122, 17, 0.03);' : ''"
                  >
                    <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px;">
                      <a :href="`/app/broker-sales-entry/${v.name}`" target="_blank" style="color: var(--blue); text-decoration: none;">
                        {{ v.name }} ↗
                      </a>
                    </td>
                    <td>
                      <div>{{ v.posting_date }}</div>
                      <div style="font-size: 10px; color: var(--muted); font-weight: 600;">
                        {{ v.days_outstanding === 0 ? 'Today' : v.days_outstanding + 'd ago' }} ({{ v.ageing_bucket }})
                      </div>
                    </td>
                    <td>
                      <div style="font-weight: 700; color: var(--navy);">{{ v.broker_name || v.broker }}</div>
                    </td>
                    <td>
                      <div style="font-weight: 600; color: var(--navy);">{{ cleanItemText(v.item_name || v.item) }}</div>
                      <div v-if="getStockGroups(v).length > 0" class="selected-groups-row" style="margin-top: 2px;">
                        <span v-for="grp in getStockGroups(v)" :key="grp" class="badge badge-purple group-pill" style="font-size: 9.5px;">
                          🏷️ {{ grp }}
                        </span>
                      </div>
                    </td>
                  <td style="text-align: right;">{{ formatNumber(v.quantity) }}</td>
                  <td style="text-align: right;">{{ formatNumber(v.bags) }}</td>
                  <td style="text-align: right;">₹{{ formatCurrency(v.rate) }}</td>
                  <td style="text-align: right;">₹{{ formatCurrency(v.trade_amount) }}</td>
                  <td style="text-align: right; font-weight: 700; color: var(--navy);">
                    ₹{{ formatCurrency(v.outstanding_amount) }}
                  </td>
                  <td>
                    <span class="badge badge-blue">{{ v.brokerage_method }}</span>
                    <span style="font-size: 11px; margin-left: 4px;">{{ v.brokerage_rate }}</span>
                  </td>
                  <td style="text-align: right;">₹{{ formatCurrency(v.brokerage_amount) }}</td>
                  <td
                    style="text-align: right; font-weight: 800; font-size: 13.5px;"
                    :style="v.outstanding_brokerage > 0 ? 'color: #d97706;' : 'color: var(--green);'"
                  >
                    ₹{{ formatCurrency(v.outstanding_brokerage) }}
                  </td>
                  <td style="text-align: center;">
                    <span
                      class="badge"
                      :class="v.settlement_status === 'Settled' ? 'badge-green' : (v.settlement_status === 'Partially Settled' ? 'badge-blue' : 'badge-amber')"
                    >
                      {{ v.settlement_status }}
                    </span>
                  </td>
                  <td style="text-align: center;">
                    <button
                      v-if="v.settlement_status !== 'Settled'"
                      type="button"
                      class="btn btn-sm"
                      style="background: var(--green); color: #fff; font-size: 11px;"
                      @click="openSettleModal(v)"
                    >
                      ⚡ Settle
                    </button>
                    <span v-else style="color: var(--green); font-size: 11px; font-weight: 700;">✓ Settled</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- SUB-VIEW C: AGEING BREAKDOWN CARDS -->
          <div v-else-if="outstandingSubTab === 'ageing'">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px;">
              <div
                v-for="(data, bucket) in outSummary.ageing_summary"
                :key="bucket"
                style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 14px 18px;"
              >
                <div style="font-size: 12px; font-weight: 700; color: var(--navy); text-transform: uppercase;">
                  ⏳ {{ bucket }}
                </div>
                <div style="font-size: 22px; font-weight: 800; color: #d97706; margin-top: 6px;">
                  ₹ {{ formatCurrency(data.brokerage) }}
                </div>
                <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">
                  Brokerage Due across <strong>{{ data.count }}</strong> vouchers
                </div>
                <div style="font-size: 12px; color: var(--navy); font-weight: 600; margin-top: 6px; border-top: 1px solid var(--line); padding-top: 6px;">
                  Trade Due: ₹{{ formatCurrency(data.trade_amount) }}
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Right-side Gateway MenuPanel -->
    <MenuPanel
      section-title="Registers Menu"
      :items="menuItems"
      :active-index="currentType === 'SalesOutstanding' ? 1 : (currentType === 'ItemWise' ? 2 : (currentType === 'Purchase' ? 3 : 4))"
      @select="handleSelect"
    />

    <!-- Quick Settlement Modal -->
    <div v-if="isSettleModalOpen" class="modal-overlay" @click.self="isSettleModalOpen = false">
      <div class="modal-box" style="width: 480px; padding: 22px;">
        <div style="font-weight: 700; font-size: 16px; color: var(--navy); margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
          <span>⚡</span>
          <span>Record Settlement for {{ activeVoucher?.name }}</span>
        </div>
        <p style="font-size: 12.5px; color: var(--muted); margin-bottom: 16px;">
          Broker: <strong>{{ activeVoucher?.broker_name || activeVoucher?.broker }}</strong> · Commodity: <strong>{{ cleanItemText(activeVoucher?.item_name || activeVoucher?.item) }}</strong>
        </p>

        <!-- Current Status Breakdown -->
        <div style="background: var(--panel-soft); padding: 12px 14px; border-radius: 6px; border: 1px solid var(--line); margin-bottom: 16px; font-size: 12.5px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div>Total Trade Amount: <strong>₹{{ formatCurrency(activeVoucher?.trade_amount) }}</strong></div>
          <div>Trade Outstanding: <strong style="color: var(--navy);">₹{{ formatCurrency(activeVoucher?.outstanding_amount) }}</strong></div>
          <div>Total Brokerage: <strong>₹{{ formatCurrency(activeVoucher?.brokerage_amount) }}</strong></div>
          <div>Brokerage Outstanding: <strong style="color: #d97706;">₹{{ formatCurrency(activeVoucher?.outstanding_brokerage) }}</strong></div>
        </div>

        <div class="form-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 14px;">
          <div class="form-group">
            <label>Settled Trade Amount (₹)</label>
            <input v-model.number="settleForm.settled_trade_amount" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Settled Brokerage (₹)</label>
            <input v-model.number="settleForm.settled_brokerage" type="number" step="0.01" />
          </div>
        </div>

        <div class="form-group" style="margin-bottom: 18px;">
          <label>Settlement Notes / Bank Particulars</label>
          <input v-model="settleForm.remarks" type="text" placeholder="e.g. Paid in full via Bank Transfer / Cash" />
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); padding-top: 14px;">
          <button
            type="button"
            class="btn btn-sm btn-success"
            style="font-weight: 700;"
            @click="submitQuickSettle(true)"
          >
            ⚡ Mark 100% Full Settled
          </button>

          <div style="display: flex; gap: 8px;">
            <button type="button" class="btn btn-secondary btn-sm" @click="isSettleModalOpen = false">
              Cancel (Esc)
            </button>
            <button type="button" class="btn btn-primary btn-sm" @click="submitQuickSettle(false)">
              Save Settlement
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import TypeaheadSelect from '../components/TypeaheadSelect.vue'
import MenuPanel from '../components/common/MenuPanel.vue'

const route = useRoute()
const router = useRouter()
const { getEntries, searchEntities, getSalesOutstandingRegister, settleSalesEntry, getItemWiseRegister } = useFrappeApi()

// Current register type: 'Purchase' | 'Sell' | 'ItemWise' | 'SalesOutstanding'
const currentType = ref('Purchase')

// Data cleaning & group extraction helpers
const cleanItemText = (val) => {
  if (!val) return ''
  return String(val).replace(/\s*\(\+\d+\s*more\)/gi, '').trim()
}

const getStockGroups = (r) => {
  if (!r) return []
  const list = []

  // Check child items first
  if (r.items && Array.isArray(r.items) && r.items.length > 0) {
    r.items.forEach((it) => {
      if (it && it.stock_group) {
        const cleaned = cleanItemText(it.stock_group)
        cleaned.split(',').forEach((sub) => {
          const s = sub.trim()
          if (s && !list.includes(s)) list.push(s)
        })
      }
    })
  }

  // Check stock_groups_list from API
  if (r.stock_groups_list && Array.isArray(r.stock_groups_list)) {
    r.stock_groups_list.forEach((g) => {
      if (g) {
        const cleaned = cleanItemText(g)
        cleaned.split(',').forEach((sub) => {
          const s = sub.trim()
          if (s && !list.includes(s)) list.push(s)
        })
      }
    })
  }

  // Fallback to parent stock_group field
  if (list.length === 0 && r.stock_group) {
    const cleaned = cleanItemText(r.stock_group)
    cleaned.split(',').forEach((sub) => {
      const s = sub.trim()
      if (s && !list.includes(s)) list.push(s)
    })
  }

  return list
}

// Standard Purchase & Sales state
const records = ref([])
const summary = reactive({
  total_count: 0,
  total_trade: 0,
  total_brokerage: 0,
  total_qty: 0,
})

const filters = reactive({
  from_date: '',
  to_date: '',
  broker: '',
  broker_name: '',
})

// Item-Wise Register state
const itemRecords = ref([])
const expandedItems = reactive({})
const itemSummary = reactive({
  total_items: 0,
  total_purchase_qty: 0,
  total_purchase_trade: 0,
  total_purchase_brokerage: 0,
  total_sales_qty: 0,
  total_sales_trade: 0,
  total_sales_brokerage: 0,
  overall_trade: 0,
  overall_brokerage: 0,
  total_vouchers: 0,
})

const itemFilters = reactive({
  from_date: '',
  to_date: '',
  broker: '',
  broker_name: '',
})

const toggleItemExpand = (itemCode) => {
  expandedItems[itemCode] = !expandedItems[itemCode]
}

const onItemBrokerFilter = (b) => {
  itemFilters.broker = b ? (b.id || b.name) : ''
  itemFilters.broker_name = b ? (b.label || b.name) : ''
  loadItemWiseData()
}

const resetItemFilters = () => {
  itemFilters.from_date = ''
  itemFilters.to_date = ''
  itemFilters.broker = ''
  itemFilters.broker_name = ''
  loadItemWiseData()
}

const loadItemWiseData = async () => {
  try {
    const res = await getItemWiseRegister({
      from_date: itemFilters.from_date || undefined,
      to_date: itemFilters.to_date || undefined,
      broker: itemFilters.broker || undefined,
    })
    itemRecords.value = res.items || []
    if (res.summary) {
      Object.assign(itemSummary, res.summary)
    }
  } catch (e) {
    console.error('Failed to load item-wise register:', e)
  }
}

// Sales Outstanding Register state
const outstandingSubTab = ref('brokers')
const outRecords = ref([])
const brokerSummary = ref([])
const expandedBrokers = reactive({})
const outSummary = reactive({
  total_vouchers: 0,
  pending_vouchers: 0,
  settled_vouchers: 0,
  total_trade_volume: 0,
  total_trade_outstanding: 0,
  total_brokerage: 0,
  total_brokerage_outstanding: 0,
  total_brokerage_settled: 0,
  total_qty: 0,
  total_bags: 0,
  total_brokers: 0,
  brokers_with_dues: 0,
  ageing_summary: {
    '0-7 Days': { count: 0, trade_amount: 0, brokerage: 0 },
    '8-15 Days': { count: 0, trade_amount: 0, brokerage: 0 },
    '16-30 Days': { count: 0, trade_amount: 0, brokerage: 0 },
    '30+ Days': { count: 0, trade_amount: 0, brokerage: 0 },
  },
})

const outFilters = reactive({
  from_date: '',
  to_date: '',
  broker: '',
  broker_name: '',
  settlement_status: 'All',
  query: '',
})

// Quick Settlement Modal
const isSettleModalOpen = ref(false)
const activeVoucher = ref(null)
const settleForm = reactive({
  settled_trade_amount: 0,
  settled_brokerage: 0,
  remarks: '',
})

const toggleBrokerExpand = (brokerId) => {
  expandedBrokers[brokerId] = !expandedBrokers[brokerId]
}

const openSettleModal = (v) => {
  activeVoucher.value = v
  settleForm.settled_trade_amount = v.trade_amount
  settleForm.settled_brokerage = v.brokerage_amount
  settleForm.remarks = ''
  isSettleModalOpen.value = true
}

const submitQuickSettle = async (isFull = false) => {
  if (!activeVoucher.value) return
  try {
    const res = await settleSalesEntry({
      voucher_id: activeVoucher.value.name,
      settled_trade_amount: isFull ? activeVoucher.value.trade_amount : settleForm.settled_trade_amount,
      settled_brokerage: isFull ? activeVoucher.value.brokerage_amount : settleForm.settled_brokerage,
      remarks: settleForm.remarks || (isFull ? 'Marked 100% full settled' : 'Settlement recorded'),
      mark_full: isFull ? 1 : 0,
    })
    isSettleModalOpen.value = false
    showToast(`✅ ${res.name} settlement recorded (${res.settlement_status})`)
    loadSalesOutstanding()
  } catch (e) {
    showToast('Failed to settle voucher: ' + e.message)
  }
}

const switchType = (type) => {
  currentType.value = type
  router.replace({ query: { type } })
  if (type === 'SalesOutstanding') {
    loadSalesOutstanding()
  } else if (type === 'ItemWise') {
    loadItemWiseData()
  } else {
    loadData()
  }
}

const searchBrokers = async (q) => {
  return await searchEntities('Brokers', q)
}

const searchSellBrokers = async (q) => {
  return await searchEntities('Brokers', q, { for_sales: 1 })
}

const onBrokerFilter = (b) => {
  filters.broker = b ? (b.id || b.name) : ''
  filters.broker_name = b ? (b.label || b.name) : ''
  loadData()
}

const onOutBrokerFilter = (b) => {
  outFilters.broker = b ? (b.id || b.name) : ''
  outFilters.broker_name = b ? (b.label || b.name) : ''
  loadSalesOutstanding()
}

const resetFilters = () => {
  filters.from_date = ''
  filters.to_date = ''
  filters.broker = ''
  filters.broker_name = ''
  loadData()
}

const resetOutFilters = () => {
  outFilters.from_date = ''
  outFilters.to_date = ''
  outFilters.broker = ''
  outFilters.broker_name = ''
  outFilters.settlement_status = 'All'
  outFilters.query = ''
  loadSalesOutstanding()
}

// Load standard Purchase or Sales register entries
const loadData = async () => {
  try {
    const entryTypeParam = (currentType.value === 'Sell' || currentType.value === 'Sales') ? 'Sell' : 'Purchase'
    const res = await getEntries(entryTypeParam, {
      from_date: filters.from_date || undefined,
      to_date: filters.to_date || undefined,
      broker: filters.broker || undefined,
    })
    records.value = res.records || []
    summary.total_count = res.total_count || 0
    summary.total_trade = res.total_trade || 0
    summary.total_brokerage = res.total_brokerage || 0
    summary.total_qty = res.total_qty || 0
    summary.total_gst = res.total_gst || 0
    summary.total_grand = res.total_grand || 0
  } catch (e) {
    console.error('Failed to load register entries:', e)
  }
}

// Load dedicated Sales Outstanding Register
const loadSalesOutstanding = async () => {
  try {
    const res = await getSalesOutstandingRegister({
      from_date: outFilters.from_date || undefined,
      to_date: outFilters.to_date || undefined,
      broker: outFilters.broker || undefined,
      settlement_status: outFilters.settlement_status !== 'All' ? outFilters.settlement_status : undefined,
      query: outFilters.query || undefined,
    })
    outRecords.value = res.records || []
    brokerSummary.value = res.broker_summary || []
    if (res.summary) {
      Object.assign(outSummary, res.summary)
    }
  } catch (e) {
    console.error('Failed to load sales outstandings:', e)
  }
}

const formatCurrency = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (val) => {
  const n = Number(val) || 0
  return n.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

// Right-side Menu Items
const menuItems = [
  { isHeader: true, label: '📋 REGISTERS' },
  { key: 'O', label: 'Sales Outstanding Register', action: () => switchType('SalesOutstanding') },
  { key: 'I', label: 'Item-Wise Register', action: () => switchType('ItemWise') },
  { key: 'P', label: 'Purchase Register', action: () => switchType('Purchase') },
  { key: 'S', label: 'Sales Register', action: () => switchType('Sell') },

  { isHeader: true, label: '⚡ NEW VOUCHERS' },
  { key: 'F9', label: 'New Purchase Entry', action: () => router.push('/purchase') },
  { key: 'F8', label: 'New Sales Entry', action: () => router.push('/sell') },

  { isHeader: true, label: '🏢 MASTERS' },
  { key: 'B', label: 'Brokers Directory', action: () => router.push('/brokers') },
  { key: 'R', label: 'Rate Configurations', action: () => router.push('/rate-configs') },
  { key: 'Esc', label: 'Gateway of Brokerage', action: () => router.push('/') },
]

const handleSelect = (idx) => {
  if (menuItems[idx].isHeader) return
  menuItems[idx].action()
}

const handleTypeFromQuery = (qType) => {
  if (qType === 'SalesOutstanding' || qType === 'Outstanding' || qType === 'outstanding') {
    currentType.value = 'SalesOutstanding'
    loadSalesOutstanding()
  } else if (qType === 'ItemWise' || qType === 'item-wise' || qType === 'items') {
    currentType.value = 'ItemWise'
    loadItemWiseData()
  } else if (qType === 'Sales' || qType === 'Sell') {
    currentType.value = 'Sell'
    loadData()
  } else {
    currentType.value = 'Purchase'
    loadData()
  }
}

watch(
  () => route.query.type,
  (newType) => {
    handleTypeFromQuery(newType)
  }
)

onMounted(() => {
  handleTypeFromQuery(route.query.type)
})
</script>

<style scoped>
/* Responsive Layout & Table Containers */
.register-table-wrapper {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.register-data-table {
  width: 100%;
  min-width: 1100px;
  border-collapse: collapse;
  font-size: 12.5px;
}

.register-data-table th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--navy);
  color: #ffffff;
  padding: 10px 12px;
  font-weight: 700;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-right: 1px solid rgba(255, 255, 255, 0.12);
  white-space: nowrap;
}

.register-data-table th:last-child {
  border-right: none;
}

.register-data-table td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--line);
  border-right: 1px solid var(--line);
  color: var(--text);
  vertical-align: middle;
}

.register-data-table td:last-child {
  border-right: none;
}

.register-data-table tr:hover {
  background: var(--table-hover);
}

/* Specific Column Sizing & Formatting */
.col-id {
  min-width: 125px;
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 12px;
}

.entry-link {
  color: var(--blue);
  text-decoration: none;
  font-weight: 600;
}

.entry-link:hover {
  text-decoration: underline;
}

.col-date {
  min-width: 95px;
  white-space: nowrap;
  font-size: 12px;
}

.col-broker {
  min-width: 160px;
  max-width: 230px;
  white-space: normal;
  line-height: 1.35;
}

.broker-name-cell {
  font-weight: 700;
  color: var(--navy);
}

.broker-id-sub {
  font-size: 10.5px;
  color: var(--muted);
  font-family: var(--font-mono);
}

/* Commodity & Group Column - Key Deliverable */
.col-commodity {
  min-width: 270px;
  max-width: 380px;
  white-space: normal !important;
}

.commodity-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 2px 0;
}

.commodity-items-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.commodity-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 2px 0;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.06);
}

.commodity-item-row:last-child {
  border-bottom: none;
}

.commodity-item-title {
  font-weight: 600;
  color: var(--navy);
  font-size: 12.5px;
  word-break: break-word;
}

.group-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.3px;
}

.selected-groups-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 3px;
  padding-top: 3px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.selected-groups-caption {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.5px;
  margin-right: 2px;
}

.col-num {
  min-width: 120px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.subtotal-cell {
  color: var(--navy);
}

.col-gst {
  min-width: 125px;
  text-align: right;
  font-size: 11.5px;
  color: #166534;
}

.col-grand {
  min-width: 130px;
  text-align: right;
  font-weight: 800;
  color: var(--blue);
}

.col-method {
  min-width: 95px;
  text-align: center;
}

.col-rate {
  min-width: 110px;
  text-align: right;
  font-family: var(--font-mono);
}

.col-brk {
  min-width: 115px;
  text-align: right;
  font-weight: 800;
  color: var(--green);
}

.col-status {
  min-width: 80px;
  text-align: center;
}

.empty-cell {
  text-align: center;
  padding: 36px;
  color: var(--muted);
}

.muted-note {
  font-size: 11px;
  color: var(--muted);
}

/* Mobile Scroll Cue */
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

/* Responsive Metric Summary Ribbon */
.register-metric-ribbon {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.register-metric-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 12px 14px;
  min-width: 0;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.register-metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
}

.metric-card-label {
  font-size: 10.5px;
  color: var(--muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.metric-card-val {
  font-size: clamp(16px, 1.6vw, 22px);
  font-weight: 800;
  margin-top: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.navy-val { color: var(--navy); }
.green-text { color: #166534; }
.blue-text { color: var(--blue); }
.brk-text { color: var(--green); }

.metric-card-gst {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.metric-card-grand {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.metric-card-brokerage {
  background: var(--green-soft);
  border-color: rgba(27, 135, 63, 0.2);
}

/* Responsive Filter Bar */
.register-filter-bar {
  background: var(--panel-soft);
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid var(--line);
  margin-bottom: 16px;
  display: flex;
  gap: 14px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-date {
  min-width: 140px;
  flex: 1 1 140px;
}

.filter-broker {
  min-width: 220px;
  flex: 2 1 220px;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
}

/* Media Queries for Mobile & Tablet Responsiveness */
@media (max-width: 1024px) {
  .mobile-scroll-cue {
    display: flex;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .register-tabs-group {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
  }

  .register-tabs-group .btn {
    width: 100%;
    justify-content: center;
    font-size: 11.5px;
    padding: 7px 8px;
  }

  .register-filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 12px;
  }

  .filter-date,
  .filter-broker,
  .filter-actions {
    width: 100% !important;
    min-width: 0 !important;
    flex: none !important;
  }

  .filter-actions .btn {
    width: 100%;
  }

  .register-metric-ribbon {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .register-metric-card {
    padding: 10px 12px;
  }

  .metric-card-val {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .register-tabs-group {
    grid-template-columns: 1fr;
  }

  .register-metric-ribbon {
    grid-template-columns: 1fr;
  }
}
</style>
