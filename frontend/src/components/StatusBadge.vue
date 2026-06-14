<!--
  StatusBadge.vue — shows a coloured Bootstrap badge for a status string.
  Reused anywhere a status appears (orders, subscriptions). The colour logic lives in
  utils/format.js; this component just renders it.

  Usage: <StatusBadge :status="order.status" />
-->
<template>
  <span :class="statusBadgeClass(status)">{{ status }}</span>
</template>

<script setup>
import { statusBadgeClass } from '../utils/format'

// defineProps declares the inputs a component accepts (like function arguments).
defineProps({
  status: { type: String, required: true },
})
</script>
