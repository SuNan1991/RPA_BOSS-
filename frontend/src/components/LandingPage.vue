<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <GlassCard class="max-w-2xl w-full">
      <!-- Header with Theme Toggle -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-primary">BOSS 直聘 RPA 助手</h1>
          <p class="text-text-secondary mt-2">安全的 BOSS 直聘自动化工具</p>
        </div>
        <button
          @click="toggleTheme"
          class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          :title="mode === 'light' ? '切换到暗色模式' : '切换到亮色模式'"
        >
          <svg v-if="mode === 'light'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </button>
      </div>

      <!-- Connection Status -->
      <div class="flex items-center gap-2 mb-6">
        <StatusIndicator :status="wsStatus" show-label />
      </div>

      <!-- Login Section -->
      <div class="text-center py-8">
        <div class="mb-8">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-4">
            <svg class="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h2 class="text-2xl font-semibold mb-2">欢迎使用 BOSS 直聘 RPA 助手</h2>
          <p class="text-text-secondary">安全、便捷的自动化登录工具</p>
        </div>

        <!-- Login Button -->
        <Button
          variant="primary"
          :loading="loading"
          @click="handleLogin"
          class="w-full max-w-xs mx-auto"
        >
          {{ loginButtonText }}
        </Button>

        <!-- Login Instructions -->
        <div v-if="showInstructions" class="mt-8 text-left max-w-md mx-auto">
          <h3 class="font-semibold mb-4 text-center">登录步骤</h3>
          <ol class="space-y-3">
            <li class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm">1</span>
              <span>系统将自动打开 BOSS 直聘登录页</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm">2</span>
              <span>请使用 BOSS 直聘 App 扫码登录</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-sm">3</span>
              <span>登录成功后自动保存账号信息</span>
            </li>
          </ol>
        </div>

        <!-- Countdown Timer -->
        <div v-if="showCountdown" class="mt-6">
          <p class="text-text-secondary text-sm">登录剩余时间: {{ formattedTime }}</p>
        </div>
      </div>

      <!-- Features -->
      <div class="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">主要功能</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center">
            <div class="text-primary font-semibold text-lg">安全登录</div>
            <p class="text-sm text-text-secondary mt-1">用户辅助登录，避免自动化检测</p>
          </div>
          <div class="text-center">
            <div class="text-primary font-semibold text-lg">会话保存</div>
            <p class="text-sm text-text-secondary mt-1">加密保存登录状态，自动恢复</p>
          </div>
          <div class="text-center">
            <div class="text-primary font-semibold text-lg">实时监控</div>
            <p class="text-sm text-text-secondary mt-1">WebSocket 实时状态推送</p>
          </div>
        </div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { useWebSocket } from '@/composables/useWebSocket'
import { useRPAStore } from '@/stores/rpa'
import Button from './Button.vue'
import StatusIndicator from './StatusIndicator.vue'
import GlassCard from './GlassCard.vue'

const { loading, login } = useAuth()
const { mode, toggleTheme } = useTheme()
const { connected } = useWebSocket()
const rpaStore = useRPAStore()

const showInstructions = ref(false)
const showCountdown = ref(false)
const remainingTime = ref(300) // 5 minutes in seconds
let countdownInterval: number | null = null

const wsStatus = computed(() => {
  if (connected.value) return 'connected'
  if (rpaStore.status === 'browser_opened') return 'connecting'
  return 'disconnected'
})

const loginButtonText = computed(() => {
  if (loading.value) return '正在启动浏览器...'
  if (rpaStore.status === 'browser_opened') return '请扫码登录'
  return '登录 BOSS 直聘'
})

const formattedTime = computed(() => {
  const minutes = Math.floor(remainingTime.value / 60)
  const seconds = remainingTime.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

async function handleLogin() {
  const result = await login()
  if (result.success) {
    showInstructions.value = true
    showCountdown.value = true
    startCountdown()
  }
}

function startCountdown() {
  if (countdownInterval) clearInterval(countdownInterval)

  countdownInterval = window.setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      stopCountdown()
      showInstructions.value = false
      showCountdown.value = false
      rpaStore.reset()
    }
  }, 1000)
}

function stopCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
}

onMounted(() => {
  // Reset countdown
  remainingTime.value = 300
})

onUnmounted(() => {
  stopCountdown()
})
</script>
