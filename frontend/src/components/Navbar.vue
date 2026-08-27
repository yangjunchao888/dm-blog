<template>
  <header class="navbar">
    <div class="container navbar-inner">
      <router-link class="brand" to="/">DM 博客</router-link>
      <nav>
        <router-link to="/articles">文章</router-link>
        <router-link to="/manage">管理</router-link>
        <router-link v-if="!auth.token" to="/login">登录</router-link>
        <a v-else href="#" @click.prevent="auth.logout()">退出</a>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.navbar {
  position: sticky; top: 0; z-index: 10;
  background: #ffffff;
  border-bottom: 1px solid var(--border);
}
.navbar-inner { display: flex; align-items: center; justify-content: space-between; }
.brand { font-weight: 700; font-size: 18px; }
nav a { margin-left: 16px; }
</style>
