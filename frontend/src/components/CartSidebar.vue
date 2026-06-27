<!--
  CartSidebar.vue — the slide-in shopping cart (ported from the design's cart panel).

  It reads the shared cart from useCart(), so the header's count badge and the Store
  page's "Add to cart" buttons all feed THIS panel. It renders:
    - a dim overlay behind the panel (click it to close),
    - the panel itself (header, scrolling line-item list, totals footer),
    - an empty state when the cart has nothing in it.

  Phase status: the visual shell + open/close + quantity steppers work now. The cart
  gets ITEMS once the Store page's "Add to cart" lands (next phase), and the
  "Checkout with Stripe" button gets wired to the real Stripe flow then too.
-->
<template>
  <Transition name="cart">
    <div v-if="state.open" class="cart-root">
      <!-- Dim, blurred backdrop. Clicking it closes the cart. -->
      <div class="cart-overlay" @click="closeCart" />

      <!-- The panel. -->
      <aside class="cart-panel">
        <!-- Header -->
        <header class="cart-head">
          <div>
            <div class="cart-title">Cart</div>
            <div class="cart-sub">{{ count }} item{{ count === 1 ? '' : 's' }}</div>
          </div>
          <button class="icon-btn" @click="closeCart" aria-label="Close cart">
            <Icon name="x" :size="16" />
          </button>
        </header>

        <!-- Line items (scrolls) -->
        <div class="cart-body">
          <!-- Empty state -->
          <div v-if="isEmpty" class="cart-empty">
            <Icon name="cart" :size="28" />
            <p>Nothing here yet</p>
          </div>

          <!-- One row per cart line -->
          <div v-for="item in state.items" :key="item.id" class="cart-line">
            <div class="cart-line-info">
              <div class="cart-line-name">{{ item.name }}</div>
              <div class="cart-line-unit">{{ formatMoney(item.price) }} each</div>
            </div>

            <!-- Quantity stepper -->
            <div class="stepper">
              <button class="step-btn" @click="changeQty(item.id, -1)" aria-label="Decrease">
                <Icon name="minus" :size="13" />
              </button>
              <span class="step-qty">{{ item.qty }}</span>
              <button class="step-btn" @click="changeQty(item.id, 1)" aria-label="Increase">
                <Icon name="plus" :size="13" />
              </button>
            </div>

            <span class="cart-line-total">{{ formatMoney(item.price * item.qty) }}</span>
          </div>
        </div>

        <!-- Totals + checkout -->
        <footer class="cart-foot">
          <div class="cart-row"><span>Subtotal</span><span class="val">{{ formatMoney(subtotal) }}</span></div>
          <div class="cart-row"><span>Tax (8%)</span><span class="val">{{ formatMoney(tax) }}</span></div>
          <div class="cart-divider" />
          <div class="cart-row total"><span>Total</span><span>{{ formatMoney(total) }}</span></div>
          <p v-if="error" class="cart-err">{{ error }}</p>
          <button class="checkout-btn" :disabled="isEmpty || loading" @click="checkout">
            {{ loading ? 'Redirecting…' : 'Checkout with Stripe' }}
          </button>
        </footer>
      </aside>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'
import Icon from './Icon.vue'
import { useCart } from '../composables/useCart'
import { payments } from '../api'
import { formatMoney } from '../utils/format'

const { state, count, subtotal, tax, total, isEmpty, changeQty, closeCart } = useCart()

const loading = ref(false)
const error = ref('')

// Ask the backend to build a Stripe Checkout Session for the whole cart, then send the
// browser to Stripe's hosted page. We pass only product_id + quantity; the server looks
// up the prices itself (see POST /payments/checkout-cart).
async function checkout() {
  if (isEmpty.value || loading.value) return
  error.value = ''
  loading.value = true
  try {
    const items = state.items.map((i) => ({ product_id: i.id, quantity: i.qty }))
    const { checkout_url } = await payments.checkoutCart(items)
    window.location.href = checkout_url
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Checkout failed'
    loading.value = false
  }
}
</script>

<style scoped>
/*
  Pixel values come straight from the design. The cart slides in from the right; the
  <Transition> wrapper plays the design's slideRight (panel) + fadeIn (overlay) by
  animating these enter/leave classes.
*/
.cart-root { position: fixed; inset: 0; z-index: 200; }

.cart-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(3px);
}

.cart-panel {
  position: absolute;
  top: 0;
  right: 0;
  height: 100vh;
  width: 380px;
  max-width: 92vw;
  background: var(--surface);
  border-left: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

/* Header */
.cart-head {
  padding: 20px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cart-title { font-family: var(--font-display); font-size: 20px; font-weight: 500; }
.cart-sub { font-size: 12px; color: var(--muted-2); margin-top: 2px; }

/* A small square icon button, reused for the close (x). */
.icon-btn {
  width: 32px;
  height: 32px;
  background: var(--cream);
  border: none;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--muted);
  transition: all 0.12s;
}
.icon-btn:hover { background: #e8e7e2; color: var(--ink); }

/* Body */
.cart-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cart-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--muted-2);
  padding: 40px 0;
}
.cart-empty :deep(svg) { opacity: 0.5; }
.cart-empty p { font-size: 13px; margin: 0; }

/* Line item */
.cart-line {
  background: var(--surface-2);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.cart-line-info { flex: 1; min-width: 0; }
.cart-line-name {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cart-line-unit { font-size: 12px; color: var(--muted-2); }
.cart-line-total { font-size: 14px; font-weight: 700; min-width: 44px; text-align: right; }

/* Quantity stepper */
.stepper {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid rgba(0, 0, 0, 0.09);
  border-radius: 7px;
  overflow: hidden;
}
.step-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s;
}
.step-btn:hover { background: var(--cream); color: var(--ink); }
.step-qty { padding: 0 10px; font-size: 13px; font-weight: 600; }

/* Footer totals */
.cart-foot { padding: 16px 20px; border-top: 1px solid var(--line); }
.cart-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 5px;
}
.cart-row .val { color: var(--ink); }
.cart-divider { height: 1px; background: var(--line); margin: 7px 0 14px; }
.cart-row.total { font-size: 16px; font-weight: 700; color: var(--ink); margin-bottom: 14px; }

.checkout-btn {
  width: 100%;
  background: var(--ink);
  color: #fff;
  border: none;
  border-radius: 9px;
  padding: 13px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--font-body);
  transition: opacity 0.12s;
}
.checkout-btn:hover { opacity: 0.85; }
.checkout-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.cart-err {
  font-size: 12px;
  color: var(--danger);
  margin: 0 0 10px;
}

/* Enter/leave animation: overlay fades, panel slides in from the right. */
.cart-enter-active .cart-overlay { animation: fadeIn 0.2s ease; }
.cart-enter-active .cart-panel { animation: slideRight 0.22s cubic-bezier(0.2, 0.8, 0.2, 1); }
.cart-leave-active { transition: opacity 0.18s ease; }
.cart-leave-to { opacity: 0; }
</style>
