<!--
  ProductCard.vue — one product shown as a Bootstrap card with a Buy button.
  Presentational: it displays a product and emits "buy" when clicked. The parent
  (StoreView) decides what buying actually does.
-->
<template>
  <div class="card h-100 shadow-sm">
    <div class="card-body d-flex flex-column">
      <h5 class="card-title">{{ product.name }}</h5>
      <p class="card-text text-muted small flex-grow-1">
        {{ product.description || 'No description' }}
      </p>
      <div class="d-flex justify-content-between align-items-center mt-2">
        <span class="fs-5 fw-bold">{{ formatMoney(product.price) }}</span>
        <button class="btn btn-primary btn-sm" :disabled="disabled" @click="emit('buy', product)">
          Buy
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../utils/format'

defineProps({
  product: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['buy'])
</script>
