<template>
  <section>
    <div class="manage-grid">
      <div class="card">
        <h3>{{ form.id ? '编辑文章' : '新建文章' }}</h3>
        <div class="grid">
          <input class="input" v-model="form.title" placeholder="标题" />
          <input class="input" v-model="form.tagsText" placeholder="标签，逗号分隔" />

          <div class="toolbar">
            <button class="btn secondary" @click="insert('**', '**')">加粗</button>
            <button class="btn secondary" @click="insert('*', '*')">斜体</button>
            <button class="btn secondary" @click="insert('## ', '')">标题</button>
            <button class="btn secondary" @click="insert('[', '](url)')">链接</button>
            <button class="btn secondary" @click="insert('```\n', '\n```')">代码块</button>
          </div>

          <div class="editor-grid">
            <textarea ref="editorRef" class="textarea" v-model="form.content_md" placeholder="Markdown 内容" @input="syncPreview"></textarea>
            <div class="preview md-body" v-html="previewHtml"></div>
          </div>

          <div style="display:flex;gap:10px;">
            <button class="btn" @click="onSubmit">{{ form.id ? '保存' : '创建' }}</button>
            <button class="btn secondary" @click="onReset">清空</button>
          </div>
        </div>
      </div>

      <div>
        <div class="grid cols-2">
          <div v-for="a in items" :key="a.id" class="card">
            <div @click="onEdit(a)">
              <h4>{{ a.title }}</h4>
              <div class="muted">{{ a.summary }}</div>
            </div>
            <div style="margin-top:10px;">
              <button class="btn secondary" @click.stop="onDelete(a)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { marked } from 'marked'
import { articleApi } from '../api'

const form = reactive({ id: 0, title: '', content_md: '', tagsText: '' })
const items = ref([])
const editorRef = ref(null)
const previewHtml = computed(() => marked.parse(form.content_md || ''))

async function fetchList() {
  const { data } = await articleApi.list({ page: 1, size: 50, mine: true })
  items.value = data.items
}

function onEdit(a) {
  form.id = a.id
  form.title = a.title
  form.content_md = a.content_md
  form.tagsText = (a.tags || []).map(t => t.name).join(',')
}

async function onSubmit() {
  const tags = form.tagsText.split(',').map(s => s.trim()).filter(Boolean)
  if (form.id) {
    await articleApi.update(form.id, { title: form.title, content_md: form.content_md, tags })
  } else {
    await articleApi.create({ title: form.title, content_md: form.content_md, tags })
    form.title = ''
    form.content_md = ''
    form.tagsText = ''
  }
  await fetchList()
}

async function onDelete(a) {
  const yes = window.confirm(`确认删除《${a.title}》吗？`)
  if (!yes) return
  await articleApi.remove(a.id)
  await fetchList()
}

function insert(before, after) {
  const el = editorRef.value
  if (!el) return
  const start = el.selectionStart || 0
  const end = el.selectionEnd || 0
  const value = form.content_md || ''
  const selected = value.slice(start, end) || '文本'
  const next = value.slice(0, start) + before + selected + after + value.slice(end)
  form.content_md = next
}

function syncPreview() {
  // computed 自动更新，这里保留用于后续扩展
}

function onReset() {
  form.id = 0
  form.title = ''
  form.content_md = ''
  form.tagsText = ''
}

onMounted(fetchList)
</script>

<style scoped>
.manage-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 900px) { .manage-grid { grid-template-columns: 1fr; } }
</style>
