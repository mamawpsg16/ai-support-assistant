<!--
  Picker.vue — a GENERIC searchable dropdown (vue-multiselect), reusable for ANY data.

  It knows nothing about customers/products specifically — the parent passes in the
  options and tells it which fields to use. DRY: one picker for everything.

  Props (all configurable — nothing hardcoded):
    options      : the array of objects to choose from               (required)
    modelValue   : selected id (single) or array of ids (multiple)
    multiple     : single vs multi select                            (default false)
    labelField   : which object field to DISPLAY                     (default "name")
    trackBy      : which object field is the unique id               (default "id")
    title        : the form label text above the box                 (default "Select")
    placeholder  : the box's placeholder text                        (default "Search…")
    loading      : show the spinner (parent controls while fetching) (default false)

  Usage:
    <Picker v-model="customerId" :options="customers" title="Customer" />
    <Picker v-model="productIds" :options="products" multiple title="Products" />
-->
<template>
  <div>
    <!-- Plain div (not <label>): vue-multiselect is a custom widget, not a native
         input, so its accessible name comes from :aria-label below instead. -->
    <div class="picker-title">{{ title }}</div>
    <VueMultiselect
      :model-value="selected"
      :options="options"
      :loading="loading"
      :multiple="multiple"
      :close-on-select="!multiple"
      :label="labelField"
      :track-by="trackBy"
      :placeholder="placeholder"
      :aria-label="title"
      @update:model-value="onChange"
    >
      <!-- Show "<label> (#id)" for each row. -->
      <template #singleLabel="{ option }">
        {{ option[labelField] }} (#{{ option[trackBy] }})
      </template>
      <template #option="{ option }">
        {{ option[labelField] }} (#{{ option[trackBy] }})
      </template>
    </VueMultiselect>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VueMultiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.css'

const props = defineProps({
  options: { type: Array, default: () => [] },
  modelValue: { type: [Number, String, Array], default: null },
  multiple: { type: Boolean, default: false },
  labelField: { type: String, default: 'name' },
  trackBy: { type: String, default: 'id' },
  title: { type: String, default: 'Select' },
  placeholder: { type: String, default: 'Search…' },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

// Find an option object by its tracked id.
function byId(id) {
  return props.options.find((o) => o[props.trackBy] === Number(id)) || null
}

// ids (parent) -> object(s) (widget)
const selected = computed(() => {
  if (props.multiple) {
    return (props.modelValue || []).map(byId).filter(Boolean)
  }
  return byId(props.modelValue)
})

// object(s) (widget) -> ids (parent)
function onChange(value) {
  if (props.multiple) {
    emit('update:modelValue', (value || []).map((o) => o[props.trackBy]))
  } else {
    emit('update:modelValue', value ? value[props.trackBy] : null)
  }
}
</script>

<style scoped>
.picker-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 6px;
}
</style>
