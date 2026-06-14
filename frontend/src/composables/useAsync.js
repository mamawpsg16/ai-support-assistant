// useAsync.js — a reusable "composable" for running an async call with state.
//
// A composable is just a function that uses Vue's reactivity (ref) and returns
// reactive values + functions. It's how the Composition API shares logic between
// components without repeating it (the Vue equivalent of a custom hook).
//
// PROBLEM it solves (DRY): almost every page does the same dance —
//   set loading = true, call the API, store the result, catch errors, set loading = false.
// Instead of rewriting that everywhere, we write it ONCE here.
//
// Usage in a component:
//   const { data, loading, error, run } = useAsync(() => products.list())
//   onMounted(run)            // load on mount
//   // template: v-if="loading" / v-else-if="error" / v-else use data

import { ref } from 'vue'

export function useAsync(asyncFn) {
  const data = ref(null)     // the result of the call
  const loading = ref(false) // true while the call is in flight
  const error = ref(null)    // an error message if it failed

  // run(...args) executes the async function and updates the state.
  async function run(...args) {
    loading.value = true
    error.value = null
    try {
      data.value = await asyncFn(...args)
      return data.value
    } catch (e) {
      // FastAPI puts a human message in response.data.detail; fall back to e.message.
      error.value = e?.response?.data?.detail || e.message || 'Something went wrong'
      throw e
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, run }
}
