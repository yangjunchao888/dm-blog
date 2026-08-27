<template>
  <section class="detail-layout">
    <article class="card article-detail">
      <h1>{{ article.title }}</h1>
      <div class="muted">作者 #{{ article.author_id }} · {{ article.updated_at }}</div>
      <div class="tags">
        <span v-for="t in article.tags" :key="t.id" class="chip">{{ t.name }}</span>
      </div>
      <div class="md-body" v-html="html"></div>
    </article>

    <aside class="side card">
      <h4>目录</h4>
      <div v-if="toc.length">
        <div v-for="(h,i) in toc" :key="i">
          <a :href="`#${h.id}`">{{ h.text }}</a>
        </div>
      </div>
      <div v-else class="muted">暂无目录</div>
    </aside>
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { articleApi } from '../api'
import { marked } from 'marked'

const route = useRoute()
const article = ref({ id: 0, title: '', content_md: '', tags: [] })
const html = computed(() => marked.parse(article.value.content_md || ''))
const toc = computed(() => {
  const out = []
  const re = /<h([23])[^>]*>(.*?)<\/h\1>/gi
  let m
  while ((m = re.exec(html.value))) {
    const text = m[2].replace(/<[^>]+>/g, '')
    const id = text.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-').replace(/(^-|-$)/g, '')
    out.push({ level: m[1], text, id })
  }
  return out
})

onMounted(async () => {
  const { data } = await articleApi.get(route.params.id)
  article.value = data
})
</script>

<style scoped>
.detail-layout { display: grid; grid-template-columns: 1fr 280px; gap: 16px; }
@media (max-width: 1000px) { .detail-layout { grid-template-columns: 1fr; } }
.article-detail h1 { margin-top: 8px; }
.tags { margin: 12px 0 16px; }
.md-body { margin-top: 8px; line-height: 1.8; }
</style>
