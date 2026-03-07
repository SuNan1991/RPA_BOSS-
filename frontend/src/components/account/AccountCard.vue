<template>
  <GlassCard
    class="p-4 transition-all"
    :class="{
      'ring-2 ring-primary': isActive,
      'bg-primary/5 dark:bg-primary/10': isActive,
    }"
  >
    <div class="flex items-center gap-4">
      <!-- Checkbox -->
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('select', account.id)"
        class="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
      />

      <!-- Avatar -->
      <div
        class="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white font-semibold flex-shrink-0"
      >
        {{ account.username?.charAt(0)?.toUpperCase() || '?' }}
      </div>

      <!-- Account Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="font-semibold text-text-primary truncate">
            {{ account.username || `账户 ${account.id}` }}
          </h3>
          <StatusIndicator
            :status="cookieStatusColor"
            :show-label="false"
          />
          <span
            v-if="isActive"
            class="px-2 py-0.5 text-xs rounded-full bg-primary/20 text-primary"
          >
            当前
          </span>
          <!-- 登录中标记 -->
          <span
            v-if="isLoggingInForAccount"
            class="px-2 py-0.5 text-xs rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center gap-1"
          >
            <svg class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            登录中
          </span>
        </div>
        <p class="text-sm text-text-secondary">{{ account.phone || '未设置手机号' }}</p>
        <!-- 登录状态文本 -->
        <p v-if="isLoggingInForAccount && loginStatusText" class="text-sm text-primary mt-1">
          {{ loginStatusText }}
        </p>
        <div v-if="account.tags && account.tags.length > 0" class="flex gap-1 mt-1">
          <span
            v-for="tag in account.tags"
            :key="tag"
            class="px-2 py-0.5 text-xs rounded bg-gray-100 dark:bg-gray-700 text-text-secondary"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Quota & Last Active -->
      <div class="hidden md:flex items-center gap-6 text-sm">
        <div class="text-center">
          <p class="text-text-secondary">配额</p>
          <p class="font-medium">
            {{ account.quota_used || 0 }}/{{ account.quota_limit || 100 }}
          </p>
        </div>
        <div class="text-center">
          <p class="text-text-secondary">最后活跃</p>
          <p class="font-medium">{{ formatLastActive(account.last_operation_at) }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- 登录按钮 - 显示不同状态 -->
        <button
          v-if="account.cookie_status !== 'valid'"
          @click="handleLoginClick"
          :disabled="isLoggingInForAccount"
          class="px-3 py-1.5 text-sm rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
        >
          <svg v-if="isLoggingInForAccount" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ loginButtonText }}</span>
        </button>
        <!-- 恢复会话按钮 - cookie有效但浏览器未运行时显示 -->
        <button
          v-else-if="account.cookie_status === 'valid' && !browserRunning"
          @click="$emit('restore-browser', account.id)"
          :disabled="isRestoringBrowser"
          class="px-3 py-1.5 text-sm rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          title="浏览器未运行，点击恢复会话"
        >
          <svg v-if="isRestoringBrowser" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{{ isRestoringBrowser ? '恢复中...' : '恢复会话' }}</span>
        </button>
        <button
          @click="$emit('refresh', account.id)"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          刷新
        </button>
        <button
          v-if="!isActive"
          @click="$emit('switch', account.id)"
          class="px-3 py-1.5 text-sm rounded-lg bg-green-500 text-white hover:bg-green-600 transition-colors"
        >
          切换
        </button>
        <button
          @click="$emit('view-detail', account.id)"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          详情
        </button>
        <button
          @click="$emit('delete', account.id)"
          class="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          title="删除"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import type { HRAccount } from '@/stores/hr'
import { useAccountLogin } from '@/composables/useAccountLogin'

const props = defineProps<{
  account: HRAccount
  selected: boolean
  isActive: boolean
  browserRunning?: boolean  // 浏览器是否在运行
  isRestoringBrowser?: boolean  // 是否正在恢复浏览器
}>()

const emit = defineEmits<{
  select: [accountId: number]
  login: [accountId: number]
  refresh: [accountId: number]
  switch: [accountId: number]
  edit: [accountId: number]
  delete: [accountId: number]
  'view-detail': [accountId: number]
  'restore-browser': [accountId: number]  // 恢复浏览器会话
}>()

// 使用账号登录 composable
const {
  isLoggingIn,
  loginStatus,
  currentAccountId,
  loginStatusText
} = useAccountLogin()

// 判断当前账号是否正在登录
const isLoggingInForAccount = computed(() => {
  return isLoggingIn.value && currentAccountId.value === props.account.id
})

// 登录按钮文本
const loginButtonText = computed(() => {
  if (isLoggingInForAccount.value) {
    switch (loginStatus.value) {
      case 'opening':
        return '打开中...'
      case 'waiting_qrcode':
        return '扫码中...'
      default:
        return '登录中...'
    }
  }
  return '登录'
})

// 处理登录按钮点击
async function handleLoginClick() {
  emit('login', props.account.id)
}

const cookieStatusColor = computed(() => {
  switch (props.account.cookie_status) {
    case 'valid':
      return 'connected'
    case 'invalid':
      return 'disconnected'
    default:
      return 'disconnected'
  }
})

function formatLastActive(dateStr?: string): string {
  if (!dateStr) return '从未'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString()
}
</script>
