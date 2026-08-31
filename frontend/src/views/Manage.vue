<template>
  <section>
    <div class="manage-header">
      <h2>我的文章</h2>
      <router-link class="btn" to="/manage/new">✏️ 新建文章</router-link>
    </div>

    <div class="article-list">
      <div v-for="a in items" :key="a.id" class="card article-row">
        <div class="article-info" @click="onEdit(a)">
          <h4>{{ a.title }}</h4>
          <div class="muted">{{ a.summary || '暂无摘要' }}</div>
          <div class="tags">
            <span v-for="t in a.tags" :key="t.id" class="chip">{{ t.name }}</span>
          </div>
        </div>
        <div class="article-actions">
          <button class="btn secondary" @click="onEdit(a)">编辑</button>
          <button class="btn secondary" @click.stop="onDelete(a)">删除</button>
        </div>
      </div>
      <div v-if="!items.length" class="card empty-state">
        <p class="muted">暂无文章，点击上方按钮创建。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../api'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const toast = useToastStore()
const items = ref([])

async function fetchList() {
  const { data } = await articleApi.list({ page: 1, size: 50, mine: true })
  items.value = data.items
}

function onEdit(a) {
  router.push(`/manage/edit/${a.id}`)
}

async function onDelete(a) {
  const yes = window.confirm(`确认删除《${a.title}》吗？`)
  if (!yes) return
  await articleApi.remove(a.id)
  toast.success('删除成功')
  await fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.manage-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.manage-header h2 { margin: 0; }
.article-list { display: flex; flex-direction: column; gap: 12px; }
.article-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
}
.article-info { flex: 1; cursor: pointer; }
.article-info h4 { margin: 0 0 4px; }
.tags { margin-top: 6px; }
.article-actions { display: flex; gap: 8px; flex-shrink: 0; }
.empty-state { text-align: center; padding: 40px; }
</style>
