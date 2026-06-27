<!--
  StatusBadge.vue — a coloured status pill (themed to the design).
  Colour + label come from utils/format.js so a status looks identical everywhere.

  Usage: <StatusBadge :status="order.status" />
-->
<template>
  <span class="status-pill" :style="{ background: s.bg, color: s.col }">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { statusStyle, statusLabel } from '../utils/format'

const props = defineProps({
  status: { type: String, required: true },
})

const s = computed(() => statusStyle(props.status))
const label = computed(() => statusLabel(props.status))
</script>

<style scoped>
.status-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
}
</style>
