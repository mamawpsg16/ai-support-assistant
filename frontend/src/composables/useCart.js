// useCart.js — the shopping cart, shared across the whole app.
//
// The design's cart appears in three places at once: the count badge in the header,
// the "Add to cart" buttons on the Store page, and the slide-in cart sidebar. They all
// must read and write the SAME cart. So unlike useAsync/useCrud (which create fresh
// state each call), this module creates its reactive state ONCE, at module load, and
// every import shares it.
//
// That's the "module singleton" pattern: because `state` is declared at the top level
// of the module (not inside the exported function), Node/Vite evaluate it a single time
// and hand the same object to every `useCart()` caller. It's a lightweight store
// without pulling in Pinia/Vuex.

import { reactive, computed } from 'vue'

// reactive() makes a plain object deeply reactive — mutating state.items or state.open
// re-renders any component using them.
const state = reactive({
  items: [], // [{ id, name, price, qty }]
  open: false, // is the cart sidebar showing?
})

const TAX_RATE = 0.08 // 8% — matches the design's checkout summary.

// --- Derived totals (computed = auto-recalculate when items change) ---------------
const count = computed(() => state.items.reduce((sum, i) => sum + i.qty, 0))
const subtotal = computed(() => state.items.reduce((sum, i) => sum + i.price * i.qty, 0))
const tax = computed(() => subtotal.value * TAX_RATE)
const total = computed(() => subtotal.value + tax.value)
const isEmpty = computed(() => count.value === 0)

// --- Mutations --------------------------------------------------------------------

// Add a product to the cart, or bump its quantity if it's already in there.
// `product` is a backend product ({ id, name, price, ... }); we copy only what the
// cart needs so later catalog edits don't mutate the cart line.
function add(product) {
  const existing = state.items.find((i) => i.id === product.id)
  if (existing) {
    existing.qty += 1
  } else {
    state.items.push({ id: product.id, name: product.name, price: product.price, qty: 1 })
  }
}

// Change a line's quantity by delta (+1 / -1). Hitting 0 removes the line.
function changeQty(id, delta) {
  const item = state.items.find((i) => i.id === id)
  if (!item) return
  item.qty += delta
  if (item.qty <= 0) {
    state.items = state.items.filter((i) => i.id !== id)
  }
}

function clear() {
  state.items = []
}

// Sidebar open/close helpers.
function openCart() {
  state.open = true
}
function closeCart() {
  state.open = false
}
function toggleCart() {
  state.open = !state.open
}

// The composable just hands back the shared state + helpers. Every caller gets the
// same cart instance.
export function useCart() {
  return {
    state,
    count,
    subtotal,
    tax,
    total,
    isEmpty,
    add,
    changeQty,
    clear,
    openCart,
    closeCart,
    toggleCart,
  }
}
