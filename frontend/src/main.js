// main.js — the JavaScript entry point of the SPA (index.html loads this).
//
// Its job: create the Vue app, attach plugins (router later), and "mount" it onto
// the <div id="app"> in index.html.

import { createApp } from 'vue'

// Our design system: palette, fonts, global resets, animations, and the reusable UI
// primitives (.ui-btn/.ui-input/.ui-table/…). This fully replaces Bootstrap, which was
// removed once every view was re-skinned to the design.
import './assets/theme.css'

import App from './App.vue'
import { router } from './router'

// createApp(App) builds the app from our root component; .use(router) installs
// page routing; .mount('#app') puts it into the <div id="app"> in index.html.
createApp(App).use(router).mount('#app')
