<!--
  SubscriptionsView.vue — pick a customer, see their subscription(s).
  Uses: GET /support/customer/{id}/subscription  (returns a list).
  Same pattern as OrdersView: Picker + useAsync + watch.
-->
<template>
  <div>
    <h2 class="mb-3">Subscriptions</h2>

    <div class="mb-4" style="max-width: 360px">
      <Picker
        v-model="customerId"
        :options="customersReq.data.value || []"
        :loading="customersReq.loading.value"
        title="Customer"
        placeholder="Search a customer…"
      />
    </div>

    <p v-if="!customerId" class="text-muted">Pick a customer to see their subscriptions.</p>

    <div v-else-if="subsReq.loading.value" class="text-muted">Loading subscriptions…</div>
    <div v-else-if="subsReq.error.value" class="alert alert-danger">{{ subsReq.error.value }}</div>
    <div v-else-if="(subsReq.data.value || []).length === 0" class="text-muted">
      This customer has no subscriptions.
    </div>

    <div v-else class="row g-3">
      <div class="col-12 col-md-6" v-for="s in subsReq.data.value" :key="s.id">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">{{ s.plan_name }}</h5>
              <StatusBadge :status="s.status" />
            </div>
            <p class="text-muted small mb-0 mt-2">
              Subscription #{{ s.id }} · started {{ formatDate(s.created_at) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { support, customers as customersApi } from '../api'
import { useAsync } from '../composables/useAsync'
import { formatDate } from '../utils/format'
import Picker from '../components/Picker.vue'
import StatusBadge from '../components/StatusBadge.vue'

const customerId = ref(null)

const customersReq = useAsync(() => customersApi.list())
customersReq.run()

const subsReq = useAsync((id) => support.customerSubscription(id))
watch(customerId, (id) => {
  if (id) subsReq.run(id)
})
</script>
