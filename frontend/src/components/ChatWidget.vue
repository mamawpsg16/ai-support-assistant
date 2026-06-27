<!--
  ChatWidget.vue — the floating AI support chat (Phase 4 feature), restyled to the design.

  A round button (FAB) sits bottom-right; clicking it toggles the chat panel. The panel
  shows the conversation, a typing indicator, and an input row.

  Backend is STATELESS, so we keep the message history here ({ role, content }) and send
  the whole array on every request (see api.chat.send). The system prompt is added
  server-side; we only track user/assistant turns.
-->
<template>
  <!-- Hidden while the cart drawer is open, so the FAB doesn't float over the cart's
       Checkout button (the cart sits at a lower z-index than this widget). -->
  <div v-show="!cartState.open">
    <!-- Floating toggle button. -->
    <button class="fab" @click="open = !open" :aria-label="open ? 'Close chat' : 'Open chat'">
      <Icon :name="open ? 'x' : 'chat'" :size="open ? 20 : 19" />
    </button>

    <!-- Chat panel -->
    <Transition name="chat">
      <div v-if="open" class="chat">
        <!-- Header -->
        <header class="chat-head">
          <div class="chat-avatar"><Icon name="chat" :size="16" /></div>
          <div class="chat-id">
            <div class="chat-name">Support</div>
            <div class="chat-tag">RAG · policy assistant</div>
          </div>
          <button class="chat-close" @click="open = false" aria-label="Close chat">
            <Icon name="x" :size="14" />
          </button>
        </header>

        <!-- Messages -->
        <div ref="scroller" class="chat-body">
          <!-- Static greeting when the conversation is empty. -->
          <div v-if="messages.length === 0" class="msg a">
            <div class="bubble a">Hi. Ask me about shipping, returns, payments, or store policies.</div>
          </div>

          <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role === 'user' ? 'u' : 'a'">
            <div class="bubble" :class="m.role === 'user' ? 'u' : 'a'">{{ m.content }}</div>
          </div>

          <!-- Typing dots while waiting for the AI. -->
          <div v-if="loading" class="msg a">
            <div class="typing">
              <span /><span /><span />
            </div>
          </div>
        </div>

        <!-- Error banner (e.g. AI not configured / network). -->
        <div v-if="error" class="chat-err">{{ error }}</div>

        <!-- Input row -->
        <footer class="chat-foot">
          <input
            v-model="draft"
            class="chat-input"
            placeholder="Ask about shipping, returns…"
            :disabled="loading"
            @keydown.enter.prevent="send"
          />
          <button class="chat-send" :disabled="loading || !draft.trim()" @click="send" aria-label="Send">
            <Icon name="send" :size="16" />
          </button>
        </footer>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import Icon from './Icon.vue'
import { chat } from '../api'
import { useCart } from '../composables/useCart'

// Used only to hide the chat FAB/panel while the cart drawer is open.
const { state: cartState } = useCart()

const open = ref(false)
const messages = ref([]) // [{ role: 'user'|'assistant', content }]
const draft = ref('')
const loading = ref(false)
const error = ref(null)

const scroller = ref(null)
async function scrollToBottom() {
  await nextTick()
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
}

async function send() {
  const text = draft.value.trim()
  if (!text || loading.value) return

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
    error.value = e?.response?.data?.detail || e.message || 'Something went wrong'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
/* Floating action button */
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  background: var(--ink);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  z-index: 400;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s;
}
.fab:hover { transform: scale(1.07); }

/* Panel */
.chat {
  position: fixed;
  bottom: 84px;
  right: 24px;
  width: 340px;
  max-width: calc(100vw - 48px);
  height: 440px;
  background: var(--surface);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 18px;
  z-index: 399;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* Header */
.chat-head {
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface-2);
}
.chat-avatar {
  width: 32px;
  height: 32px;
  background: var(--ink);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.chat-id { flex: 1; }
.chat-name { font-size: 13px; font-weight: 600; }
.chat-tag { font-size: 11px; color: var(--sage); font-weight: 500; }
.chat-close {
  width: 28px;
  height: 28px;
  background: #e8e7e2;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--muted);
  transition: all 0.12s;
}
.chat-close:hover { background: #d8d7d2; color: var(--ink); }

/* Body */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.msg { display: flex; }
.msg.u { justify-content: flex-end; }
.msg.a { justify-content: flex-start; }
.bubble {
  padding: 9px 13px;
  max-width: 82%;
  font-size: 13px;
  line-height: 19px;
  word-break: break-word;
  white-space: pre-wrap;
}
.bubble.u { background: var(--ink); color: #fff; border-radius: 14px 14px 4px 14px; }
.bubble.a { background: var(--cream); color: var(--ink); border-radius: 14px 14px 14px 4px; }

/* Typing dots */
.typing {
  background: var(--cream);
  padding: 10px 14px;
  border-radius: 14px 14px 14px 4px;
  display: flex;
  gap: 4px;
  align-items: center;
}
.typing span {
  width: 5px;
  height: 5px;
  background: var(--muted-2);
  border-radius: 50%;
  animation: dot 1.4s ease infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

.chat-err {
  font-size: 12px;
  color: var(--danger);
  padding: 0 14px 8px;
}

/* Footer input */
.chat-foot {
  padding: 10px 12px;
  border-top: 1px solid var(--line);
  display: flex;
  gap: 7px;
  align-items: center;
  background: var(--surface-2);
}
.chat-input {
  flex: 1;
  background: var(--surface);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 9px;
  padding: 9px 11px;
  font-size: 13px;
  color: var(--ink);
  font-family: var(--font-body);
}
.chat-send {
  width: 36px;
  height: 36px;
  background: var(--ink);
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  flex-shrink: 0;
  transition: opacity 0.12s;
}
.chat-send:hover:not(:disabled) { opacity: 0.8; }
.chat-send:disabled { opacity: 0.45; cursor: not-allowed; }

/* Open animation */
.chat-enter-active { animation: slideUp 0.22s cubic-bezier(0.2, 0.8, 0.2, 1); }
.chat-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.chat-leave-to { opacity: 0; transform: translateY(8px); }
</style>
