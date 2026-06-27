<!--
  CheckoutSuccess.vue — Stripe redirects here after a successful payment
  (matches CHECKOUT_SUCCESS_URL in the backend config).
  The order is marked paid by the webhook, not by this page.
-->
<template>
  <div class="result ui-view">
    <div class="result-icon"><Icon name="check" :size="34" stroke="var(--sage)" /></div>
    <h1 class="ui-h1">Payment confirmed</h1>
    <p class="result-sub">Your order is being processed. Confirmation sent to your email.</p>
    <div class="result-actions">
      <RouterLink class="ui-btn ui-btn-accent" to="/">Back to store</RouterLink>
      <RouterLink class="ui-btn ui-btn-ghost" to="/orders">View orders</RouterLink>
    </div>
  </div>
</template>

<script setup>
import Icon from '../components/Icon.vue'
</script>

<style scoped>
.result { text-align: center; padding: 64px 16px; }
.result-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: var(--sage-tint);
  border: 2px solid rgba(74, 122, 88, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-sub { font-size: 14px; color: var(--muted); max-width: 320px; margin: 0 auto 20px; line-height: 20px; }
.result-actions { display: flex; gap: 10px; justify-content: center; }
.result-actions a { text-decoration: none; }
</style>
