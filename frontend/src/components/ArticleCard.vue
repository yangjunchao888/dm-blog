<template>
<router-link class="card article-card" :to="`/articles/${item.id}`">
  <h3>{{ item.title }}</h3>
  <p class="muted">{{ item.summary || '暂无摘要' }}</p>
  <div class="tags">
    <span v-for="t in item.tags" :key="t.id" class="chip">{{ t.name }}</span>
  </div>
  <div class="meta muted">阅读全文</div>
</router-link>
</template>

<script setup>
defineProps({ item: { type: Object, required: true } })
</script>

<style scoped>
.article-card { display: block; }
.article-card h3 { margin: 0 0 8px; font-size: 16px; color: var(--text); }
.article-card:hover h3 { color: var(--brand); }
.tags { margin-top: 8px; }
.meta { margin-top: 10px; font-size: 13px; }
</style>
