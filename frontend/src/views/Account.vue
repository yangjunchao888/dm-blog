<template>
  <section class="account-page">
    <h2>账号信息</h2>

    <div class="card info-card">
      <div class="info-row">
        <span class="label">用户名</span>
        <span>{{ user.username }}</span>
      </div>
      <div class="info-row">
        <span class="label">昵称</span>
        <span>{{ user.nickname || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">注册时间</span>
        <span>{{ user.created_at || '-' }}</span>
      </div>
    </div>

    <h3>修改密码</h3>
    <div class="card pwd-card">
      <div class="grid">
        <input class="input" v-model="form.old_password" type="password" placeholder="原密码" />
        <input class="input" v-model="form.new_password" type="password" placeholder="新密码（至少6位）" />
        <input class="input" v-model="form.confirm" type="password" placeholder="确认新密码" />
        <button class="btn" @click="onChangePwd" :disabled="loading">{{ loading ? '提交中...' : '修改密码' }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { accountApi } from '../api'
import { useToastStore } from '../stores/toast'

const toast = useToastStore()
const user = ref({ username: '', nickname: '', created_at: '' })
const form = reactive({ old_password: '', new_password: '', confirm: '' })
const loading = ref(false)

onMounted(async () => {
  const { data } = await accountApi.me()
  user.value = data
})

async function onChangePwd() {
  if (!form.old_password || form.old_password.length < 6) { toast.error('请输入原密码'); return }
  if (!form.new_password || form.new_password.length < 6) { toast.error('新密码至少6位'); return }
  if (form.new_password !== form.confirm) { toast.error('两次密码不一致'); return }
  loading.value = true
  try {
    await accountApi.changePassword({ old_password: form.old_password, new_password: form.new_password })
    toast.success('密码修改成功')
    form.old_password = ''
    form.new_password = ''
    form.confirm = ''
  } catch (e) {
    toast.error(e?.response?.data?.detail || '修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.account-page { max-width: 560px; margin: 0 auto; }
.account-page h2 { margin: 0 0 16px; }
.account-page h3 { margin: 24px 0 12px; }
.info-card { display: flex; flex-direction: column; gap: 12px; }
.info-row { display: flex; gap: 12px; }
.label { color: var(--muted); min-width: 70px; }
.pwd-card .grid { gap: 12px; }
</style>
