// router/index.js — maps URL paths to page components (views).
//
// vue-router swaps which view shows inside <router-view/> based on the URL, without
// reloading the page. "history" mode keeps URLs clean (/orders, not /#/orders).

import { createRouter, createWebHistory } from 'vue-router'

// Lazy-load views: each page's code downloads only when first visited (smaller initial load).
const routes = [
  { path: '/', name: 'store', component: () => import('../views/StoreView.vue') },
  { path: '/orders', name: 'orders', component: () => import('../views/OrdersView.vue') },
  {
    path: '/subscriptions',
    name: 'subscriptions',
    component: () => import('../views/SubscriptionsView.vue'),
  },
  { path: '/manage', name: 'manage', component: () => import('../views/ManageView.vue') },

  // Stripe redirects the customer back to these after the hosted checkout page.
  {
    path: '/checkout/success',
    name: 'checkout-success',
    component: () => import('../views/CheckoutSuccess.vue'),
  },
  {
    path: '/checkout/cancel',
    name: 'checkout-cancel',
    component: () => import('../views/CheckoutCancel.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
