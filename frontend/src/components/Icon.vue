<!--
  Icon.vue — one small reusable inline-SVG icon, ported from the design's icon set.

  The design drew icons as inline SVG (lucide-style: 24x24 viewBox, rounded strokes,
  no fill). We keep that exact look here so every icon matches. Instead of shipping an
  icon library, we store just the handful of icons the design actually uses.

  How it works:
    - ICONS maps a name -> the inner SVG markup (the <path>/<line>/<circle> shapes).
    - The <svg> wrapper holds the shared attributes (size, stroke, rounded caps).
    - v-html injects the chosen shapes inside that <svg>. Because the parent element
      is a real <svg>, the browser creates the children in the SVG namespace correctly.

  The markup is fixed, author-controlled data (not user input), so v-html is safe here.

  Usage:  <Icon name="cart" :size="18" />
          <Icon name="check" :size="28" stroke="#4A7A58" />
-->
<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="stroke"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    style="display: block; flex-shrink: 0"
    v-html="inner"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 20 },
  stroke: { type: String, default: 'currentColor' }, // inherits text colour by default
})

// Inner SVG shapes per icon name. Copied verbatim from the design's icon map so the
// strokes line up pixel-for-pixel.
const ICONS = {
  cart:  '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
  x:     '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  plus:  '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  minus: '<line x1="5" y1="12" x2="19" y2="12"/>',
  send:  '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  chat:  '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  bag:   '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
  pkg:   '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
  credit:'<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
}

const inner = computed(() => ICONS[props.name] || '')
</script>
