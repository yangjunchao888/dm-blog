<template>
  <section class="list-layout">
    <div class="main">
      <div class="toolbar">
        <input class="input" v-model="keyword" placeholder="搜索文章..." @keyup.enter="fetchList" />
        <input class="input" v-model="tag" placeholder="标签筛选" style="max-width:220px;" @keyup.enter="fetchList" />
        <button class="btn" @click="fetchList">搜索</button>
      </div>

      <div class="cards" style="margin-top:16px;">
        <ArticleCard v-for="a in items" :key="a.id" :item="a" />
      </div>

      <div class="pager" v-if="total > size">
        <button class="btn secondary" :disabled="page<=1" @click="page--; fetchList()">上一页</button>
        <span class="muted">{{ page }} / {{ Math.ceil(total/size) }}</span>
        <button class="btn secondary" :disabled="page>=Math.ceil(total/size)" @click="page++; fetchList()">下一页</button>
      </div>
    </div>

    <aside class="side">
      <div class="card">
        <h4>最新推荐</h4>
        <div v-if="recommended.length" class="recommend-list">
          <router-link v-for="r in recommended" :key="r.id" :to="`/articles/${r.id}`" class="recommend-item">{{ r.title }}</router-link>
        </div>
        <div v-else class="muted">暂无推荐</div>
      </div>
      <div class="card" style="margin-top:16px;">
        <h4>标签</h4>
        <div class="tags">
          <span v-for="t in tags" :key="t.id" class="chip" @click="onTagClick(t.name)">{{ t.name }}</span>
        </div>
        <div style="margin-top:8px;">
          <button v-if="tag" class="btn secondary" @click="onClearTag">清除标签筛选</button>
        </div>
      </div>
    </aside>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { articleApi, tagApi } from '../api'
import ArticleCard from '../components/ArticleCard.vue'

const keyword = ref('')
const tag = ref('')
const items = ref([])
const recommended = ref([])
const tags = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

async function fetchList() {
  const { data } = await articleApi.list({ keyword: keyword.value || undefined, tag: tag.value || undefined, page: page.value, size: size.value })
  items.value = data.items
  total.value = data.total
}

onMounted(async () => {
  await fetchList()
  const [tagRes, recRes] = await Promise.all([tagApi.list(), articleApi.list({ page: 1, size: 5 })])
  tags.value = tagRes.data
  recommended.value = recRes.data.items
})

function onTagClick(name) {
  tag.value = name
  page.value = 1
  fetchList()
}

function onClearTag() {
  tag.value = ''
  page.value = 1
  fetchList()
}
</script>

<style scoped>
.list-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
@media (max-width: 1000px) { .list-layout { grid-template-columns: 1fr; } }
.toolbar { display: flex; gap: 10px; }
.cards { display: grid; gap: 16px; }
.pager { display: flex; gap: 12px; align-items: center; margin-top: 16px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { cursor: pointer; }
.recommend-list { display: flex; flex-direction: column; gap: 8px; }
.recommend-item { color: var(--brand); }
.recommend-item:hover { color: var(--brand-2); }
</style>
