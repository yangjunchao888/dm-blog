<template>
<router-link class="card article-card" :to="`/articles/${item.id}`">
  <div class="cover"></div>
  <h3>{{ item.title }}</h3>
  <p class="muted">{{ item.summary || '暂无摘要' }}</p>
  <div class="tags">
    <span v-for="t in item.tags" :key="t.id" class="chip">{{ t.name }}</span>
  </div>
  <div class="meta muted">阅读全文 →</div>
</router-link>
</template>

<script setup>
defineProps({ item: { type: Object, required: true } })
</script>

<style scoped>
.article-card { display: block; overflow: hidden; }
.cover {
  height: 6px; margin: -16px -16px 12px -16px;
  background: linear-gradient(90deg, #93c5fd, #60a5fa);
}
.article-card h3 { margin: 0 0 8px; }
.tags { margin-top: 10px; }
.meta { margin-top: 10px; font-size: 12px; }
</style>
