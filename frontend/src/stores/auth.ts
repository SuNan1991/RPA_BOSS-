/**
 * Auth Store - Manage authentication state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const isAuthenticated = ref(false)
  const user = ref<UserInfo | null>(null)
  const session = ref<any>(null)

  // Getters
  const userName = computed(() => user.value?.username || '未登录')
  const userAvatar = computed(() => user.value?.avatar || null)

  // Actions
  function setAuth(authData: { isAuthenticated: boolean; user?: UserInfo | null; session?: any }) {
    // 验证：只有 isAuthenticated=true 且 user 有效时才设置认证状态
    const isValidAuth = authData.isAuthenticated && authData.user && Object.keys(authData.user).length > 0

    if (authData.isAuthenticated && !isValidAuth) {
      console.warn('setAuth called with isAuthenticated=true but no valid user info - treating as not authenticated')
    }

    isAuthenticated.value = isValidAuth
    user.value = isValidAuth ? authData.user : null
    session.value = isValidAuth ? (authData.session || null) : null

    // Persist to localStorage only if valid
    if (isValidAuth) {
      localStorage.setItem('auth', JSON.stringify({
        isAuthenticated: true,
        user: authData.user
      }))
    } else {
      localStorage.removeItem('auth')
    }
  }

  function clearAuth() {
    isAuthenticated.value = false
    user.value = null
    session.value = null
    localStorage.removeItem('auth')
  }

  function loadFromStorage() {
    const stored = localStorage.getItem('auth')
    if (stored) {
      try {
        const data = JSON.parse(stored)

        // 验证：只有 user 有效才恢复认证状态
        const hasValidUser = data.user && Object.keys(data.user).length > 0

        if (data.isAuthenticated && hasValidUser) {
          isAuthenticated.value = true
          user.value = data.user
        } else {
          // 清除无效的存储数据
          console.warn('Invalid auth data in localStorage - clearing')
          localStorage.removeItem('auth')
          isAuthenticated.value = false
          user.value = null
        }
      } catch (e) {
        console.error('Error loading auth from storage:', e)
        // 清除损坏的数据
        localStorage.removeItem('auth')
      }
    }
  }

  return {
    // State
    isAuthenticated,
    user,
    session,
    // Getters
    userName,
    userAvatar,
    // Actions
    setAuth,
    clearAuth,
    loadFromStorage
  }
})
