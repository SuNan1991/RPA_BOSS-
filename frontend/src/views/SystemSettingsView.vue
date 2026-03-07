<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-bold text-text-primary">系统设置</h1>
      <p class="text-text-secondary mt-1">管理您的账户和应用偏好</p>
    </div>

    <!-- Settings Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex gap-4 -mb-px">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-primary text-primary'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="mt-6">
      <!-- Accounts Tab -->
      <div v-if="activeTab === 'accounts'" class="space-y-4">
        <AccountManagementTab />
      </div>

      <!-- General Tab -->
      <div v-if="activeTab === 'general'" class="space-y-4">
        <GlassCard class="p-6">
          <h2 class="text-lg font-semibold mb-4">外观设置</h2>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium">暗色模式</p>
                <p class="text-sm text-text-secondary">切换应用的明暗主题</p>
              </div>
              <button
                @click="toggleTheme"
                :class="[
                  'relative w-14 h-7 rounded-full transition-colors',
                  isDark ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'absolute top-1 w-5 h-5 bg-white rounded-full shadow transition-transform',
                    isDark ? 'translate-x-8' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
          </div>
        </GlassCard>

        <GlassCard class="p-6">
          <h2 class="text-lg font-semibold mb-4">通知设置</h2>
          <div class="space-y-4">
            <label class="flex items-center justify-between">
              <div>
                <p class="font-medium">桌面通知</p>
                <p class="text-sm text-text-secondary">接收新消息和任务更新通知</p>
              </div>
              <input
                v-model="settings.desktopNotifications"
                type="checkbox"
                class="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
            </label>
            <label class="flex items-center justify-between">
              <div>
                <p class="font-medium">声音提醒</p>
                <p class="text-sm text-text-secondary">通知时播放提示音</p>
              </div>
              <input
                v-model="settings.soundEnabled"
                type="checkbox"
                class="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
            </label>
          </div>
        </GlassCard>
      </div>

      <!-- Logs Tab -->
      <div v-if="activeTab === 'logs'" class="space-y-4">
        <GlassCard class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">操作日志</h2>
            <button
              @click="loadLogs"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              刷新
            </button>
          </div>
          <LogViewer />
        </GlassCard>
      </div>

      <!-- About Tab -->
      <div v-if="activeTab === 'about'" class="space-y-4">
        <GlassCard class="p-6 text-center">
          <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
            <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold">BOSS 直聘助手</h2>
          <p class="text-text-secondary mt-1">版本 1.0.0</p>
          <p class="text-sm text-text-secondary mt-4 max-w-md mx-auto">
            安全、便捷的 BOSS 直聘自动化工具，支持多账户管理、候选人搜索、批量打招呼等功能。
          </p>
          <div class="mt-6 flex justify-center gap-4 text-sm text-text-secondary">
            <a href="#" class="hover:text-primary transition-colors">使用文档</a>
            <a href="#" class="hover:text-primary transition-colors">隐私政策</a>
            <a href="#" class="hover:text-primary transition-colors">开源许可</a>
          </div>
        </GlassCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import GlassCard from '@/components/ui/GlassCard.vue'
import AccountManagementTab from '@/components/account/AccountManagementTab.vue'
import LogViewer from '@/components/LogViewer.vue'
import { useTheme } from '@/composables/useTheme'

const { mode, toggleTheme } = useTheme()

const isDark = computed(() => mode === 'dark')

// Tabs
const tabs = [
  { key: 'accounts', label: '账户管理' },
  { key: 'general', label: '通用设置' },
  { key: 'logs', label: '操作日志' },
  { key: 'about', label: '关于' },
]
const activeTab = ref('accounts')

// Settings
const settings = ref({
  desktopNotifications: true,
  soundEnabled: false,
})

// Methods
async function loadLogs() {
  // LogViewer has its own refresh logic
}
</script>
