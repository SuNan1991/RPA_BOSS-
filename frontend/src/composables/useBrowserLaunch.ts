/**
 * 浏览器启动 Composable
 * 封装浏览器启动流程和状态管理
 */
import { ref } from 'vue'
import api from '@/api'
import { useRPAStore } from '@/stores/rpa'

export function useBrowserLaunch() {
  const rpaStore = useRPAStore()

  const isLaunching = ref(false)
  const browserOpened = ref(false)
  const error = ref<string | null>(null)

  /**
   * 启动 BOSS 网页浏览器
   */
  async function launch() {
    isLaunching.value = true
    error.value = null

    try {
      const response = await api.post('/api/auth/login', {})
      if (response.data.status === 'browser_opened') {
        browserOpened.value = true
        rpaStore.setStatus('browser_opened')
      } else {
        error.value = response.data.message || '启动失败'
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || '网络错误，请重试'
    } finally {
      isLaunching.value = false
    }
  }

  /**
   * 重置状态
   */
  function reset() {
    browserOpened.value = false
    error.value = null
  }

  return {
    isLaunching,
    browserOpened,
    error,
    launch,
    reset
  }
}
