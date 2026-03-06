<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-bg-primary">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const isDark = computed(() => themeStore.mode === 'dark')

// 监听认证状态变化，登录成功后自动跳转
watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      const currentPath = router.currentRoute.value.path
      // 只有在登录页时才自动跳转到主页
      if (currentPath === '/login') {
        router.push('/')
      }
    }
  }
)

onMounted(async () => {
  // Initialize theme
  themeStore.loadTheme()

  // Load auth from storage first (for quick UI response)
  authStore.loadFromStorage()

  // 后端 API 基础 URL
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  // 然后与后端同步验证
  try {
    const response = await fetch(`${apiBaseUrl}/api/auth/status`)
    if (response.ok) {
      const status = await response.json()
      console.log('Backend status:', status)

      // 情况1: 后端有有效 session 且浏览器已打开
      if (status.is_logged_in && status.browser_opened && status.user_info) {
        console.log('Session valid and browser running')
        authStore.setAuth({
          isAuthenticated: true,
          user: status.user_info
        })
      }

      // 情况2: 后端有 session 但浏览器未打开（尝试恢复）
      else if (status.is_logged_in && !status.browser_opened && status.user_info) {
        console.log('Session valid but browser not running, attempting to restore...')

        // 尝试调用恢复 API
        try {
          const restoreResponse = await fetch(`${apiBaseUrl}/api/auth/restore-browser`, {
            method: 'POST'
          })
          if (restoreResponse.ok) {
            const restoreResult = await restoreResponse.json()
            console.log('Restore result:', restoreResult)

            if (restoreResult.browser_opened) {
              authStore.setAuth({
                isAuthenticated: true,
                user: status.user_info
              })
            } else {
              // 恢复失败，清除认证状态
              console.warn('Browser restore failed, clearing auth')
              authStore.clearAuth()
            }
          }
        } catch (restoreError) {
          console.error('Failed to restore browser:', restoreError)
          // 恢复失败，清除认证状态
          authStore.clearAuth()
        }
      }

      // 情况3: 无有效 session
      else if (!status.is_logged_in) {
        console.log('No valid session')
        if (authStore.isAuthenticated) {
          console.warn('Backend reports not logged in, clearing stale localStorage data')
          authStore.clearAuth()
        }
      }
    }
  } catch (error) {
    console.error('Failed to sync auth status with backend:', error)
    // 如果后端不可达，清除认证状态（保守策略）
    if (authStore.isAuthenticated) {
      console.warn('Backend unreachable, clearing auth state to be safe')
      authStore.clearAuth()
    }
  }

  // 如果已登录且在登录页，跳转到主页
  if (authStore.isAuthenticated && router.currentRoute.value.path === '/login') {
    router.push('/')
  }
})
</script>

<style>
#app {
  height: 100%;
}
</style>
