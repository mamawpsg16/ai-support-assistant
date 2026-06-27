<!--
  StoreView.vue — the storefront home, restyled to the design.

  Flow (now a cart, not buy-one-at-a-time):
    1. Click "Add to cart" on a product  -> useCart().add() + the cart sidebar opens
    2. Adjust quantities in the sidebar
    3. "Checkout with Stripe" (in CartSidebar) -> POST /payments/checkout-cart
       -> redirect to Stripe's hosted page

  No customer picker here anymore: the cart checkout charges for the products directly
  (the server looks up prices), so it doesn't need a customer chosen up front.

  Category chips filter the grid client-side. Categories come from utils/catalog.js
  (the backend product has no category column yet).
-->
<template>
  <div class="store">
    <!-- Category filter bar -->
    <div class="cat-bar">
      <button
        v-for="cat in categories"
        :key="cat"
        class="chip"
        :class="{ 'chip-active': cat === selectedCat }"
        @click="selectedCat = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- loading / error / grid -->
    <div v-if="productsReq.loading.value" class="state">Loading products…</div>
    <div v-else-if="productsReq.error.value" class="state error">{{ productsReq.error.value }}</div>
    <div v-else class="grid">
      <ProductCard
        v-for="p in visibleProducts"
        :key="p.id"
        :product="p"
        @add="addToCart"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { products as productsApi } from '../api'
import { useAsync } from '../composables/useAsync'
import { useCart } from '../composables/useCart'
import { categoryFor, CATEGORY_ORDER } from '../utils/catalog'
import ProductCard from '../components/ProductCard.vue'

const productsReq = useAsync(() => productsApi.list())
onMounted(() => productsReq.run())

// Cart: adding a product opens the sidebar so the change is visible.
const { add, openCart } = useCart()
function addToCart(product) {
  add(product)
  openCart()
}

// Which category chip is selected ("All" shows everything).
const selectedCat = ref('All')

// Chips = "All" + only the categories that actually appear in the loaded products,
// kept in the preferred display order.
const categories = computed(() => {
  const present = new Set((productsReq.data.value || []).map(categoryFor))
  return ['All', ...CATEGORY_ORDER.filter((c) => present.has(c))]
})

const visibleProducts = computed(() => {
  const all = productsReq.data.value || []
  return selectedCat.value === 'All' ? all : all.filter((p) => categoryFor(p) === selectedCat.value)
})
</script>

<style scoped>
.store { animation: fadeIn 0.25s ease; }

/* Category chips */
.cat-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  padding: 0 2px;
}
.chip {
  background: var(--surface);
  color: #555;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 12px;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.12s;
}
.chip:hover { border-color: var(--orange); color: var(--orange); }
.chip-active {
  background: var(--orange);
  color: #fff;
  border-color: var(--orange);
  font-weight: 600;
  padding: 6px 16px;
}
.chip-active:hover { color: #fff; }

/* Product grid — auto-fills as many ~160px columns as fit. */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.state { padding: 48px 0; text-align: center; color: var(--muted); }
.state.error { color: var(--danger); }
</style>
