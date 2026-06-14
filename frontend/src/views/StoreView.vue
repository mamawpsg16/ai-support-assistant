<!--
  StoreView.vue — the storefront home: a grid of products with Buy buttons.

  Buy flow (uses real backend endpoints):
    1. Pick a customer (who's buying).
    2. Click Buy on a product.
    3. POST /orders/                      -> creates a pending order
    4. POST /payments/checkout/{orderId}  -> returns a Stripe checkout_url
    5. window.location = checkout_url     -> Stripe's hosted payment page

  After paying, Stripe redirects to /checkout/success and (with `stripe listen`
  running) the webhook marks the order paid.
-->
<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-end gap-3 mb-4">
      <div>
        <h2 class="mb-1">Store</h2>
        <p class="text-muted mb-0">Pick a customer, then buy a product.</p>
      </div>
      <div style="min-width: 280px">
        <Picker
          v-model="customerId"
          :options="customersReq.data.value || []"
          :loading="customersReq.loading.value"
          title="Buying as"
          placeholder="Search a customer…"
        />
      </div>
    </div>

    <div v-if="buyError" class="alert alert-danger">{{ buyError }}</div>

    <!-- loading / error / grid -->
    <div v-if="productsReq.loading.value" class="text-center text-muted py-5">Loading products…</div>
    <div v-else-if="productsReq.error.value" class="alert alert-danger">
      {{ productsReq.error.value }}
    </div>
    <div v-else class="row g-3">
      <div class="col-12 col-sm-6 col-lg-4" v-for="p in productsReq.data.value || []" :key="p.id">
        <ProductCard :product="p" :disabled="buying" @buy="buy" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { products as productsApi, customers as customersApi, orders, payments } from '../api'
import { useAsync } from '../composables/useAsync'
import Picker from '../components/Picker.vue'
import ProductCard from '../components/ProductCard.vue'

// Who is buying — bound to the customer Picker.
const customerId = ref(null)

// Load products (grid) and customers (picker) via the composable.
const productsReq = useAsync(() => productsApi.list())
const customersReq = useAsync(() => customersApi.list())
onMounted(() => {
  productsReq.run()
  customersReq.run()
})

// State while a Buy is in progress.
const buying = ref(false)
const buyError = ref('')

async function buy(product) {
  buyError.value = ''
  if (!customerId.value) {
    buyError.value = 'Pick a customer first.'
    return
  }
  buying.value = true
  try {
    // create the order, then create its checkout session
    const order = await orders.create({
      customer_id: customerId.value,
      product_id: product.id,
      total: product.price,
    })
    const session = await payments.checkout(order.id)
    // send the browser to Stripe's hosted checkout page
    window.location.href = session.checkout_url
  } catch (e) {
    buyError.value = e?.response?.data?.detail || e.message || 'Checkout failed'
    buying.value = false
  }
}
</script>
