// api/index.js — all backend endpoints in one place.
//
// DRY: a `resource()` factory builds the 5 standard CRUD methods for any model, so we
// don't hand-write the same axios calls per resource. Non-CRUD endpoints (support,
// payments) get their own small named helpers.
//
// Every method returns response.data (the JSON body), so callers ignore the axios wrapper.

import { http } from './http'

// resource('customers') -> { list, get, create, update, remove } for /customers/
//
// list(params) and get(id, params) accept optional query params; axios serializes them
// into the URL query string, e.g. list({ skip: 0, limit: 20 }) -> /customers/?skip=0&limit=20
export function resource(name) {
  const base = `/${name}/`
  return {
    list: (params) => http.get(base, { params }).then((r) => r.data),
    get: (id, params) => http.get(`${base}${id}`, { params }).then((r) => r.data),
    create: (data) => http.post(base, data).then((r) => r.data),
    update: (id, data) => http.patch(`${base}${id}`, data).then((r) => r.data),
    remove: (id) => http.delete(`${base}${id}`).then((r) => r.data),
  }
}

// Pre-built resources for our four models (import and reuse anywhere).
export const customers = resource('customers')
export const products = resource('products')
export const orders = resource('orders')
export const subscriptions = resource('subscriptions')

// Read-only support lookups.
export const support = {
  orderStatus: (orderId) => http.get(`/support/order/${orderId}/status`).then((r) => r.data),
  customerOrders: (customerId) =>
    http.get(`/support/customer/${customerId}/orders`).then((r) => r.data),
  customerSubscription: (customerId) =>
    http.get(`/support/customer/${customerId}/subscription`).then((r) => r.data),
}

// Stripe payments.
export const payments = {
  checkout: (orderId) => http.post(`/payments/checkout/${orderId}`).then((r) => r.data),
  refund: (orderId) => http.post(`/payments/refund/${orderId}`).then((r) => r.data),
}
