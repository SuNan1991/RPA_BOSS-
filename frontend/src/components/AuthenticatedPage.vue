<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <GlassCard class="max-w-2xl w-full">
      <!-- Header with Theme Toggle -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-primary">BOSS 直聘 RPA 助手</h1>
          <p class="text-text-secondary mt-2">已登录</p>
        </div>
        <div class="flex items-center gap-4">
          <StatusIndicator :status="wsStatus" show-label />
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
      </div>

      <!-- Account Information Card -->
      <AccountCard />

      <!-- Connection Info -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="glass-card">
          <h3 class="text-sm font-semibold text-text-secondary mb-2">连接时长</h3>
          <p class="text-2xl font-bold text-primary">{{ connectionDuration }}</p>
        </div>
        <div class="glass-card">
          <h3 class="text-sm font-semibold text-text-secondary mb-2">最后登录</h3>
          <p class="text-lg">{{ lastLoginTime }}</p>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="mt-8 text-center">
        <Button
          variant="danger"
          :loading="loading"
          @click="handleLogout"
        >
          退出登录
        </Button>
      </div>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { useWebSocket } from '@/composables/useWebSocket'
import Button from './ui/Button.vue'
import StatusIndicator from './ui/StatusIndicator.vue'
import AccountCard from './business/AccountCard.vue'
import GlassCard from './ui/GlassCard.vue'

const { loading, logout } = useAuth()
const { mode, toggleTheme } = useTheme()
const { connected } = useWebSocket()

const loginTime = ref<Date>(new Date())
const currentTime = ref<Date>(new Date())
let timeUpdateInterval: number | null = null

const wsStatus = computed(() => {
  if (connected.value) return 'connected'
  return 'disconnected'
})

const connectionDuration = computed(() => {
  const diff = currentTime.value.getTime() - loginTime.value.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  if (hours > 0) {
    return `${hours}小时 ${minutes}分 ${seconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分 ${seconds}秒`
  } else {
    return `${seconds}秒`
  }
})

const lastLoginTime = computed(() => {
  return loginTime.value.toLocaleString('zh-CN')
})

async function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    const result = await logout()
    if (result.success) {
      // Auth store will be cleared by logout composable
    }
  }
}

onMounted(() => {
  loginTime.value = new Date()
  currentTime.value = new Date()

  timeUpdateInterval = window.setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timeUpdateInterval) {
    clearInterval(timeUpdateInterval)
  }
})
</script>
