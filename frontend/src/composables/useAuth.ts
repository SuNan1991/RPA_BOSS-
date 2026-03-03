/**
 * useAuth - Authentication composable
 */
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRPAStore } from '@/stores/rpa'
import api from '@/api'

// 轮询定时器（模块级，避免被重置）
let statusPollingTimer: number | null = null

export function useAuth() {
  const authStore = useAuthStore()
  const rpaStore = useRPAStore()

  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login() {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/login', {})

      if (response.data.status === 'browser_opened') {
        rpaStore.setStatus('browser_opened')
        return { success: true, message: response.data.message }
      }

      return { success: false, message: response.data.message || 'Login failed' }

    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to start login'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    // 停止轮询
    stopPollingLoginStatus()

    try {
      const response = await api.post('/api/auth/logout')

      authStore.clearAuth()
      rpaStore.reset()

      return { success: true, message: response.data.message }

    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Logout failed'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  async function checkStatus() {
    try {
      const response = await api.get('/api/auth/status')

      authStore.setAuth({
        isAuthenticated: response.data.is_logged_in,
        user: response.data.user_info
      })

      return response.data

    } catch (e: any) {
      console.error('Error checking status:', e)
      return null
    }
  }

  async function startPollingLoginStatus(callback?: (isLogged: boolean) => void) {
    // 先停止之前的轮询
    stopPollingLoginStatus()

    const maxAttempts = 150 // 5分钟，2秒间隔
    let attempts = 0

    console.log('Starting login status polling...')

    statusPollingTimer = window.setInterval(async () => {
      attempts++

      try {
        const result = await checkStatus()

        if (result?.is_logged_in) {
          console.log('Login detected via polling!')
          stopPollingLoginStatus()
          callback?.(true)
        } else if (attempts >= maxAttempts) {
          console.log('Login polling timeout after', maxAttempts, 'attempts')
          stopPollingLoginStatus()
          callback?.(false)
        }
      } catch (e) {
        console.error('Error polling login status:', e)
      }
    }, 2000) // 每2秒轮询一次
  }

  function stopPollingLoginStatus() {
    if (statusPollingTimer) {
      console.log('Stopping login status polling')
      clearInterval(statusPollingTimer)
      statusPollingTimer = null
    }
  }

  return {
    loading,
    error,
    login,
    logout,
    checkStatus,
    startPollingLoginStatus,
    stopPollingLoginStatus
  }
}
