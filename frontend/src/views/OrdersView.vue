<!--
  OrdersView.vue — pick a customer, see their orders, refund the paid ones.

  Uses:
    GET  /support/customer/{id}/orders   -> the customer's orders
    POST /payments/refund/{orderId}      -> refund (backend only allows paid orders)

  After a refund, the `charge.refunded` webhook flips the order to refunded; we reload
  the list to show the new status.
-->
<template>
  <div>
    <h2 class="mb-3">Orders</h2>

    <div class="mb-4" style="max-width: 360px">
      <Picker
        v-model="customerId"
        :options="customersReq.data.value || []"
        :loading="customersReq.loading.value"
        title="Customer"
        placeholder="Search a customer…"
      />
    </div>

    <div v-if="refundError" class="alert alert-danger">{{ refundError }}</div>

    <p v-if="!customerId" class="text-muted">Pick a customer to see their orders.</p>

    <div v-else-if="ordersReq.loading.value" class="text-muted">Loading orders…</div>
    <div v-else-if="ordersReq.error.value" class="alert alert-danger">
      {{ ordersReq.error.value }}
    </div>
    <div v-else-if="(ordersReq.data.value || []).length === 0" class="text-muted">
      This customer has no orders yet.
    </div>

    <table v-else class="table align-middle">
      <thead>
        <tr>
          <th>#</th>
          <th>Product ID</th>
          <th>Total</th>
          <th>Status</th>
          <th>Placed</th>
          <th class="text-end">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="o in ordersReq.data.value" :key="o.id">
          <td>{{ o.id }}</td>
          <td>{{ o.product_id }}</td>
          <td>{{ formatMoney(o.total) }}</td>
          <td><StatusBadge :status="o.status" /></td>
          <td class="text-muted small">{{ formatDate(o.created_at) }}</td>
          <td class="text-end">
            <button
              v-if="o.status === 'paid'"
              class="btn btn-outline-warning btn-sm"
              :disabled="refundingId === o.id"
              @click="refund(o)"
            >
              {{ refundingId === o.id ? 'Refunding…' : 'Refund' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { support, payments, customers as customersApi } from '../api'
import { useAsync } from '../composables/useAsync'
import { formatMoney, formatDate } from '../utils/format'
import Picker from '../components/Picker.vue'
import StatusBadge from '../components/StatusBadge.vue'

const customerId = ref(null)

// Customers for the picker — run() fires the fetch now.
const customersReq = useAsync(() => customersApi.list())
customersReq.run()

// Orders for the chosen customer (loaded on demand via the watch below).
const ordersReq = useAsync((id) => support.customerOrders(id))

// When the picked customer changes, (re)load their orders.
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
    // reload so the webhook-updated status shows (give the webhook a moment)
    setTimeout(() => ordersReq.run(customerId.value), 1500)
  } catch (e) {
    refundError.value = e?.response?.data?.detail || e.message || 'Refund failed'
  } finally {
    refundingId.value = null
  }
}
</script>
