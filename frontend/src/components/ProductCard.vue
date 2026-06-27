<!--
  ProductCard.vue — one product card, restyled to the design.

  Presentational: it shows a product (coloured initials tile, name, category, price)
  and emits "add" when the user clicks "Add to cart". The parent (StoreView) decides
  what adding does. The tile colour + initials + category come from utils/catalog.js,
  since the backend product has no art or category field.
-->
<template>
  <div class="pcard">
    <!-- Initials tile (stands in for a product photo) -->
    <div class="pcard-tile" :style="{ background: tile.bg }">
      <span class="pcard-ab" :style="{ color: tile.col }">{{ tile.ab }}</span>
    </div>

    <!-- Info -->
    <div class="pcard-info">
      <div class="pcard-name">{{ product.name }}</div>
      <div class="pcard-cat">{{ category }}</div>
      <div class="pcard-price">{{ formatMoney(product.price) }}</div>
      <button class="pcard-add" :disabled="disabled" @click="emit('add', product)">
        Add to cart
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatMoney } from '../utils/format'
import { tileFor, categoryFor } from '../utils/catalog'

const props = defineProps({
  product: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['add'])

const tile = computed(() => tileFor(props.product))
const category = computed(() => categoryFor(props.product))
</script>

<style scoped>
.pcard {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.pcard:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1); }

.pcard-tile {
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.pcard-ab {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 500;
  letter-spacing: -1px;
  opacity: 0.75;
  user-select: none;
}

.pcard-info { padding: 10px 10px 12px; }
.pcard-name {
  font-size: 13px;
  line-height: 17px;
  margin-bottom: 4px;
  min-height: 34px;
  /* Clamp to 2 lines so cards stay the same height. */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.pcard-cat {
  font-size: 11px;
  color: var(--muted-2);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.pcard-price {
  font-size: 17px;
  font-weight: 700;
  color: var(--orange);
  margin-bottom: 10px;
  font-variant-numeric: tabular-nums;
}
.pcard-add {
  width: 100%;
  background: var(--orange);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 0;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: background 0.12s;
}
.pcard-add:hover { background: var(--orange-dark); }
.pcard-add:disabled { opacity: 0.6; cursor: default; }
</style>
