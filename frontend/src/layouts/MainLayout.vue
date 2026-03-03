<template>
  <div :class="{ dark: isDark }" class="min-h-screen bg-bg-primary flex flex-col md:flex-row">
    <!-- Mobile Header -->
    <header
      v-if="navigationStore.isMobile"
      class="md:hidden flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
    >
      <button
        @click="navigationStore.toggleMobileMenu()"
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-primary">BOSS 助手</h1>
      <AppHeader class="flex-1" />
    </header>

    <!-- Mobile Menu Overlay -->
    <div
      v-if="navigationStore.mobileMenuOpen && navigationStore.isMobile"
      class="fixed inset-0 bg-black/50 z-40 md:hidden"
      @click="navigationStore.closeMobileMenu()"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed md:sticky top-0 left-0 z-50 h-screen md:h-auto bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-transform duration-300',
        navigationStore.isMobile && navigationStore.mobileMenuOpen
          ? 'translate-x-0'
          : navigationStore.isMobile
          ? '-translate-x-full'
          : '',
        navigationStore.sidebarCollapsed ? 'md:w-16' : 'md:w-64',
      ]"
    >
      <!-- Logo (Desktop) -->
      <div class="hidden md:flex items-center gap-3 px-4 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <span
          v-show="!navigationStore.sidebarCollapsed"
          class="font-semibold text-lg text-primary transition-opacity duration-200"
        >
          BOSS 助手
        </span>
      </div>

      <!-- Navigation -->
      <nav class="p-2 space-y-1 overflow-y-auto flex-1">
        <NavItem
          v-for="item in NAV_ITEMS"
          :key="item.name"
          :item="item"
          :collapsed="navigationStore.sidebarCollapsed"
          @click="navigationStore.closeMobileMenu()"
        />
      </nav>

      <!-- Collapse Toggle (Desktop) -->
      <button
        class="hidden md:flex absolute bottom-4 right-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        @click="navigationStore.toggleSidebar()"
        :title="navigationStore.sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
      >
        <svg
          v-if="navigationStore.sidebarCollapsed"
          class="w-5 h-5 text-text-secondary"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
        <svg v-else class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-h-0 overflow-hidden">
      <!-- Desktop Header -->
      <header
        v-if="!navigationStore.isMobile"
        class="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
      >
        <AppHeader />
      </header>

      <!-- Page Content -->
      <div class="flex-1 overflow-y-auto p-4 md:p-6">
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>
    </main>

    <!-- Toast Container -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <!-- Toast notifications will be rendered here -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { useThemeStore } from '@/stores/theme'
import { NAV_ITEMS } from '@/router/routes'
import AppHeader from '@/components/layout/AppHeader.vue'
import NavItem from '@/components/navigation/NavItem.vue'

const navigationStore = useNavigationStore()
const themeStore = useThemeStore()

const isDark = computed(() => themeStore.mode === 'dark')

// Handle window resize
function handleResize() {
  if (typeof window !== 'undefined') {
    navigationStore.isMobile ? null : null
  }
}

onMounted(() => {
  // Initialize theme
  themeStore.loadTheme()
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
