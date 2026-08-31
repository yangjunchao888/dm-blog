import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', redirect: '/articles' },
  { path: '/articles', name: 'articles', component: () => import('../views/ArticleList.vue') },
  { path: '/articles/:id', name: 'article-detail', component: () => import('../views/ArticleDetail.vue') },
  { path: '/manage', name: 'manage', component: () => import('../views/Manage.vue') },
  { path: '/manage/new', name: 'editor-new', component: () => import('../views/Editor.vue') },
  { path: '/manage/edit/:id', name: 'editor-edit', component: () => import('../views/Editor.vue') },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue') },
  { path: '/account', name: 'account', component: () => import('../views/Account.vue') },
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
