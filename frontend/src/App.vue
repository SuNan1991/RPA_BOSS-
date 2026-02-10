<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'

const themeStore = useThemeStore()
const authStore = useAuthStore()

onMounted(() => {
  // Initialize theme
  themeStore.loadTheme()

  // Load auth from storage
  authStore.loadFromStorage()
})
</script>

<style>
#app {
  height: 100%;
}
</style>
