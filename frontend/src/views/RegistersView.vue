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
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
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
          <div style="background: var(--panel-soft); padding: 12px 16px; border-radius: 6px; border: 1px solid var(--line); margin-bottom: 16px; display: flex; gap: 14px; align-items: flex-end; flex-wrap: wrap;">
            <div class="form-group" style="min-width: 140px;">
              <label>From Date</label>
              <input v-model="filters.from_date" type="date" @change="loadData" />
            </div>

            <div class="form-group" style="min-width: 140px;">
              <label>To Date</label>
              <input v-model="filters.to_date" type="date" @change="loadData" />
            </div>

            <div class="form-group" style="min-width: 240px;">
              <label>Filter by Broker</label>
              <TypeaheadSelect
                v-model="filters.broker"
                :label="filters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchBrokers"
                @change="onBrokerFilter"
              />
            </div>

            <button type="button" class="btn btn-secondary btn-sm" style="margin-bottom: 2px;" @click="resetFilters">
              Reset Filters
            </button>
          </div>

          <!-- Metric Summary Ribbon -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Total Vouchers</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                {{ summary.total_count }}
              </div>
            </div>

            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Total Quantity (Qtl)</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                {{ formatNumber(summary.total_qty) }} Qtl
              </div>
            </div>

            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--navy); font-weight: 700; text-transform: uppercase;">Trade Subtotal</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                ₹ {{ formatCurrency(summary.total_trade) }}
              </div>
            </div>

            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: #166534; font-weight: 700; text-transform: uppercase;">Total GST</div>
              <div style="font-size: 20px; font-weight: 800; color: #166534; margin-top: 2px;">
                ₹ {{ formatCurrency(summary.total_gst || 0) }}
              </div>
            </div>

            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--blue); font-weight: 700; text-transform: uppercase;">Grand Total</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--blue); margin-top: 2px;">
                ₹ {{ formatCurrency(summary.total_grand || summary.total_trade) }}
              </div>
            </div>

            <div style="background: var(--green-soft); border: 1px solid rgba(27, 135, 63, 0.2); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--green); font-weight: 700; text-transform: uppercase;">Total Brokerage</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--green); margin-top: 2px;">
                ₹ {{ formatCurrency(summary.total_brokerage) }}
              </div>
            </div>
          </div>

          <!-- Table of Entries -->
          <div style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Entry ID</th>
                  <th>Date</th>
                  <th>Broker (Sole Party)</th>
                  <th>Commodity &amp; Group</th>
                  <th style="text-align: right;">Trade Subtotal (₹)</th>
                  <th style="text-align: right;">GST Rate</th>
                  <th style="text-align: right;">Grand Total (₹)</th>
                  <th>Method</th>
                  <th style="text-align: right;">Brokerage Rate</th>
                  <th style="text-align: right;">Brokerage (₹)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="records.length === 0">
                  <td colspan="11" style="text-align: center; padding: 36px; color: var(--muted);">
                    No {{ currentType }} entries found for selected criteria.
                  </td>
                </tr>
                <tr v-for="r in records" :key="r.name">
                  <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px;">
                    <a :href="`/app/${(currentType === 'Sell' || currentType === 'Sales') ? 'broker-sales-entry' : 'broker-purchase-entry'}/${r.name}`" target="_blank" style="color: var(--blue); text-decoration: none;">
                      {{ r.name }} ↗
                    </a>
                  </td>
                  <td>{{ r.posting_date }}</td>
                  <td style="font-weight: 600;">{{ r.broker_name || r.broker }}</td>
                  <td>
                    <div style="font-weight: 600;">{{ r.item_name || r.item }}</div>
                    <div v-if="r.items_count > 1" style="font-size: 10.5px; color: var(--blue); margin-top: 1px; font-weight: 600;">
                      📦 {{ r.items_count }} Items Combined
                    </div>
                    <span v-if="r.stock_group" class="badge badge-purple" style="font-size: 10px; margin-top: 2px;">
                      🏷️ {{ r.stock_group }}
                    </span>
                  </td>
                  <td style="text-align: right; font-weight: 600; color: var(--navy);">
                    ₹{{ formatCurrency(r.trade_amount) }}
                  </td>
                  <td style="text-align: right; font-size: 11.5px; color: #166534;">
                    {{ r.gst_rate !== undefined ? r.gst_rate : 5 }}% (₹{{ formatCurrency(r.total_gst_amount || 0) }})
                  </td>
                  <td style="text-align: right; font-weight: 700; color: var(--blue);">
                    ₹{{ formatCurrency(r.grand_total || r.trade_amount) }}
                  </td>
                  <td>
                    <span v-if="r.items_count > 1" class="badge badge-purple">Multi-Item</span>
                    <span v-else class="badge" :class="(currentType === 'Sell' || currentType === 'Sales') ? 'badge-green' : 'badge-blue'">{{ r.brokerage_method }}</span>
                  </td>
                  <td style="text-align: right; font-family: var(--font-mono);">
                    <span v-if="r.items_count > 1" style="font-size: 11px; color: var(--muted);">Multi-Terms</span>
                    <span v-else>{{ r.brokerage_method === 'Percentage' ? `${r.brokerage_rate}%` : (r.brokerage_method === 'Per Bag' ? `₹${r.brokerage_rate}/bag` : `₹${r.brokerage_rate}/qtl`) }}</span>
                  </td>
                  <td style="text-align: right; font-weight: 800; color: var(--green);">
                    ₹{{ formatCurrency(r.brokerage_amount) }}
                  </td>
                  <td>
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
          <div style="background: var(--panel-soft); padding: 12px 16px; border-radius: 6px; border: 1px solid var(--line); margin-bottom: 16px; display: flex; gap: 14px; align-items: flex-end; flex-wrap: wrap;">
            <div class="form-group" style="min-width: 140px;">
              <label>From Date</label>
              <input v-model="itemFilters.from_date" type="date" @change="loadItemWiseData" />
            </div>

            <div class="form-group" style="min-width: 140px;">
              <label>To Date</label>
              <input v-model="itemFilters.to_date" type="date" @change="loadItemWiseData" />
            </div>

            <div class="form-group" style="min-width: 240px;">
              <label>Filter by Broker</label>
              <TypeaheadSelect
                v-model="itemFilters.broker"
                :label="itemFilters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchBrokers"
                @change="onItemBrokerFilter"
              />
            </div>

            <button type="button" class="btn btn-secondary btn-sm" style="margin-bottom: 2px;" @click="resetItemFilters">
              Reset Filters
            </button>
          </div>

          <!-- Metric Summary Ribbon -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Total Commodities</div>
              <div style="font-size: 20px; font-weight: 800; color: #7c3aed; margin-top: 2px;">
                {{ itemSummary.total_items }}
              </div>
            </div>

            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--blue); font-weight: 700; text-transform: uppercase;">Purchase Volume</div>
              <div style="font-size: 18px; font-weight: 800; color: var(--blue); margin-top: 2px;">
                {{ formatNumber(itemSummary.total_purchase_qty) }} Qtl
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">
                Trade: ₹{{ formatCurrency(itemSummary.total_purchase_trade) }}
              </div>
            </div>

            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: #166534; font-weight: 700; text-transform: uppercase;">Sales Volume</div>
              <div style="font-size: 18px; font-weight: 800; color: #166534; margin-top: 2px;">
                {{ formatNumber(itemSummary.total_sales_qty) }} Qtl
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 2px;">
                Trade: ₹{{ formatCurrency(itemSummary.total_sales_trade) }}
              </div>
            </div>

            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--navy); font-weight: 700; text-transform: uppercase;">Overall Trade Volume</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                ₹ {{ formatCurrency(itemSummary.overall_trade) }}
              </div>
            </div>

            <div style="background: var(--green-soft); border: 1px solid rgba(27, 135, 63, 0.2); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--green); font-weight: 700; text-transform: uppercase;">Combined Brokerage</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--green); margin-top: 2px;">
                ₹ {{ formatCurrency(itemSummary.overall_brokerage) }}
              </div>
            </div>

            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Total Vouchers</div>
              <div style="font-size: 20px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                {{ itemSummary.total_vouchers }}
              </div>
            </div>
          </div>

          <!-- Table of Item-Wise Entries -->
          <div style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
            <table class="data-table">
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
          <div style="background: var(--panel-soft); padding: 12px 16px; border-radius: 6px; border: 1px solid var(--line); margin-bottom: 16px; display: flex; gap: 14px; align-items: flex-end; flex-wrap: wrap;">
            <div class="form-group" style="min-width: 140px;">
              <label>From Date</label>
              <input v-model="outFilters.from_date" type="date" @change="loadSalesOutstanding" />
            </div>

            <div class="form-group" style="min-width: 140px;">
              <label>To Date</label>
              <input v-model="outFilters.to_date" type="date" @change="loadSalesOutstanding" />
            </div>

            <div class="form-group" style="min-width: 240px;">
              <label>Filter Broker</label>
              <TypeaheadSelect
                v-model="outFilters.broker"
                :label="outFilters.broker_name"
                placeholder="All Brokers..."
                :fetch-fn="searchSellBrokers"
                @change="onOutBrokerFilter"
              />
            </div>

            <div class="form-group" style="flex: 1; min-width: 200px;">
              <label>Instant Search (Voucher / Broker / Item)</label>
              <input
                v-model="outFilters.query"
                type="text"
                placeholder="Filter results..."
                @input="loadSalesOutstanding"
              />
            </div>

            <button type="button" class="btn btn-secondary btn-sm" style="margin-bottom: 2px;" @click="resetOutFilters">
              Reset
            </button>
          </div>

          <!-- Outstanding KPI Ribbon -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <!-- Total Brokerage Due (Highlighted in Amber/Red) -->
            <div style="background: #fff8eb; border: 1px solid #fde68a; border-radius: 6px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
              <div style="font-size: 11px; color: #b45309; font-weight: 700; text-transform: uppercase;">Brokerage Due (Sell)</div>
              <div style="font-size: 22px; font-weight: 800; color: #d97706; margin-top: 2px;">
                ₹ {{ formatCurrency(outSummary.total_brokerage_outstanding) }}
              </div>
              <div style="font-size: 11px; color: #92400e; margin-top: 4px;">
                Settled: ₹{{ formatCurrency(outSummary.total_brokerage_settled) }}
              </div>
            </div>

            <!-- Total Sales Trade Outstanding -->
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--navy); font-weight: 700; text-transform: uppercase;">Trade Volume Outstanding</div>
              <div style="font-size: 22px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                ₹ {{ formatCurrency(outSummary.total_trade_outstanding) }}
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 4px;">
                Total Billed: ₹{{ formatCurrency(outSummary.total_trade_volume) }}
              </div>
            </div>

            <!-- Pending Vouchers Count -->
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Pending Sales Vouchers</div>
              <div style="font-size: 22px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                {{ outSummary.pending_vouchers }}
                <span style="font-size: 13px; font-weight: normal; color: var(--muted);">/ {{ outSummary.total_vouchers }}</span>
              </div>
              <div style="font-size: 11px; color: var(--green); margin-top: 4px;">
                ✓ {{ outSummary.settled_vouchers }} Settled
              </div>
            </div>

            <!-- Brokers with Dues -->
            <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px;">
              <div style="font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Brokers With Pending Dues</div>
              <div style="font-size: 22px; font-weight: 800; color: var(--navy); margin-top: 2px;">
                {{ outSummary.brokers_with_dues }}
                <span style="font-size: 13px; font-weight: normal; color: var(--muted);">/ {{ outSummary.total_brokers }}</span>
              </div>
              <div style="font-size: 11px; color: var(--muted); margin-top: 4px;">
                Volume: {{ formatNumber(outSummary.total_qty) }} Qtl
              </div>
            </div>
          </div>

          <!-- SUB-VIEW A: BROKER-WISE GROUPED SUMMARY -->
          <div v-if="outstandingSubTab === 'brokers'" style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
            <table class="data-table">
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
                            <td>{{ v.item_name || v.item }}</td>
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

          <!-- SUB-VIEW B: VOUCHER-WISE DETAILED LOG -->
          <div v-else-if="outstandingSubTab === 'vouchers'" style="border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;">
            <table class="data-table">
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
                  <td>{{ v.item_name || v.item }}</td>
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
          Broker: <strong>{{ activeVoucher?.broker_name || activeVoucher?.broker }}</strong> · Commodity: <strong>{{ activeVoucher?.item_name || activeVoucher?.item }}</strong>
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
