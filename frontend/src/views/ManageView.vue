<!--
  ManageView.vue — admin page to manage customers and products.
  Two Bootstrap tabs, each hosting a manager component. A simple `tab` ref decides
  which one shows (no Bootstrap JS needed — Vue handles the toggle).
-->
<template>
  <div>
    <h2 class="mb-3">Manage</h2>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'customers' }" @click="tab = 'customers'">
          Customers
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'products' }" @click="tab = 'products'">
          Products
        </button>
      </li>
    </ul>

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
