<!--
  ManageView.vue — admin page to manage customers and products, restyled.

  (The design's "Manage" is a mock account/profile screen. The real app's Manage is the
  CRUD admin we already have, so we keep that and give it the design's look: a heading
  plus themed tab pills switching between the two manager components.)
-->
<template>
  <div class="ui-view">
    <div class="ui-head">
      <h1 class="ui-h1">Manage</h1>
      <p class="ui-sub">Customers &amp; products.</p>
    </div>

    <div class="tabs">
      <button class="tab" :class="{ 'tab-active': tab === 'customers' }" @click="tab = 'customers'">
        Customers
      </button>
      <button class="tab" :class="{ 'tab-active': tab === 'products' }" @click="tab = 'products'">
        Products
      </button>
    </div>

    <CustomerManager v-if="tab === 'customers'" />
    <ProductManager v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CustomerManager from '../components/CustomerManager.vue'
import ProductManager from '../components/ProductManager.vue'

const tab = ref('customers')
</script>

<style scoped>
.tabs { display: flex; gap: 2px; margin-bottom: 24px; }
.tab {
  border: none;
  background: transparent;
  border-radius: 7px;
  padding: 7px 16px;
  font-size: 14px;
  font-family: var(--font-body);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.12s;
}
.tab:hover { color: var(--ink); }
.tab-active { background: var(--ink); color: #fff; font-weight: 600; }
</style>
