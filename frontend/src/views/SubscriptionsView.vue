<!--
  SubscriptionsView.vue — pick a customer, see their subscription(s), restyled.

  Note: the Claude design's Subscriptions screen is a marketing PRICING TABLE (mock,
  not wired to the backend). The real feature is "show this customer's subscriptions",
  so we keep the real data and give it the design's card look (like we skipped the mock
  checkout modal). Endpoint unchanged: GET /support/customer/{id}/subscription.
-->
<template>
  <div class="ui-view">
    <div class="ui-head">
      <h1 class="ui-h1">Subscriptions</h1>
      <p class="ui-sub">Active plans for the selected customer.</p>
    </div>

    <div class="picker-row">
      <Picker
        v-model="customerId"
        :options="customersReq.data.value || []"
        :loading="customersReq.loading.value"
        title="Customer"
        placeholder="Search a customer…"
      />
    </div>

    <p v-if="!customerId" class="ui-state">Pick a customer to see their subscriptions.</p>
    <div v-else-if="subsReq.loading.value" class="ui-state">Loading subscriptions…</div>
    <div v-else-if="subsReq.error.value" class="ui-alert">{{ subsReq.error.value }}</div>
    <p v-else-if="(subsReq.data.value || []).length === 0" class="ui-state">
      This customer has no subscriptions.
    </p>

    <div v-else class="sub-grid">
      <div v-for="s in subsReq.data.value" :key="s.id" class="sub-card">
        <div class="sub-top">
          <span class="sub-name">{{ s.plan_name }}</span>
          <StatusBadge :status="s.status" />
        </div>
        <p class="sub-meta">Subscription #{{ s.id }} · started {{ formatDateShort(s.created_at) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { support, customers as customersApi } from '../api'
import { useAsync } from '../composables/useAsync'
import { formatDateShort } from '../utils/format'
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

<style scoped>
.picker-row { max-width: 360px; margin-bottom: 24px; }

.sub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  max-width: 860px;
}

.sub-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 22px;
}
.sub-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.sub-name { font-family: var(--font-display); font-size: 22px; font-weight: 500; }
.sub-meta { font-size: 13px; color: var(--muted); margin: 0; }
</style>
