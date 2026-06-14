// useCrud.js — reusable CRUD logic for ANY resource.
//
// The manager pages (customers, products) all do the same operations; only the API and
// the form fields differ. This composable holds the operations ONCE; each component
// supplies its own fields + validation.
//
// CRUD map (what each returned thing does):
//   READ list -> fetchAll(params) : GET the list (optional query params); -> `items`
//   READ one  -> getOne(id)        : GET a single record by id (returns it)
//   items     -> the fetched list (reactive); read this in the template
//   CREATE    -> save(form)        : POST   when form.id is empty
//   UPDATE    -> save(form)        : PATCH  when form.id is set
//   DELETE    -> remove(id)        : DELETE
//   loading/error -> state of the list fetch
//
// fetchAll forwards its arguments to api.list, so you can filter/paginate:
//   fetchAll({ skip: 0, limit: 20 })
//
// It does NOT care about field names/types — save(form) forwards the WHOLE form object
// to the API, so a customer form {name,email} and a product form {name,price} both work.
//
// Usage:
//   const { items, loading, error, fetchAll, getOne, save, remove } = useCrud(customersApi)
//   onMounted(fetchAll)                 // load all
//   onMounted(() => fetchAll({ limit: 10 }))   // load with params

import { useAsync } from './useAsync'

export function useCrud(api) {
  // READ/list: fetchAll(params?) triggers GET /<resource>/; result lands in `items`.
  // useAsync's run forwards args, so params flow through to api.list(params).
  const { data: items, loading, error, run: fetchAll } = useAsync((params) => api.list(params))

  // READ one: get a single record by id (with optional query params).
  // Returns the record so the caller can use it (e.g. prefill an edit form).
  function getOne(id, params) {
    return api.get(id, params)
  }

  // CREATE (no id) or UPDATE (has id), then refresh the list.
  async function save(form) {
    if (form.id) {
      await api.update(form.id, form)
    } else {
      await api.create(form)
    }
    await fetchAll()
  }

  // DELETE by id, then refresh the list.
  async function remove(id) {
    await api.remove(id)
    await fetchAll()
  }

  return { items, loading, error, fetchAll, getOne, save, remove }
}
