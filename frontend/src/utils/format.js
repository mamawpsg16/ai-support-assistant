// format.js — small shared formatting helpers (DRY: defined once, used everywhere).

// Money: 25 -> "$25.00". Intl.NumberFormat handles currency formatting for us.
export function formatMoney(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount ?? 0)
}

// Design-themed status pill colours: status -> { bg, col }. Used by StatusBadge.vue.
// Covers both order and subscription statuses.
const STATUS_STYLE = {
  // orders
  pending: { bg: '#EDF2F7', col: '#3D6A8A' },
  paid: { bg: '#EEF5F1', col: '#4A7A58' },
  shipped: { bg: '#FDF4E8', col: '#C07830' },
  delivered: { bg: '#EEF5F1', col: '#4A7A58' },
  refunded: { bg: '#F4F3EF', col: '#7A7870' },
  // subscriptions
  active: { bg: '#EEF5F1', col: '#4A7A58' },
  canceled: { bg: '#F4F3EF', col: '#7A7870' },
  past_due: { bg: '#FDF2F0', col: '#C9695A' },
}

export function statusStyle(status) {
  return STATUS_STYLE[status] || { bg: '#F4F3EF', col: '#7A7870' }
}

// "past_due" -> "Past due" (underscores to spaces, first letter capitalised).
export function statusLabel(status) {
  return (status || '').replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())
}

// Format an ISO date string -> readable local date/time. Returns '' if missing.
export function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

// Shorter date only, e.g. "Jun 15, 2026" (matches the design's order rows).
export function formatDateShort(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
