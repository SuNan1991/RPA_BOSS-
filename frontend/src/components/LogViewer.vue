<template>
  <div class="log-viewer h-full flex flex-col bg-bg-secondary rounded-2xl overflow-hidden">
    <!-- Header -->
    <div class="glass-card p-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold">系统日志</h2>
        <div class="flex items-center gap-2">
          <button
            @click="toggleLiveMode"
            :class="['btn', 'text-sm', liveMode ? 'btn-primary' : 'btn-secondary']"
          >
            {{ liveMode ? '🔴 实时' : '▶️ 暂停' }}
          </button>
          <button @click="clearLogs" class="btn btn-secondary text-sm">
            清空
          </button>
          <button @click="exportLogs" class="btn btn-secondary text-sm">
            导出
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-2 mb-4">
        <select
          v-model="filters.level"
          class="input px-3 py-2 rounded-lg text-sm"
        >
          <option value="">所有级别</option>
          <option value="TRACE">TRACE</option>
          <option value="DEBUG">DEBUG</option>
          <option value="INFO">INFO</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>

        <select
          v-model="filters.module"
          class="input px-3 py-2 rounded-lg text-sm"
        >
          <option value="">所有模块</option>
          <option value="app">app</option>
          <option value="rpa">rpa</option>
          <option value="api">api</option>
        </select>

        <input
          v-model="filters.keyword"
          type="text"
          placeholder="搜索关键词..."
          class="input px-3 py-2 rounded-lg text-sm"
        >

        <select
          v-model="filters.timeRange"
          class="input px-3 py-2 rounded-lg text-sm"
        >
          <option value="1">最近 1 小时</option>
          <option value="6">最近 6 小时</option>
          <option value="24">最近 24 小时</option>
          <option value="168">最近 7 天</option>
        </select>

        <button @click="refreshLogs" class="btn btn-secondary text-sm">
          刷新
        </button>
      </div>
    </div>

    <!-- Log List -->
    <div class="flex-1 overflow-auto p-4">
      <div v-if="logs.length === 0" class="text-center text-text-secondary py-8">
        <LoadingSpinner v-if="loading" />
        <span v-else>暂无日志</span>
      </div>

      <div
        v-else
        class="space-y-1"
        ref="logContainer"
      >
        <div
          v-for="(log, index) in logs"
          :key="index"
          :class="[
            'log-entry p-2 rounded text-sm font-mono cursor-pointer',
            'hover:bg-gray-100 dark:hover:bg-gray-800',
            getLevelClass(log.level)
          ]"
          @click="toggleLogExpand(index)"
        >
          <div class="flex items-start gap-2">
            <!-- Level Badge -->
            <span :class="['level-badge', 'px-2 py-0.5 rounded text-xs font-semibold', getLevelBadgeClass(log.level)]">
              {{ log.level }}
            </span>

            <!-- Timestamp -->
            <span class="text-text-secondary text-xs">
              {{ log.timestamp }}
            </span>

            <!-- Module -->
            <span class="text-primary text-xs font-medium">
              {{ log.module || '-' }}
            </span>

            <!-- Message -->
            <span class="flex-1 break-all">
              {{ log.message }}
            </span>
          </div>

          <!-- Expanded Details -->
          <div v-if="expandedLogs.has(index)" class="mt-2 pl-8 text-xs text-text-secondary">
            <div>函数: {{ log.function_line || '-' }}</div>
            <div v-if="log.exception" class="mt-1 p-2 bg-red-50 dark:bg-red-900/20 rounded">
              <pre class="whitespace-pre-wrap">{{ log.exception }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Stats -->
    <div class="glass-card p-3 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between text-sm text-text-secondary">
        <span>共 {{ logs.length }} 条日志</span>
        <span v-if="stats.connected_clients !== undefined">
          WebSocket: {{ stats.connected_clients }} 客户端连接
        </span>
        <span v-if="liveMode">
          <span class="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          实时接收中...
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import api from '@/api'

interface LogEntry {
  timestamp: string
  level: string
  module?: string
  function_line?: string
  message: string
  exception?: string
}

interface LogStats {
  connected_clients: number
  buffer_size: number
  logs_sent: number
  log_file_count: number
  log_file_size_bytes: number
  log_file_size_mb: number
}

// State
const logs = ref<LogEntry[]>([])
const expandedLogs = ref<Set<number>>(new Set())
const loading = ref(false)
const liveMode = ref(false)
const logContainer = ref<HTMLElement | null>(null)

// Filters
const filters = ref({
  level: '',
  module: '',
  keyword: '',
  timeRange: '1'
})

// Stats
const stats = ref<LogStats>({
  connected_clients: 0,
  buffer_size: 0,
  logs_sent: 0,
  log_file_count: 0,
  log_file_size_bytes: 0,
  log_file_size_mb: 0
})

// WebSocket for live logs
let ws: WebSocket | null = null

// Methods
const toggleLiveMode = async () => {
  liveMode.value = !liveMode.value

  if (liveMode.value) {
    await connectWebSocket()
  } else {
    disconnectWebSocket()
  }
}

const connectWebSocket = async () => {
  try {
    // 使用环境变量或默认值构建 WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const wsHost = apiBaseUrl.replace(/^https?:\/\//, '')
    ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/logs`)

    ws.onopen = () => {
      console.log('Log WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'connected') {
          console.log('Log stream ready')
        } else if (Array.isArray(data)) {
          // Batch of logs
          data.forEach((log: LogEntry) => {
            logs.value.unshift(log)
          })
          // Keep only last 1000 logs in memory
          if (logs.value.length > 1000) {
            logs.value = logs.value.slice(0, 1000)
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket closed, reconnecting in 5s...')
      setTimeout(() => {
        if (liveMode.value) {
          connectWebSocket()
        }
      }, 5000)
    }
  } catch (e) {
    console.error('Failed to connect WebSocket:', e)
    liveMode.value = false
  }
}

const disconnectWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

const refreshLogs = async () => {
  loading.value = true
  try {
    const hours = parseInt(filters.value.timeRange)
    const params = new URLSearchParams()
    params.set('limit', '1000')
    params.set('hours', hours.toString())
    if (filters.value.level) params.set('level', filters.value.level)
    if (filters.value.module) params.set('module', filters.value.module)
    if (filters.value.keyword) params.set('keyword', filters.value.keyword)

    const response = await api.get(`/api/logs?${params}`)
    logs.value = response.data
  } catch (e: any) {
    console.error('Error fetching logs:', e)
  } finally {
    loading.value = false
  }
}

const clearLogs = () => {
  logs.value = []
  expandedLogs.value.clear()
}

const exportLogs = async () => {
  try {
    const hours = parseInt(filters.value.timeRange)
    const params = new URLSearchParams({
      format: 'json',
      hours: hours.toString()
    })

    const response = await api.post(`/api/logs/export?${params}`, {
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `logs_${new Date().toISOString().slice(0, 19)}.json`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (e: any) {
    console.error('Error exporting logs:', e)
  }
}

const toggleLogExpand = (index: number) => {
  if (expandedLogs.value.has(index)) {
    expandedLogs.value.delete(index)
  } else {
    expandedLogs.value.add(index)
  }
}

// Level badge classes
const getLevelClass = (level: string) => {
  const classes: Record<string, string> = {
    'TRACE': 'text-gray-500',
    'DEBUG': 'text-blue-500',
    'INFO': 'text-green-500',
    'SUCCESS': 'text-emerald-500',
    'WARNING': 'text-yellow-500',
    'ERROR': 'text-red-500',
    'CRITICAL': 'text-purple-500'
  }
  return classes[level] || 'text-gray-500'
}

const getLevelBadgeClass = (level: string) => {
  const classes: Record<string, string> = {
    'TRACE': 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    'DEBUG': 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    'INFO': 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    'SUCCESS': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300',
    'WARNING': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    'ERROR': 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    'CRITICAL': 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
  }
  return classes[level] || 'bg-gray-100'
}

// Lifecycle
onMounted(async () => {
  await refreshLogs()
  // Fetch stats
  try {
    const statsResponse = await api.get('/api/logs/stats')
    stats.value = statsResponse.data
  } catch (e) {
    console.error('Error fetching log stats:', e)
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<style scoped>
.log-entry {
  transition: background-color 200ms;
}

.level-badge {
  min-width: 60px;
  text-align: center;
}
</style>
