<template>
  <section class="card" style="max-width:420px;">
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
const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', password: '' })
async function onLogin() {
  await auth.login(form)
  router.push('/manage')
}
</script>
