<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-bg-primary">
    <!-- Landing Page -->
    <LandingPage v-if="!isAuthenticated" />

    <!-- Authenticated Page -->
    <AuthenticatedPage v-else />

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
import LandingPage from '@/components/LandingPage.vue'
import AuthenticatedPage from '@/components/AuthenticatedPage.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const isDark = computed(() => themeStore.mode === 'dark')
const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(async () => {
  // Load theme
  themeStore.loadTheme()

  // Load auth from storage
  authStore.loadFromStorage()
})
</script>
