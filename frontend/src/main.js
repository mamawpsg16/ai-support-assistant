// main.js — the JavaScript entry point of the SPA (index.html loads this).
//
// Its job: create the Vue app, attach plugins (router later), and "mount" it onto
// the <div id="app"> in index.html.

import { createApp } from 'vue'

// Import Bootstrap's CSS once here so every component can use Bootstrap classes.
// (We import it from the npm package we installed — no CDN link needed.)
import 'bootstrap/dist/css/bootstrap.min.css'

import App from './App.vue'
import { router } from './router'

// createApp(App) builds the app from our root component; .use(router) installs
// page routing; .mount('#app') puts it into the <div id="app"> in index.html.
createApp(App).use(router).mount('#app')
