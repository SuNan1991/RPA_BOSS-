/**
 * useWebSocket - WebSocket connection composable
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useHRStore } from '@/stores/hr'

type MessageHandler = (data: any) => void

export function useWebSocket() {
  const connected = ref(false)
  const connecting = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 10

  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null
  const messageHandlers: MessageHandler[] = []

  function connect() {
    if (ws?.readyState === WebSocket.OPEN) {
      return
    }

    connecting.value = true

    try {
      const wsUrl = `ws://localhost:8000/api/auth/ws`
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected')
        connected.value = true
        connecting.value = false
        reconnectAttempts.value = 0

        // Start heartbeat
        startHeartbeat()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle specific message types
          handleMessageByType(data)

          // Call registered handlers
          messageHandlers.forEach(handler => handler(data))
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        connected.value = false
        connecting.value = false

        // Attempt to reconnect
        scheduleReconnect()
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        connecting.value = false
      }

    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      connecting.value = false
      scheduleReconnect()
    }
  }

  function handleMessageByType(data: any) {
    const hrStore = useHRStore()

    switch (data.type) {
      case 'account_switched':
        // Handle account switched event
        console.log('Account switched:', data.data)
        hrStore.loadAccounts()
        break

      case 'candidate_found':
        // Handle new candidate found
        console.log('New candidate found:', data.data)
        hrStore.loadCandidates()
        break

      case 'greet_progress':
        // Handle greet progress update
        console.log('Greet progress:', data.data)
        break

      case 'account_login_success':
        // 账号登录成功
        console.log('Account login success:', data.data)
        const loginAccountId = data.data?.account_id
        const loginAccountName = data.data?.account_name
        const loginUserInfo = data.data?.user_info

        if (loginAccountId) {
          // 动态导入避免循环依赖
          import('@/stores/auth').then(({ useAuthStore }) => {
            const authStore = useAuthStore()
            authStore.setAuth({
              isAuthenticated: true,
              user: loginUserInfo,
              accountId: loginAccountId
            })
          })

          // 更新活跃账号
          hrStore.switchAccount(loginAccountId)

          // 刷新账号列表
          hrStore.loadAccounts()

          // 通知 useAccountLogin composable
          import('@/composables/useAccountLogin').then(({ useAccountLogin }) => {
            const { handleLoginSuccess } = useAccountLogin()
            handleLoginSuccess(loginAccountId, loginUserInfo)
          })

          console.log(`Account ${loginAccountName} (${loginAccountId}) login success`)
        }
        break

      case 'account_login_failed':
        // 账号登录失败
        console.log('Account login failed:', data.data)
        const failedAccountId = data.data?.account_id
        const failedReason = data.data?.reason || '未知错误'

        if (failedAccountId) {
          // 通知 useAccountLogin composable
          import('@/composables/useAccountLogin').then(({ useAccountLogin }) => {
            const { handleLoginFailed } = useAccountLogin()
            handleLoginFailed(failedAccountId, failedReason)
          })

          console.error(`Account ${failedAccountId} login failed: ${failedReason}`)
        }
        break

      case 'status':
      case 'status_update':
        // Handle auth status updates - 验证 user_info 后再更新认证状态
        console.log('Status update:', data)

        // 验证：is_logged_in 和 user_info 都必须有效
        const isLoggedIn = data.data?.is_logged_in
        const userInfo = data.data?.user_info
        const accountId = data.data?.account_id  // 新增
        const isNewAccount = data.data?.is_new_account  // 新增
        const syncMessage = data.data?.sync_message  // 新增
        const hasValidUserInfo = userInfo && Object.keys(userInfo).length > 0

        if (isLoggedIn && hasValidUserInfo) {
          // 动态导入避免循环依赖
          import('@/stores/auth').then(({ useAuthStore }) => {
            const authStore = useAuthStore()
            authStore.setAuth({
              isAuthenticated: true,
              user: userInfo,
              accountId: accountId  // 新增
            })
            console.log('Auth state updated: isAuthenticated = true, accountId =', accountId)

            // 显示同步提示
            if (syncMessage) {
              const icon = isNewAccount ? '✓' : '↻'
              const title = isNewAccount ? '新账号已添加' : '账号已同步'
              console.log(`${icon} ${title}: ${syncMessage}`)

              // TODO: 接入 toast notification 系统
              // showToast({ type: 'success', title, message: syncMessage })
            }

            // 刷新账号列表（让新账号出现在管理界面）
            if (accountId) {
              import('@/stores/hr').then(({ useHRStore }) => {
                const hrStore = useHRStore()
                hrStore.loadAccounts()
                console.log('Account list refreshed')
              }).catch(err => {
                console.error('Failed to refresh account list:', err)
              })
            }
          }).catch(err => {
            console.error('Failed to update auth state:', err)
          })
        } else if (isLoggedIn && !hasValidUserInfo) {
          console.warn('Received is_logged_in=true but no valid user_info - ignoring')
        }
        break

      default:
        console.log('Unknown message type:', data.type)
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (ws) {
      ws.close()
      ws = null
    }

    connected.value = false
  }

  function scheduleReconnect() {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
    reconnectAttempts.value++

    console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.value})`)

    reconnectTimer = window.setTimeout(() => {
      connect()
    }, delay)
  }

  function startHeartbeat() {
    const heartbeatInterval = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send('ping')
      } else {
        clearInterval(heartbeatInterval)
      }
    }, 30000) // Send ping every 30 seconds
  }

  function send(data: any) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  function onMessage(handler: MessageHandler) {
    messageHandlers.push(handler)

    // Return unsubscribe function
    return () => {
      const index = messageHandlers.indexOf(handler)
      if (index > -1) {
        messageHandlers.splice(index, 1)
      }
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    connecting,
    connect,
    disconnect,
    send,
    onMessage,
    isConnected: connected
  }
}
