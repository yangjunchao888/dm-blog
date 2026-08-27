import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/articles', name: 'articles', component: () => import('../views/ArticleList.vue') },
  { path: '/articles/:id', name: 'article-detail', component: () => import('../views/ArticleDetail.vue') },
  { path: '/manage', name: 'manage', component: () => import('../views/Manage.vue') },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const requiresAuth = to.path.startsWith('/manage')
  if (requiresAuth && !auth.token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
