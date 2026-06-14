<!--
  ChatWidget.vue — the floating AI support chat (Phase 4).

  A round button sits bottom-right; clicking it toggles a chat panel. The panel shows the
  conversation, an input box, and a send button.

  State lives here in the component:
    - messages: the conversation ({ role, content }). The backend is STATELESS, so we keep
      the history here and send the whole array on every request (see api.chat.send).
    - The system message is added server-side; we only track user/assistant turns.

  Template-first block order (template, then script) per the project's frontend convention.
-->
<template>
  <div>
    <!-- Floating toggle button (always visible, bottom-right). -->
    <button
      class="btn btn-primary rounded-circle shadow position-fixed bottom-0 end-0 m-4"
      style="width: 56px; height: 56px; z-index: 1050"
      @click="open = !open"
      :aria-label="open ? 'Close chat' : 'Open chat'"
    >
      {{ open ? '✕' : '💬' }}
    </button>

    <!-- Chat panel (only rendered when open). -->
    <div
      v-if="open"
      class="card shadow position-fixed end-0 m-4"
      style="bottom: 88px; width: 340px; max-width: calc(100vw - 2rem); z-index: 1050"
    >
      <div class="card-header bg-primary text-white fw-bold">Support Assistant</div>

      <!-- Message list. ref="scroller" so we can auto-scroll to the newest message. -->
      <div ref="scroller" class="card-body overflow-auto" style="height: 320px">
        <p v-if="messages.length === 0" class="text-muted small">
          Ask me about orders, shipping, returns, or your subscription.
        </p>

        <!-- One bubble per message; align user right, assistant left. -->
        <div
          v-for="(m, i) in messages"
          :key="i"
          class="d-flex mb-2"
          :class="m.role === 'user' ? 'justify-content-end' : 'justify-content-start'"
        >
          <span
            class="px-3 py-2 rounded"
            :class="m.role === 'user' ? 'bg-primary text-white' : 'bg-light border'"
            style="max-width: 85%; white-space: pre-wrap"
            >{{ m.content }}</span
          >
        </div>

        <!-- Typing indicator while waiting for the AI. -->
        <div v-if="loading" class="text-muted small">Assistant is typing…</div>
      </div>

      <!-- Error banner (e.g. AI not configured / network). -->
      <div v-if="error" class="alert alert-danger small m-2 mb-0 py-2">{{ error }}</div>

      <!-- Input row. Enter or the button sends. -->
      <div class="card-footer p-2">
        <form class="d-flex gap-2" @submit.prevent="send">
          <input
            v-model="draft"
            class="form-control form-control-sm"
            placeholder="Type a message…"
            :disabled="loading"
          />
          <button class="btn btn-primary btn-sm" :disabled="loading || !draft.trim()">
            Send
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

import { chat } from '../api'

const open = ref(false)        // panel visible?
const messages = ref([])       // conversation: [{ role: 'user'|'assistant', content }]
const draft = ref('')          // the text box
const loading = ref(false)     // waiting on the AI?
const error = ref(null)

// Scroll the message list to the bottom after the DOM updates (new message added).
const scroller = ref(null)
async function scrollToBottom() {
  await nextTick()
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
}

async function send() {
  const text = draft.value.trim()
  if (!text || loading.value) return

  // Show the user's message immediately, clear the box.
  messages.value.push({ role: 'user', content: text })
  draft.value = ''
  error.value = null
  loading.value = true
  await scrollToBottom()

  try {
    // Send the FULL history so the AI has context (stateless backend).
    const { reply } = await chat.send(messages.value)
    messages.value.push({ role: 'assistant', content: reply })
  } catch (e) {
    // FastAPI puts a message in response.data.detail; fall back to e.message.
    error.value = e?.response?.data?.detail || e.message || 'Something went wrong'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>
