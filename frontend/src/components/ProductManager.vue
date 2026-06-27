<!--
  ProductManager.vue — CRUD for products. Same shape as CustomerManager, but DIFFERENT
  fields (name, description, price) and DIFFERENT validation (price must be a number ≥ 0).
  This shows useCrud's flexibility: same data layer, different form.
-->
<template>
  <div>
    <form class="mgr-form" @submit.prevent="submit">
      <div class="ui-field">
        <input
          v-model="form.name"
          class="ui-input"
          :class="{ invalid: v$.name.$error }"
          placeholder="Name"
        />
        <div class="ui-error" v-if="v$.name.$error">{{ v$.name.$errors[0].$message }}</div>
      </div>
      <div class="ui-field">
        <input v-model="form.description" class="ui-input" placeholder="Description (optional)" />
      </div>
      <div class="ui-field">
        <input
          v-model.number="form.price"
          type="number"
          step="0.01"
          class="ui-input"
          :class="{ invalid: v$.price.$error }"
          placeholder="Price"
        />
        <div class="ui-error" v-if="v$.price.$error">{{ v$.price.$errors[0].$message }}</div>
      </div>
      <div class="mgr-actions">
        <button class="ui-btn ui-btn-primary" :disabled="saving">
          {{ form.id ? 'Update' : 'Add' }}
        </button>
        <button v-if="form.id" type="button" class="ui-btn ui-btn-ghost" @click="resetForm">
          Cancel
        </button>
      </div>
    </form>

    <div v-if="errorMsg" class="ui-alert">{{ errorMsg }}</div>

    <div v-if="loading" class="ui-state">Loading products…</div>
    <table v-else class="ui-table">
      <thead>
        <tr><th>#</th><th>Name</th><th>Description</th><th>Price</th><th class="ui-right">Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="p in items || []" :key="p.id">
          <td>{{ p.id }}</td>
          <td>{{ p.name }}</td>
          <td class="mgr-desc">{{ p.description }}</td>
          <td>{{ formatMoney(p.price) }}</td>
          <td class="ui-right mgr-row-actions">
            <button class="ui-btn ui-btn-ghost ui-btn-sm" @click="edit(p)">Edit</button>
            <button class="ui-btn ui-btn-danger ui-btn-sm" @click="onDelete(p)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, numeric, minValue } from '@vuelidate/validators'
import { products as productsApi } from '../api'
import { useCrud } from '../composables/useCrud'
import { formatMoney } from '../utils/format'

// Same data layer as CustomerManager — just a different API.
const { items, loading, fetchAll, save, remove } = useCrud(productsApi)
onMounted(fetchAll)

// Different fields + different rules (price is a number ≥ 0).
const form = reactive({ id: null, name: '', description: '', price: 0 })
const rules = {
  name: { required },
  price: { required, numeric, minValue: minValue(0) },
}
const v$ = useVuelidate(rules, form)

const saving = ref(false)
const errorMsg = ref('')

async function submit() {
  if (!(await v$.value.$validate())) return
  saving.value = true
  errorMsg.value = ''
  try {
    await save({ ...form })
    resetForm()
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e.message || 'Save failed'
  } finally {
    saving.value = false
  }
}

function edit(p) {
  form.id = p.id
  form.name = p.name
  form.description = p.description || ''
  form.price = p.price
  v$.value.$reset()
}

function resetForm() {
  form.id = null
  form.name = ''
  form.description = ''
  form.price = 0
  v$.value.$reset()
}

async function onDelete(p) {
  if (!window.confirm(`Delete ${p.name}?`)) return
  errorMsg.value = ''
  try {
    await remove(p.id)
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e.message || 'Delete failed'
  }
}
</script>

<style scoped>
.mgr-form {
  display: grid;
  grid-template-columns: 1.2fr 1.6fr 0.8fr auto;
  gap: 12px;
  align-items: start;
  margin-bottom: 24px;
}
.mgr-actions { display: flex; gap: 8px; }
.mgr-row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.mgr-desc { color: var(--muted); }
@media (max-width: 720px) { .mgr-form { grid-template-columns: 1fr; } }
</style>
