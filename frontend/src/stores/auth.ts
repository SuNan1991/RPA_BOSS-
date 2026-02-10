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
    isAuthenticated.value = authData.isAuthenticated
    user.value = authData.user || null
    session.value = authData.session || null

    // Persist to localStorage
    if (authData.isAuthenticated) {
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
        isAuthenticated.value = data.isAuthenticated
        user.value = data.user
      } catch (e) {
        console.error('Error loading auth from storage:', e)
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
