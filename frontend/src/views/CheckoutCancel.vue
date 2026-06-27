<!--
  CheckoutCancel.vue — Stripe redirects here if the customer cancels the payment
  (matches CHECKOUT_CANCEL_URL in the backend config). No order change happens.
-->
<template>
  <div class="result ui-view">
    <div class="result-icon"><Icon name="x" :size="30" stroke="var(--danger)" /></div>
    <h1 class="ui-h1">Payment canceled</h1>
    <p class="result-sub">No charge was made. You can try again anytime.</p>
    <div class="result-actions">
      <RouterLink class="ui-btn ui-btn-accent" to="/">Back to store</RouterLink>
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
  background: #fdf2f0;
  border: 2px solid rgba(201, 105, 90, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-sub { font-size: 14px; color: var(--muted); max-width: 320px; margin: 0 auto 20px; line-height: 20px; }
.result-actions { display: flex; gap: 10px; justify-content: center; }
.result-actions a { text-decoration: none; }
</style>
