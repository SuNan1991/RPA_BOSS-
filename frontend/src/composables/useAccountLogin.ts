/**
 * useAccountLogin - Account login composable
 * 专门处理账号登录的完整流程
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useHRStore } from '@/stores/hr'
import { useRPAStore } from '@/stores/rpa'
import api from '@/api'

// 轮询定时器（模块级，避免被重置）
let pollingTimer: number | null = null

export type LoginStatus = 'idle' | 'opening' | 'waiting_qrcode' | 'success' | 'failed' | 'timeout'

export interface LoginResult {
  success: boolean
  message?: string
  account_id?: number
}

export interface LoginStatusResult {
  status: LoginStatus
  account_id: number | null
  message?: string
}

export function useAccountLogin() {
  const authStore = useAuthStore()
  const hrStore = useHRStore()
  const rpaStore = useRPAStore()

  // 状态
  const isLoggingIn = ref(false)
  const loginStatus = ref<LoginStatus>('idle')
  const currentAccountId = ref<number | null>(null)
  const error = ref<string | null>(null)

  // 计算属性
  const isLoginInProgress = computed(() => isLoggingIn.value && loginStatus.value !== 'idle')

  /**
   * 启动账号登录
   */
  async function loginAccount(accountId: number): Promise<LoginResult> {
    // 防止重复登录
    if (isLoggingIn.value) {
      return { success: false, message: '有登录正在进行，请稍后' }
    }

    isLoggingIn.value = true
    loginStatus.value = 'opening'
    currentAccountId.value = accountId
    error.value = null

    try {
      // 1. 调用登录 API
      const response = await api.post(`/api/auth/login/account`, {
        account_id: accountId
      })

      if (response.data.status === 'browser_opened') {
        loginStatus.value = 'waiting_qrcode'
        rpaStore.setStatus('browser_opened')

        // 2. 启动轮询作为备选方案（WebSocket 的双重保障）
        _startPollingLoginStatus(accountId)

        return { success: true, message: '浏览器已打开，请扫码登录', account_id: accountId }
      }

      if (response.data.status === 'error') {
        loginStatus.value = 'failed'
        return { success: false, message: response.data.message || '登录启动失败' }
      }

      return { success: false, message: '未知状态' }

    } catch (e: any) {
      loginStatus.value = 'failed'
      const errorMsg = e.response?.data?.detail || e.message || '网络错误，请重试'
      error.value = errorMsg
      return { success: false, message: errorMsg }
    }
  }

  /**
   * 启动轮询监控登录状态（作为 WebSocket 的备选方案）
   * @param _accountId 账号ID（未使用，保留用于未来扩展）
   */
  function _startPollingLoginStatus(_accountId: number) {
    // 清除之前的轮询
    _stopPollingLoginStatus()

    const maxAttempts = 150 // 5分钟，2秒间隔
    let attempts = 0

    pollingTimer = window.setInterval(async () => {
      attempts++

      try {
        // 检查浏览器是否还在运行
        const statusResponse = await api.get('/api/auth/status')
        const { browser_opened, is_logged_in } = statusResponse.data

        // 如果浏览器关闭了，登录取消
        if (!browser_opened && loginStatus.value === 'waiting_qrcode') {
          _stopPollingLoginStatus()
          loginStatus.value = 'failed'
          isLoggingIn.value = false
          error.value = '浏览器已关闭'
          return
        }

        // 如果登录成功了（通过 WebSocket 消息处理，这里只是备用检查）
        if (is_logged_in && loginStatus.value !== 'success') {
          // 这里的逻辑主要由 WebSocket 处理
          // 轮询只是确保不会因为 WebSocket 故障而完全卡住
        }

        // 超时检查
        if (attempts >= maxAttempts) {
          _stopPollingLoginStatus()
          loginStatus.value = 'timeout'
          isLoggingIn.value = false
          error.value = '登录超时（5分钟）'
        }

      } catch (e) {
        console.error('Error polling login status:', e)
      }
    }, 2000) // 2秒间隔
  }

  /**
   * 停止轮询
   */
  function _stopPollingLoginStatus() {
    if (pollingTimer !== null) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  /**
   * 处理登录成功（由 useWebSocket 调用）
   */
  function handleLoginSuccess(accountId: number, userInfo: any) {
    loginStatus.value = 'success'
    isLoggingIn.value = false
    _stopPollingLoginStatus()

    // 更新认证状态
    authStore.setAuth({
      isAuthenticated: true,
      user: userInfo,
      accountId: accountId
    })

    // 设置为活跃账号
    hrStore.switchAccount(accountId)

    // 刷新账号列表
    hrStore.loadAccounts()

    console.log(`[useAccountLogin] Account ${accountId} login success`)
  }

  /**
   * 处理登录失败（由 useWebSocket 调用）
   */
  function handleLoginFailed(accountId: number, reason: string) {
    // 只处理当前正在登录的账号
    if (currentAccountId.value !== accountId) {
      return
    }

    loginStatus.value = 'failed'
    isLoggingIn.value = false
    _stopPollingLoginStatus()

    error.value = reason || '登录失败'

    console.error(`[useAccountLogin] Account ${accountId} login failed: ${reason}`)
  }

  /**
   * 取消登录
   */
  function cancelLogin() {
    _stopPollingLoginStatus()
    loginStatus.value = 'idle'
    isLoggingIn.value = false
    currentAccountId.value = null
    error.value = null
  }

  /**
   * 获取登录状态文本
   */
  const loginStatusText = computed(() => {
    switch (loginStatus.value) {
      case 'opening':
        return '正在打开浏览器...'
      case 'waiting_qrcode':
        return '请使用 BOSS 直聘 APP 扫码登录'
      case 'success':
        return '登录成功！'
      case 'failed':
        return error.value || '登录失败'
      case 'timeout':
        return '登录超时，请重试'
      default:
        return ''
    }
  })

  return {
    // 状态
    isLoggingIn,
    loginStatus,
    currentAccountId,
    error,
    isLoginInProgress,
    loginStatusText,

    // 方法
    loginAccount,
    cancelLogin,
    handleLoginSuccess,
    handleLoginFailed
  }
}

// 类型已在文件开头导出
