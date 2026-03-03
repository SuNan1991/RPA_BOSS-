<template>
  <div class="flex items-center justify-between gap-4 w-full">
    <!-- Left: Title or Breadcrumb -->
    <div class="flex items-center gap-3">
      <div class="hidden md:block">
        <h2 class="text-lg font-semibold text-text-primary">{{ pageTitle }}</h2>
      </div>
    </div>

    <!-- Right: Account & Theme -->
    <div class="flex items-center gap-3">
      <!-- Account Switcher -->
      <AccountSwitcher />

      <!-- Theme Toggle -->
      <button
        @click="toggleTheme"
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        :title="mode === 'light' ? '切换到暗色模式' : '切换到亮色模式'"
      >
        <svg v-if="mode === 'light'" class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
        <svg v-else class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import AccountSwitcher from '@/components/business/AccountSwitcher.vue'

const route = useRoute()
const { mode, toggleTheme } = useTheme()

const pageTitle = computed(() => {
  return (route.meta.title as string) || 'BOSS 助手'
})
</script>
