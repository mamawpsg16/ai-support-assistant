<!--
  App.vue — the ROOT component: a Bootstrap navbar on top, and <router-view/> below
  where the current page renders.

  <RouterLink> is vue-router's version of <a>: it changes the URL and swaps the page
  WITHOUT a full reload. active-class highlights the link for the current route.
-->
<template>
  <div>
    <nav class="navbar navbar-expand navbar-dark bg-dark">
      <div class="container">
        <RouterLink class="navbar-brand fw-bold" to="/">🛍️ Storefront</RouterLink>
        <ul class="navbar-nav">
          <li class="nav-item" v-for="link in links" :key="link.to">
            <!-- active-class adds Bootstrap's "active" style to the current page link -->
            <RouterLink class="nav-link" active-class="active" :to="link.to">
              {{ link.label }}
            </RouterLink>
          </li>
        </ul>
      </div>
    </nav>

    <!-- The current route's component renders here. -->
    <main class="container py-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
// Nav links defined once as data, then rendered with v-for (DRY — no repeated markup).
const links = [
  { to: '/', label: 'Store' },
  { to: '/orders', label: 'Orders' },
  { to: '/subscriptions', label: 'Subscriptions' },
  { to: '/manage', label: 'Manage' },
]
</script>
