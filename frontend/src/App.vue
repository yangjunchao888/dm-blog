<template>
  <div class="app-shell">
    <Navbar />
    <main class="container">
      <router-view />
    </main>
    <ChatPanel />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import ChatPanel from './components/ChatPanel.vue'
</script>
