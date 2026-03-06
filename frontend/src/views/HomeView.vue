<template>
  <div class="space-y-6">
    <!-- 未登录状态 - 启动区域 -->
    <div v-if="!isAuthenticated" class="login-section">
      <GlassCard class="p-8 text-center">
        <h2 class="text-2xl font-bold mb-4 text-text-primary">欢迎使用 BOSS 直聘助手</h2>
        <p class="text-text-secondary mb-6">点击下方按钮启动 BOSS 网页并扫码登录</p>

        <button
          @click="handleLaunchBrowser"
          :disabled="isLaunching"
          class="launch-button"
        >
          <span v-if="!isLaunching">启动 BOSS 网页</span>
          <span v-else>正在启动...</span>
        </button>

        <!-- 错误提示 -->
        <div v-if="launchError" class="mt-4 text-red-500 text-sm">
          {{ launchError }}
        </div>

        <!-- 登录引导 -->
        <div v-if="browserOpened" class="login-guide mt-8">
          <div class="countdown text-4xl font-bold text-primary mb-4">{{ formatCountdown(countdown) }}</div>
          <p class="text-text-secondary mb-6">请使用 BOSS 直聘 APP 扫码登录</p>
          <div class="steps text-left max-w-sm mx-auto space-y-3">
            <div class="step flex items-center gap-3">
              <span class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm font-medium">1</span>
              <span>打开 BOSS 直聘 APP</span>
            </div>
            <div class="step flex items-center gap-3">
              <span class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm font-medium">2</span>
              <span>点击右上角扫码图标</span>
            </div>
            <div class="step flex items-center gap-3">
              <span class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm font-medium">3</span>
              <span>扫描网页二维码完成登录</span>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>

    <!-- 已登录状态 - 原有内容 -->
    <div v-else>
      <!-- 浏览器状态提示 -->
      <div v-if="!browserRunning" class="mb-6">
        <GlassCard class="p-4 border-l-4 border-yellow-500">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p class="font-medium text-text-primary">浏览器未运行</p>
                <p class="text-sm text-text-secondary">您的登录状态有效，但浏览器未打开。点击"重新连接"恢复会话。</p>
              </div>
            </div>
            <button
              @click="handleRestoreBrowser"
              :disabled="isRestoring"
              class="px-4 py-2 bg-yellow-500 text-white rounded-lg font-medium hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="!isRestoring">重新连接</span>
              <span v-else>连接中...</span>
            </button>
          </div>
        </GlassCard>
      </div>

      <!-- Welcome Section -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-text-primary">欢迎回来, {{ userName }}</h1>
          <p class="text-text-secondary mt-1">这是您的工作概览</p>
        </div>
        <div class="text-sm text-text-secondary">
          {{ currentDate }}
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard class="p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-text-secondary">今日浏览</p>
              <p class="text-2xl font-semibold text-text-primary">{{ stats.todayViewed }}</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard class="p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-text-secondary">已打招呼</p>
              <p class="text-2xl font-semibold text-text-primary">{{ stats.greeted }}</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard class="p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-text-secondary">收到回复</p>
              <p class="text-2xl font-semibold text-text-primary">{{ stats.replied }}</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard class="p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-text-secondary">回复率</p>
              <p class="text-2xl font-semibold text-text-primary">{{ stats.replyRate }}%</p>
            </div>
          </div>
        </GlassCard>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard class="p-6">
          <h3 class="text-lg font-semibold mb-4">快捷操作</h3>
          <div class="space-y-3">
            <router-link
              to="/chat"
              class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium">搜索候选人</p>
                <p class="text-sm text-text-secondary">快速查找符合条件的候选人</p>
              </div>
            </router-link>

            <router-link
              to="/work"
              class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium">管理任务</p>
                <p class="text-sm text-text-secondary">查看和执行自动化任务</p>
              </div>
            </router-link>

            <router-link
              to="/work"
              class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium">回复规则</p>
                <p class="text-sm text-text-secondary">配置自动回复规则</p>
              </div>
            </router-link>
          </div>
        </GlassCard>

        <!-- Recent Activity -->
        <GlassCard class="p-6">
          <h3 class="text-lg font-semibold mb-4">最近活动</h3>
          <div class="space-y-4">
            <div v-for="activity in recentActivities" :key="activity.id" class="flex items-start gap-3">
              <div :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                activity.type === 'greet' ? 'bg-green-100 dark:bg-green-900/30' :
                activity.type === 'reply' ? 'bg-blue-100 dark:bg-blue-900/30' :
                'bg-gray-100 dark:bg-gray-700/30'
              ]">
                <svg v-if="activity.type === 'greet'" class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
                </svg>
                <svg v-else-if="activity.type === 'reply'" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <svg v-else class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ activity.title }}</p>
                <p class="text-xs text-text-secondary">{{ activity.time }}</p>
              </div>
            </div>

            <div v-if="recentActivities.length === 0" class="text-center py-6 text-text-secondary">
              <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p>暂无活动记录</p>
            </div>
          </div>
        </GlassCard>
      </div>

      <!-- System Status -->
      <GlassCard class="p-6">
        <h3 class="text-lg font-semibold mb-4">系统状态</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="flex items-center gap-3">
            <StatusIndicator :status="wsStatus" :show-label="false" />
            <div>
              <p class="text-sm text-text-secondary">连接状态</p>
              <p class="font-medium">{{ wsStatusText }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div :class="[
              'w-2 h-2 rounded-full',
              hrStore.hasActiveSession ? 'bg-green-500' : 'bg-gray-400'
            ]"></div>
            <div>
              <p class="text-sm text-text-secondary">会话状态</p>
              <p class="font-medium">{{ hrStore.hasActiveSession ? '已登录' : '未登录' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div :class="[
              'w-2 h-2 rounded-full',
              rpaStore.status === 'idle' ? 'bg-green-500' : 'bg-yellow-500'
            ]"></div>
            <div>
              <p class="text-sm text-text-secondary">RPA 状态</p>
              <p class="font-medium">{{ rpaStatusText }}</p>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import GlassCard from '@/components/ui/GlassCard.vue'
import StatusIndicator from '@/components/ui/StatusIndicator.vue'
import { useAuthStore } from '@/stores/auth'
import { useHRStore } from '@/stores/hr'
import { useRPAStore } from '@/stores/rpa'
import { useWebSocket } from '@/composables/useWebSocket'
import { useBrowserLaunch } from '@/composables/useBrowserLaunch'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

const authStore = useAuthStore()
const hrStore = useHRStore()
const rpaStore = useRPAStore()
const { connected } = useWebSocket()

// 使用浏览器启动 composable
const { isLaunching, browserOpened, error: launchError, launch: launchBrowser } = useBrowserLaunch()

// 浏览器状态
const browserRunning = ref(false)
const isRestoring = ref(false)

// 倒计时相关
const countdown = ref(300) // 5分钟
let countdownTimer: ReturnType<typeof setInterval> | null = null

// Statistics
const stats = ref({
  todayViewed: 0,
  greeted: 0,
  replied: 0,
  replyRate: 0,
})

// Recent activities
const recentActivities = ref<Array<{
  id: string
  type: 'greet' | 'reply' | 'info'
  title: string
  time: string
}>>([])

// Computed
const userName = computed(() => authStore.userName || '用户')
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日 dddd'))

const wsStatus = computed(() => {
  if (connected.value) return 'connected'
  if (rpaStore.status === 'browser_opened') return 'connecting'
  return 'disconnected'
})

const wsStatusText = computed(() => {
  switch (wsStatus.value) {
    case 'connected': return '已连接'
    case 'connecting': return '连接中'
    default: return '未连接'
  }
})

const rpaStatusText = computed(() => {
  const statusMap: Record<string, string> = {
    idle: '空闲',
    browser_opened: '浏览器已打开',
    waiting_for_login: '等待登录',
    login_successful: '登录成功',
    error: '错误',
    timeout: '超时',
  }
  return statusMap[rpaStore.status] || '未知'
})

// Load data
onMounted(async () => {
  await hrStore.loadStatistics()
  // Update stats from store
  if (hrStore.statistics) {
    stats.value = {
      todayViewed: hrStore.statistics.candidates_viewed || 0,
      greeted: hrStore.statistics.greetings_sent || 0,
      replied: hrStore.statistics.greetings_replied || 0,
      replyRate: hrStore.statistics.reply_rate || 0,
    }
  }

  // 检查浏览器状态
  await checkBrowserStatus()
})

// 检查浏览器状态
async function checkBrowserStatus() {
  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await fetch(`${apiBaseUrl}/api/auth/status`)
    if (response.ok) {
      const status = await response.json()
      browserRunning.value = status.browser_opened || false
    }
  } catch (error) {
    console.error('Failed to check browser status:', error)
    browserRunning.value = false
  }
}

// 重新连接浏览器
async function handleRestoreBrowser() {
  isRestoring.value = true
  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await fetch(`${apiBaseUrl}/api/auth/restore-browser`, {
      method: 'POST'
    })
    if (response.ok) {
      const result = await response.json()
      if (result.browser_opened) {
        browserRunning.value = true
        console.log('Browser restored successfully')
      } else {
        console.warn('Browser restore failed:', result.message)
      }
    }
  } catch (error) {
    console.error('Failed to restore browser:', error)
  } finally {
    isRestoring.value = false
  }
}

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 启动浏览器处理
async function handleLaunchBrowser() {
  await launchBrowser()
  if (browserOpened.value) {
    startCountdown()
  }
}

// 倒计时功能
function startCountdown() {
  stopCountdown() // 清除可能存在的旧定时器
  countdown.value = 300 // 重置为5分钟
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      stopCountdown()
    }
  }, 1000)
}

function stopCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function formatCountdown(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

// 监听登录成功状态变化
watch(() => authStore.isAuthenticated, (newValue) => {
  if (newValue) {
    // 登录成功后停止倒计时
    stopCountdown()
  }
})

// 清理
onUnmounted(() => {
  stopCountdown()
})
</script>

<style scoped>
.launch-button {
  @apply px-8 py-4 bg-primary text-white rounded-lg font-medium text-lg;
  @apply hover:bg-primary/90 active:bg-primary/80;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
  @apply transition-all duration-200;
  @apply shadow-lg hover:shadow-xl;
}

.login-guide {
  @apply bg-primary/5 rounded-lg p-6;
}

.step {
  color: var(--text-secondary);
}
</style>
