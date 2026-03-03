<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-bg-primary">
    <!-- 只显示登录页面，跳转由路由处理 -->
    <LandingPage />

    <!-- Toast Container -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <!-- Toast notifications will be rendered here -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useRouter } from 'vue-router'
import LandingPage from '@/components/LandingPage.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isDark = computed(() => themeStore.mode === 'dark')

onMounted(() => {
  // Load theme
  themeStore.loadTheme()

  // Load auth from storage
  authStore.loadFromStorage()

  // 如果已经登录，直接跳转到主页
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>
