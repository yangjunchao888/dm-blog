<template>
  <section>
    <div class="hero card">
      <h1>欢迎来到 DM 博客</h1>
      <p class="muted">二次元风格 + AI 陪你写博客</p>
      <div style="margin-top:16px;">
        <router-link class="btn" to="/articles">浏览文章</router-link>
        <button class="btn secondary" style="margin-left:10px;" @click="goManage">开始创作</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero { padding: 32px; }
</style>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function goManage() {
  if (!auth.token) {
    router.push('/login')
    return
  }
  router.push('/manage')
}
</script>
