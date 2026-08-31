<template>
  <section class="card login-card">
    <h2>登录</h2>
    <div class="grid">
      <input class="input" v-model="form.username" placeholder="用户名" />
      <input class="input" v-model="form.password" type="password" placeholder="密码" />
      <button class="btn" @click="onLogin">登录</button>
      <p class="muted">没有账号？<router-link to="/register">去注册</router-link></p>
    </div>
  </section>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const form = reactive({ username: '', password: '' })
function validate() {
  if (!form.username || form.username.length < 3) return '用户名至少 3 个字符'
  if (form.username.length > 64) return '用户名不能超过 64 个字符'
  if (!form.password || form.password.length < 6) return '密码至少 6 个字符'
  if (form.password.length > 128) return '密码不能超过 128 个字符'
  return ''
}
async function onLogin() {
  const msg = validate()
  if (msg) { toast.error(msg); return }
  try {
    await auth.login(form)
    toast.success('登录成功')
    router.push('/manage')
  } catch (e) {
    toast.error(e?.response?.data?.detail || '登录失败，请检查用户名和密码')
  }
}
</script>

<style scoped>
.login-card { max-width: 400px; margin: 60px auto; text-align: center; }
.login-card h2 { margin: 0 0 20px; }
</style>
.login-card h2 {
  background: linear-gradient(135deg, #FF6B9D, var(--brand-2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
