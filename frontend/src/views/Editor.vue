<template>
  <section class="editor-page">
    <div class="editor-header">
      <h2>{{ form.id ? '编辑文章' : '新建文章' }}</h2>
      <div class="editor-actions">
        <button class="btn secondary" @click="onBack">返回列表</button>
        <button class="btn" @click="onSubmit">{{ form.id ? '保存' : '创建' }}</button>
      </div>
    </div>

    <div class="editor-body">
      <div class="editor-meta">
        <input class="input" v-model="form.title" placeholder="文章标题" />
        <input class="input" v-model="form.tagsText" placeholder="标签，逗号分隔" />
      </div>

      <div class="summary-row">
        <input class="input" v-model="form.summary" placeholder="文章摘要（可选，保存时为空会自动生成）" />
        <button class="btn secondary" @click="onGenSummary" :disabled="summaryLoading">{{ summaryLoading ? '生成中...' : 'AI 生成摘要' }}</button>
      </div>

      <div class="toolbar">
        <button class="btn secondary" @click="insert('**', '**')">加粗</button>
        <button class="btn secondary" @click="insert('*', '*')">斜体</button>
        <button class="btn secondary" @click="insert('## ', '')">标题</button>
        <button class="btn secondary" @click="insert('[', '](url)')">链接</button>
        <button class="btn secondary" @click="insert('```\n', '\n```')">代码块</button>
        <button class="btn secondary" @click="insert('- ', '')">列表</button>
      </div>

      <div class="editor-split">
        <textarea ref="editorRef" class="textarea editor-input" v-model="form.content_md" placeholder="Markdown 内容"></textarea>
        <div class="preview md-body" v-html="previewHtml"></div>
      </div>
      <div class="ai-panel">
        <div class="ai-header" @click="aiOpen = !aiOpen">
          <span>AI 帮写</span>
          <span class="ai-toggle">{{ aiOpen ? '收起' : '展开' }}</span>
        </div>
        <div v-if="aiOpen" class="ai-body">
          <div class="ai-actions">
            <button class="btn secondary" :class="{active: aiAction==='generate'}" @click="aiAction='generate'">生成文章</button>
            <button class="btn secondary" :class="{active: aiAction==='polish'}" @click="aiAction='polish'">润色改写</button>
            <button class="btn secondary" :class="{active: aiAction==='summary'}" @click="aiAction='summary'">生成摘要</button>
          </div>
          <input class="input" v-model="aiInstruction" :placeholder="aiAction==='generate' ? '输入主题或额外要求（可选）' : '额外要求（可选）'" />
          <button class="btn" @click="onAiWrite" :disabled="aiLoading">{{ aiLoading ? '生成中...' : '开始生成' }}</button>
          <div v-if="aiResult" class="ai-result">
            <div class="ai-result-header">
              <span>生成结果</span>
              <button class="btn secondary" @click="onInsertResult">插入到编辑器</button>
            </div>
            <div class="md-body ai-preview" v-html="aiResultHtml"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>


<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from '../utils/marked'
import { renderMermaid } from '../utils/mermaid'
import { articleApi, aiWriteApi } from '../api'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const form = reactive({ id: 0, title: '', content_md: '', tagsText: '', summary: '' })
const editorRef = ref(null)
const previewHtml = computed(() => marked.parse(form.content_md || ''))

watch(previewHtml, () => {
  setTimeout(() => {
    const el = document.querySelector('.preview')
    if (el) renderMermaid(el)
  }, 100)
})

const aiOpen = ref(true)
const aiAction = ref('generate')
const aiInstruction = ref('')
const aiLoading = ref(false)
const aiResult = ref('')
const aiResultHtml = computed(() => marked.parse(aiResult.value || ''))

const summaryLoading = ref(false)

onMounted(async () => {
  const id = route.params.id
  if (id) {
    const { data } = await articleApi.get(id)
    form.id = data.id
    form.title = data.title
    form.content_md = data.content_md
    form.tagsText = (data.tags || []).map(t => t.name).join(',')
    form.summary = data.summary || ''
  }
})

function onBack() {
  router.push('/manage')
}

async function onSubmit() {
  if (!form.title.trim()) { toast.error('请输入文章标题'); return }
  if (!form.summary.trim() && form.content_md.trim()) {
    try {
      const { data } = await aiWriteApi.write({ action: 'summary', content: form.content_md })
      form.summary = data.result
    } catch (_) { /* 生成失败不阻塞保存 */ }
  }
  const tags = form.tagsText.split(',').map(s => s.trim()).filter(Boolean)
  try {
    if (form.id) {
      await articleApi.update(form.id, { title: form.title, content_md: form.content_md, summary: form.summary, tags })
      toast.success('保存成功')
    } else {
      const { data } = await articleApi.create({ title: form.title, content_md: form.content_md, summary: form.summary, tags })
      toast.success('创建成功')
      form.id = data.id
      router.replace(`/manage/edit/${data.id}`)
    }
  } catch (e) {
    toast.error(e?.response?.data?.detail || '操作失败')
  }
}

function insert(before, after) {
  const el = editorRef.value
  if (!el) return
  const start = el.selectionStart || 0
  const end = el.selectionEnd || 0
  const value = form.content_md || ''
  const selected = value.slice(start, end) || '文本'
  form.content_md = value.slice(0, start) + before + selected + after + value.slice(end)
}

async function onAiWrite() {
  aiLoading.value = true
  aiResult.value = ''
  try {
    const body = { action: aiAction.value, instruction: aiInstruction.value || undefined }
    if (aiAction.value !== 'generate') {
      body.content = getSelectedOrAll()
    }
    if (aiAction.value === 'generate') {
      body.title = form.title || undefined
    }
    const { data } = await aiWriteApi.write(body)
    aiResult.value = data.result
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'AI 生成失败')
  } finally {
    aiLoading.value = false
  }
}

function getSelectedOrAll() {
  const el = editorRef.value
  if (!el) return form.content_md || ''
  const start = el.selectionStart || 0
  const end = el.selectionEnd || 0
  if (start !== end) return (form.content_md || '').slice(start, end)
  return form.content_md || ''
}

function onInsertResult() {
  if (!aiResult.value) return
  if (aiAction.value === 'summary') {
    form.content_md = aiResult.value + '\n\n' + (form.content_md || '')
  } else {
    form.content_md = aiResult.value
  }
  aiResult.value = ''
  toast.success('已插入编辑器')
}

async function onGenSummary() {
  if (!form.content_md.trim()) { toast.error('请先填写文章内容'); return }
  summaryLoading.value = true
  try {
    const { data } = await aiWriteApi.write({ action: 'summary', content: form.content_md })
    form.summary = data.result
    toast.success('摘要已生成')
  } catch (e) {
    toast.error(e?.response?.data?.detail || '生成摘要失败')
  } finally {
    summaryLoading.value = false
  }
}
</script>

<style scoped>
.editor-page { max-width: 1100px; margin: 0 auto; }
.editor-page, .editor-page * { cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23228BE6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z'/%3E%3Cpath d='m15 5 4 4'/%3E%3C/svg%3E") 2 22, auto; }
.editor-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.editor-header h2 { margin: 0; }
.editor-actions { display: flex; gap: 10px; }
.editor-body { display: flex; flex-direction: column; gap: 16px; }
.editor-meta { display: flex; gap: 12px; }
.editor-meta .input { flex: 1; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
.toolbar .btn { border-radius: 20px; padding: 6px 14px; font-size: 13px; }
.editor-split {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  min-height: 500px;
}
@media (max-width: 900px) { .editor-split { grid-template-columns: 1fr; } }
.editor-input {
  min-height: 500px; font-size: 14px; line-height: 1.8;
  background: #fff !important;
}
.editor-input:focus {
  border-color: var(--brand) !important;
  box-shadow: 0 0 0 2px rgba(34,139,230,0.15) !important;
}
.preview { padding: 16px; background: #fff; border: 1.5px solid var(--border); border-radius: 12px; overflow: auto; }

.ai-panel {
  margin-top: 20px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
}
.ai-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; background: #F8F9FA; cursor: pointer; font-weight: 600; font-size: 14px;
}
.ai-toggle { color: var(--brand); font-weight: 400; font-size: 13px; }
.ai-body { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.ai-actions { display: flex; gap: 8px; }
.ai-actions .btn.active { background: var(--brand); color: #fff; }
.ai-result { border-top: 1px solid var(--border); padding-top: 12px; }
.ai-result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; font-weight: 600; font-size: 14px; }
.ai-preview { max-height: 300px; overflow: auto; padding: 12px; background: #F8F9FA; border-radius: 6px; }
.summary-row { display: flex; gap: 10px; }
.summary-row .input { flex: 1; }
.summary-row .btn { white-space: nowrap; }
.summary-row { display: flex; gap: 10px; }
.summary-row .input { flex: 1; }
.summary-row .btn { white-space: nowrap; }
</style>
