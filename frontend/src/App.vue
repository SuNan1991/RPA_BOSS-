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

onMounted(() => {
  // Initialize theme
  themeStore.loadTheme()

  // Load auth from storage
  authStore.loadFromStorage()

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
