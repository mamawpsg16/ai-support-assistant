<!--
  CheckoutSuccess.vue — Stripe redirects here after a successful payment
  (matches CHECKOUT_SUCCESS_URL in the backend config).
  The order is marked paid by the webhook, not by this page.
-->
<template>
  <div class="text-center py-5">
    <div class="display-1">✅</div>
    <h2 class="mt-3">Payment successful</h2>
    <p class="text-muted">Your order is being processed. Thanks for your purchase!</p>
    <RouterLink class="btn btn-primary mt-2" to="/">Back to store</RouterLink>
    <RouterLink class="btn btn-outline-secondary mt-2 ms-2" to="/orders">View orders</RouterLink>
  </div>
</template>
