<!--
  OrdersView.vue — pick a customer, see their orders (design row layout), refund paid ones.

  Real endpoints (unchanged):
    GET  /support/customer/{id}/orders  -> the customer's orders
    POST /payments/refund/{orderId}     -> refund (backend only allows paid orders)

  The design's order row shows item NAMES; our order stores a product_id, so we also
  load the product list once and map id -> name for a friendlier label.
-->
<template>
  <div class="ui-view">
    <div class="ui-head">
      <h1 class="ui-h1">Orders</h1>
      <p class="ui-sub">Your purchase history.</p>
    </div>

    <div class="picker-row">
      <Picker
        v-model="customerId"
        :options="customersReq.data.value || []"
        :loading="customersReq.loading.value"
        title="Customer"
        placeholder="Search a customer…"
      />
    </div>

    <div v-if="refundError" class="ui-alert">{{ refundError }}</div>

    <p v-if="!customerId" class="ui-state">Pick a customer to see their orders.</p>
    <div v-else-if="ordersReq.loading.value" class="ui-state">Loading orders…</div>
    <div v-else-if="ordersReq.error.value" class="ui-alert">{{ ordersReq.error.value }}</div>
    <p v-else-if="(ordersReq.data.value || []).length === 0" class="ui-state">
      This customer has no orders yet.
    </p>

    <div v-else class="order-list">
      <div v-for="o in ordersReq.data.value" :key="o.id" class="order-row">
        <div class="order-icon"><Icon name="pkg" :size="20" /></div>

        <div class="order-main">
          <div class="order-top">
            <span class="order-id">ORD-{{ o.id }}</span>
            <span class="order-date">{{ formatDateShort(o.created_at) }}</span>
          </div>
          <p class="order-items">{{ productName(o.product_id) }}</p>
        </div>

        <div class="order-end">
          <span class="order-total">{{ formatMoney(o.total) }}</span>
          <StatusBadge :status="o.status" />
          <button
            v-if="o.status === 'paid'"
            class="ui-btn ui-btn-ghost ui-btn-sm"
            :disabled="refundingId === o.id"
            @click="refund(o)"
          >
            {{ refundingId === o.id ? 'Refunding…' : 'Refund' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { support, payments, customers as customersApi, products as productsApi } from '../api'
import { useAsync } from '../composables/useAsync'
import { formatMoney, formatDateShort } from '../utils/format'
import Picker from '../components/Picker.vue'
import StatusBadge from '../components/StatusBadge.vue'
import Icon from '../components/Icon.vue'

const customerId = ref(null)

const customersReq = useAsync(() => customersApi.list())
customersReq.run()

// Products loaded once so we can show names instead of bare ids.
const productsReq = useAsync(() => productsApi.list())
productsReq.run()
const productMap = computed(() => {
  const map = {}
  for (const p of productsReq.data.value || []) map[p.id] = p.name
  return map
})
function productName(id) {
  return productMap.value[id] || `Product #${id}`
}

// Orders for the chosen customer.
const ordersReq = useAsync((id) => support.customerOrders(id))
watch(customerId, (id) => {
  if (id) ordersReq.run(id)
})

// Refund handling.
const refundingId = ref(null)
const refundError = ref('')

async function refund(order) {
  refundError.value = ''
  refundingId.value = order.id
  try {
    await payments.refund(order.id)
    // reload after a beat so the webhook-updated status shows
    setTimeout(() => ordersReq.run(customerId.value), 1500)
  } catch (e) {
    refundError.value = e?.response?.data?.detail || e.message || 'Refund failed'
  } finally {
    refundingId.value = null
  }
}
</script>

<style scoped>
.picker-row { max-width: 360px; margin-bottom: 24px; }

.order-list { display: flex; flex-direction: column; gap: 8px; }

.order-row {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: box-shadow 0.12s;
}
.order-row:hover { box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07); }

.order-icon {
  width: 40px;
  height: 40px;
  background: var(--sage-tint);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--sage);
}

.order-main { flex: 1; min-width: 0; }
.order-top { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.order-id { font-size: 14px; font-weight: 600; }
.order-date { font-size: 12px; color: var(--muted-2); }
.order-items {
  font-size: 13px;
  color: var(--muted);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.order-end { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.order-total { font-size: 15px; font-weight: 700; }
</style>
