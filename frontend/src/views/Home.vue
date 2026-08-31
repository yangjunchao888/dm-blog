<template>
  <section>
    <div class="hero card">
      <h1>DM Blog</h1>
      <p class="subtitle">一个简洁的技术博客平台</p>
      <div class="hero-actions">
        <router-link class="btn" to="/articles">浏览文章</router-link>
        <router-link class="btn secondary" to="/manage/new">开始创作</router-link>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero { padding: 48px 32px; text-align: center; }
.hero h1 { font-size: 28px; margin: 0 0 8px; }
.subtitle { color: var(--muted); font-size: 15px; }
.hero-actions { margin-top: 24px; display: flex; gap: 12px; justify-content: center; }
</style>

<script setup>

</script>
