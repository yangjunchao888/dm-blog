import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

export const authApi = {
  login: (body) => api.post('/auth/login', body),
}

export const articleApi = {
  list: (params) => api.get('/articles', { params }),
  get: (id) => api.get(`/articles/${id}`),
  create: (body) => api.post('/articles', body),
  update: (id, body) => api.put(`/articles/${id}`, body),
  remove: (id) => api.delete(`/articles/${id}`),
}

export const tagApi = {
  list: () => api.get('/tags'),
}

export const chatApi = {
  send: (message) => api.post('/chat', { message }),
}

export const aiWriteApi = {
  write: (body) => api.post('/ai/write', body),
}

export const accountApi = {
  me: () => api.get('/account/me'),
  changePassword: (body) => api.post('/account/change-password', body),
}
