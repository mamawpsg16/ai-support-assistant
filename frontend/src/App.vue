<!--
  App.vue — the ROOT shell, restyled to the new design.

  Layout (matches Storefront.dc.html):
    - a sticky, frosted-glass HEADER: logo (left) · pill nav (centre) · cart button (right)
    - a centred MAIN where the current route renders (<RouterView/>)
    - the slide-in CartSidebar and the floating ChatWidget, which live OUTSIDE <main>
      so they float over every page.

  We keep vue-router for navigation (the design toggled views with a variable; routing
  is the real app's equivalent and gives us real URLs). RouterLink renders an <a> that
  changes the URL without a full reload; `exact-active-class`/`active-class` mark the
  current page so we can highlight its pill.
-->
<template>
  <div class="app">
    <header class="hdr">
      <!-- Logo -->
      <RouterLink to="/" class="brand">
        <span class="brand-mark"><Icon name="bag" :size="13" /></span>
        <span class="brand-name">Storefront</span>
      </RouterLink>

      <!-- Centre nav -->
      <nav class="nav">
        <RouterLink to="/" class="pill" exact-active-class="pill-active">Store</RouterLink>
        <RouterLink to="/orders" class="pill" active-class="pill-active">Orders</RouterLink>
        <RouterLink to="/subscriptions" class="pill" active-class="pill-active">Subscriptions</RouterLink>
        <RouterLink to="/manage" class="pill" active-class="pill-active">Manage</RouterLink>
      </nav>

      <!-- Cart -->
      <div class="hdr-right">
        <button class="cart-btn" @click="toggleCart">
          <Icon name="cart" :size="18" />
          Cart
          <span v-if="count > 0" class="cart-count">{{ count }}</span>
        </button>
      </div>
    </header>

    <main class="main">
      <RouterView />
    </main>

    <!-- Float over every page. -->
    <CartSidebar />
    <ChatWidget />
  </div>
</template>

<script setup>
import Icon from './components/Icon.vue'
import CartSidebar from './components/CartSidebar.vue'
import ChatWidget from './components/ChatWidget.vue'
import { useCart } from './composables/useCart'

// Shared cart: the header shows the live item count and opens the sidebar.
const { count, toggleCart } = useCart()
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--cream);
  color: var(--ink);
  font-family: var(--font-body);
}

/* --- Header ------------------------------------------------------------------- */
.hdr {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px); /* the "frosted glass" effect over scrolled content */
  border-bottom: 1px solid var(--line);
}

/* Logo */
.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 140px;
  text-decoration: none;
}
.brand-mark {
  width: 26px;
  height: 26px;
  background: var(--sage);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.brand-name {
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.3px;
  color: var(--ink);
}

/* Centre nav pills */
.nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: center;
}
.pill {
  border: none;
  border-radius: 7px;
  padding: 6px 14px;
  font-size: 14px;
  font-family: var(--font-body);
  color: var(--muted);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.12s;
}
.pill:hover { color: var(--ink); }
/* Current page pill: ink background, white text (set by router on the active link). */
.pill-active {
  background: var(--ink);
  color: #fff;
  font-weight: 600;
}

/* Cart button (right) */
.hdr-right { min-width: 140px; display: flex; justify-content: flex-end; }
.cart-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--ink);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: opacity 0.12s;
}
.cart-btn:hover { opacity: 0.85; }
.cart-count {
  background: var(--orange);
  color: #fff;
  border-radius: 20px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 700;
}

/* --- Main --------------------------------------------------------------------- */
.main { max-width: 1440px; margin: 0 auto; padding: 16px 16px 40px; }
</style>
