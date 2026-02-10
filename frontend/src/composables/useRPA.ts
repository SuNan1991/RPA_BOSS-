/**
 * useRPA - RPA operations composable
 */
import { ref, onUnmounted } from 'vue'
import { useRPAStore } from '@/stores/rpa'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from './useWebSocket'
import api from '@/api'

export function useRPA() {
  const rpaStore = useRPAStore()
  const authStore = useAuthStore()
  const { onMessage, isConnected } = useWebSocket()

  const monitoring = ref(false)

  async function startLogin() {
    try {
      const response = await api.post('/api/auth/login', {})

      if (response.data.status === 'browser_opened') {
        rpaStore.setStatus('browser_opened')
        return { success: true }
      }

      return { success: false, message: response.data.message }

    } catch (e: any) {
      return { success: false, message: e.response?.data?.detail || 'Login failed' }
    }
  }

  async function monitorStatus() {
    monitoring.value = true

    // Set up WebSocket listener
    const unsubscribe = onMessage((data) => {
      if (data.type === 'status' || data.type === 'status_update') {
        const statusData = data.data

        // Update RPA status
        if (statusData.is_logged_in) {
          rpaStore.setStatus('login_successful')
          authStore.setAuth({
            isAuthenticated: true,
            user: statusData.user_info
          })
        }

        // Update browser status
        if (statusData.browser_status) {
          rpaStore.setBrowserId(statusData.browser_status)
        }
      }
    })

    // Cleanup on unmount
    onUnmounted(() => {
      unsubscribe()
      monitoring.value = false
    })
  }

  return {
    monitoring,
    isConnected,
    startLogin,
    monitorStatus
  }
}
