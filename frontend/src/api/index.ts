/**
 * API Client
 */
import axios from 'axios'
import type { AuthStatus } from '@/types'

const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  getStatus: () => api.get<AuthStatus>('/api/auth/status'),
  login: () => api.post('/api/auth/login', {}),
  logout: () => api.post('/api/auth/logout'),
  getLogs: (params?: { limit?: number; offset?: number }) =>
    api.get('/api/auth/logs', { params })
}

export default api
