# Frontend — Vue 3 Storefront

A single-page storefront for the AI Customer Support Assistant. **Vue 3 + Vite +
Bootstrap 5**, talking to the FastAPI backend (`../backend`) over HTTP.

## Setup & run

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```
The backend must also be running (`uvicorn backend.main:app --reload` on :8000), and
for orders to flip to paid/refunded, `stripe listen` too. See `../backend/README.md`.

## Configuration

`.env` (already created):
```
VITE_API_BASE=http://127.0.0.1:8000     # the backend base URL (Vite exposes VITE_* vars)
```

## Tech & conventions

- **Vue 3 Composition API** with `<script setup>`, **template-first** block order.
- **Bootstrap 5** for styling, **vue-multiselect** for searchable dropdowns,
  **Vuelidate** for form validation, **axios** for HTTP, **vue-router** for pages.
- **DRY**: shared composables + a generic API client (see structure).

## Structure (layered)

```
src/
  api/                # API client, in its own folder
    http.js           # configured axios instance (baseURL from VITE_API_BASE)
    index.js          # resource() CRUD factory + support + payments helpers
  composables/        # reusable logic
    useAsync.js       # { data, loading, error, run } for any async call
    useCrud.js        # list + create/update/delete for any resource
  utils/
    format.js         # formatMoney, statusBadgeClass, formatDate
  components/         # reusable UI
    Picker.vue            # generic searchable dropdown (single/multi)
    StatusBadge.vue       # coloured status badge
    ProductCard.vue       # product card with Buy
    CustomerManager.vue   # CRUD customers (Vuelidate)
    ProductManager.vue    # CRUD products (Vuelidate)
  views/             # pages (one per route)
    StoreView.vue         # products + Buy -> Stripe checkout
    OrdersView.vue        # a customer's orders + Refund
    SubscriptionsView.vue # a customer's subscriptions
    ManageView.vue        # tabs: customers + products CRUD
    CheckoutSuccess.vue / CheckoutCancel.vue   # Stripe redirect targets
  router/index.js    # routes
  App.vue            # navbar + <router-view/>
  main.js            # createApp + router + Bootstrap CSS
```

## Pages

- **Store** (`/`) — pick a customer, Buy a product → Stripe checkout → success page.
- **Orders** (`/orders`) — pick a customer → their orders + statuses → Refund paid ones.
- **Subscriptions** (`/subscriptions`) — pick a customer → their plans.
- **Manage** (`/manage`) — create / edit / delete customers and products (validated).

## Checkout test card

`4242 4242 4242 4242`, any future expiry (`12/34`), any CVC (`123`). If a green "link"
popup appears, that's Stripe's saved-card login — use a throwaway email to skip it.

## Build for production

```bash
npm run build        # outputs static files to dist/
npm run preview      # preview the production build locally
```
