<!--
  CheckoutCancel.vue — Stripe redirects here if the customer cancels the payment
  (matches CHECKOUT_CANCEL_URL in the backend config). No order change happens.
-->
<template>
  <div class="text-center py-5">
    <div class="display-1">🚫</div>
    <h2 class="mt-3">Payment canceled</h2>
    <p class="text-muted">No charge was made. You can try again anytime.</p>
    <RouterLink class="btn btn-primary mt-2" to="/">Back to store</RouterLink>
  </div>
</template>
