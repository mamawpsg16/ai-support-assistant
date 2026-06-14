<!--
  CustomerManager.vue — CRUD for customers. The data logic comes from useCrud; this
  component only owns the FORM (fields + Vuelidate rules) and the table markup.

  useCrud gives: items (the list), fetchAll, save, remove.
  Vuelidate gives: v$ — validation state for the form.
-->
<template>
  <div>
    <!-- Create / edit form (one form does both; form.id decides which) -->
    <form class="row g-2 align-items-start mb-4" @submit.prevent="submit">
      <div class="col-12 col-md-4">
        <input
          v-model="form.name"
          class="form-control"
          :class="{ 'is-invalid': v$.name.$error }"
          placeholder="Name"
        />
        <div class="invalid-feedback" v-if="v$.name.$error">{{ v$.name.$errors[0].$message }}</div>
      </div>
      <div class="col-12 col-md-4">
        <input
          v-model="form.email"
          class="form-control"
          :class="{ 'is-invalid': v$.email.$error }"
          placeholder="Email"
        />
        <div class="invalid-feedback" v-if="v$.email.$error">{{ v$.email.$errors[0].$message }}</div>
      </div>
      <div class="col-12 col-md-4 d-flex gap-2">
        <button class="btn btn-primary" :disabled="saving">
          {{ form.id ? 'Update' : 'Add' }} customer
        </button>
        <button v-if="form.id" type="button" class="btn btn-outline-secondary" @click="resetForm">
          Cancel
        </button>
      </div>
    </form>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <!-- List -->
    <div v-if="loading" class="text-muted">Loading customers…</div>
    <table v-else class="table align-middle">
      <thead>
        <tr><th>#</th><th>Name</th><th>Email</th><th class="text-end">Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="c in items || []" :key="c.id">
          <td>{{ c.id }}</td>
          <td>{{ c.name }}</td>
          <td>{{ c.email }}</td>
          <td class="text-end">
            <button class="btn btn-outline-primary btn-sm me-2" @click="edit(c)">Edit</button>
            <button class="btn btn-outline-danger btn-sm" @click="onDelete(c)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, email } from '@vuelidate/validators'
import { customers as customersApi } from '../api'
import { useCrud } from '../composables/useCrud'

// Data layer (DRY) — list + save + remove for customers.
const { items, loading, fetchAll, save, remove } = useCrud(customersApi)
onMounted(fetchAll)

// Form (this component's own concern) — fields + validation rules.
const form = reactive({ id: null, name: '', email: '' })
const rules = {
  name: { required },
  email: { required, email },
}
const v$ = useVuelidate(rules, form)

const saving = ref(false)
const errorMsg = ref('')

async function submit() {
  if (!(await v$.value.$validate())) return // invalid -> errors show, stop
  saving.value = true
  errorMsg.value = ''
  try {
    // send a plain copy of the form (id included so useCrud knows create vs update)
    await save({ ...form })
    resetForm()
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e.message || 'Save failed'
  } finally {
    saving.value = false
  }
}

function edit(c) {
  form.id = c.id
  form.name = c.name
  form.email = c.email
  v$.value.$reset()
}

function resetForm() {
  form.id = null
  form.name = ''
  form.email = ''
  v$.value.$reset()
}

async function onDelete(c) {
  if (!window.confirm(`Delete ${c.name}?`)) return
  errorMsg.value = ''
  try {
    await remove(c.id)
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e.message || 'Delete failed'
  }
}
</script>
