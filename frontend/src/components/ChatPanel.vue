<template>
  <div class="chat-fab" @click="open = !open">AI</div>

  <div v-if="open" class="chat-panel card">
    <div class="chat-header">二次元助手</div>
    <div class="chat-messages" ref="box">
      <div v-for="(m,i) in messages" :key="i" :class="['msg', m.role]">
        <div class="bubble">
          <div>{{ m.text }}</div>
          <div v-if="m.links && m.links.length" class="links">
            <router-link v-for="l in m.links" :key="l.id" :to="`/articles/${l.id}`">• {{ l.title }}</router-link>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <input class="input" v-model="text" placeholder="说点什么..." @keyup.enter="send" />
      <button class="btn" @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { chatApi } from '../api'

const open = ref(false)
const text = ref('')
const messages = ref([{ role: 'ai', text: '你好，我是你的博客助手。可以问我：搜索文章、创建文章、修改文章。' }])
const box = ref(null)

async function send() {
  const q = text.value.trim()
  if (!q) return
  messages.value.push({ role: 'user', text: q })
  text.value = ''

  try {
    const { data } = await chatApi.send(q)
    if (data.type === 'tool') {
      if (data.action === 'search_articles') {
        const items = data.result.items || []
        messages.value.push({ role: 'ai', text: `找到 ${data.result.total} 篇相关文章`, links: items.map(i => ({ id: i.id, title: i.title })) })
      } else if (data.action === 'create_article') {
        messages.value.push({ role: 'ai', text: `已创建文章`, links: [{ id: data.result.id, title: data.result.title }] })
      } else {
        messages.value.push({ role: 'ai', text: `已更新文章`, links: [{ id: data.result.id, title: data.result.title }] })
      }
    } else {
      messages.value.push({ role: 'ai', text: data.reply || '收到。' })
    }
  } catch (e) {
    messages.value.push({ role: 'ai', text: '请求失败，请确认已登录。' })
  }

  await nextTick()
  if (box.value) box.value.scrollTop = box.value.scrollHeight
}
</script>

<style scoped>
.chat-fab {
  position: fixed; right: 20px; bottom: 20px; width: 48px; height: 48px; border-radius: 999px;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white; font-weight: 700;
}
.chat-panel {
  position: fixed; right: 20px; bottom: 80px; width: 360px; max-height: 520px; display: flex; flex-direction: column;
}
.chat-header { font-weight: 700; margin-bottom: 8px; }
.chat-messages { flex: 1; overflow: auto; }
.msg { margin: 8px 0; }
.msg.user .bubble { background: #e5e7eb; margin-left: 40px; }
.msg.ai .bubble { background: #f9fafb; margin-right: 40px; border: 1px solid var(--border); }
.bubble { padding: 10px 12px; border-radius: 10px; }
.chat-input { display: flex; gap: 8px; margin-top: 8px; }
.links { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.links a { color: var(--brand-2); }
</style>
