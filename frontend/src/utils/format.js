// format.js — small shared formatting helpers (DRY: defined once, used everywhere).

// Money: 25 -> "$25.00". Intl.NumberFormat handles currency formatting for us.
export function formatMoney(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount ?? 0)
}

// Map an order/subscription status string to a Bootstrap badge colour class, so a
// status always looks consistent across pages.
const STATUS_CLASS = {
  // orders
  pending: 'bg-secondary',
  paid: 'bg-success',
  shipped: 'bg-info text-dark',
  delivered: 'bg-primary',
  refunded: 'bg-warning text-dark',
  // subscriptions
  active: 'bg-success',
  canceled: 'bg-secondary',
  past_due: 'bg-danger',
}

export function statusBadgeClass(status) {
  return `badge ${STATUS_CLASS[status] || 'bg-secondary'}`
}

// Format an ISO date string -> readable local date/time. Returns '' if missing.
export function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}
