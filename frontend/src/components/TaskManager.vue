<template>
  <GlassCard class="task-manager">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">任务管理</h2>
      <button
        @click="showCreateDialog = true"
        class="btn btn-primary text-sm px-4 py-2"
      >
        <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        创建任务
      </button>
    </div>

    <!-- 任务列表 -->
    <div class="space-y-2">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="flex items-center justify-between p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-colors"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <h3 class="font-semibold">{{ task.name }}</h3>
            <span :class="['px-2 py-0.5 rounded text-xs font-medium', getStatusClass(task.status)]">
              {{ getStatusText(task.status) }}
            </span>
            <span class="text-xs text-text-secondary">
              {{ getTaskTypeText(task.task_type) }}
            </span>
          </div>
          <div class="text-sm text-text-secondary mt-1">
            {{ task.created_at ? formatDate(task.created_at) : '' }}
          </div>
          <div v-if="task.error_message" class="text-sm text-red-500 mt-1">
            {{ task.error_message }}
          </div>
          <div v-if="task.result && task.result.total !== undefined" class="text-sm text-text-secondary mt-1">
            成功: {{ task.result.success || 0 }} | 失败: {{ task.result.failed || 0 }} | 总计: {{ task.result.total || 0 }}
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-if="task.status === 'pending' || task.status === 'failed'"
            @click="executeTask(task.id)"
            :disabled="executing"
            class="btn btn-secondary text-sm px-3 py-1"
          >
            <LoadingSpinner v-if="executing" size="sm" />
            <span v-else>执行</span>
          </button>
          <button
            v-if="task.status === 'running'"
            @click="refreshTask(task.id)"
            class="btn btn-ghost text-sm px-3 py-1"
          >
            <LoadingSpinner size="sm" />
          </button>
          <button
            @click="deleteTask(task.id)"
            class="btn btn-danger text-sm px-3 py-1"
          >
            删除
          </button>
        </div>
      </div>

      <div v-if="tasks.length === 0" class="text-center py-8 text-text-secondary">
        <p>暂无任务</p>
        <button
          @click="showCreateDialog = true"
          class="text-primary hover:underline mt-2"
        >
          创建第一个任务
        </button>
      </div>
    </div>

    <!-- 创建任务对话框 -->
    <div v-if="showCreateDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="showCreateDialog = false"></div>
      <div class="relative bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">创建任务</h2>

        <form @submit.prevent="createTask">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">任务名称</label>
              <input
                v-model="form.name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                placeholder="输入任务名称"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">任务类型</label>
              <select
                v-model="form.task_type"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                required
              >
                <option value="search_candidate">候选人搜索</option>
                <option value="batch_greet">批量打招呼</option>
                <option value="auto_chat">自动聊天</option>
              </select>
            </div>

            <!-- 候选人搜索配置 -->
            <div v-if="form.task_type === 'search_candidate'" class="space-y-3 border-t pt-3">
              <div>
                <label class="block text-sm font-medium mb-1">关键词</label>
                <input
                  v-model="form.config.keyword"
                  type="text"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  placeholder="如: Java开发工程师"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">城市</label>
                <input
                  v-model="form.config.city"
                  type="text"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  placeholder="如: 北京"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">搜索页数</label>
                <input
                  v-model.number="form.config.max_pages"
                  type="number"
                  min="1"
                  max="10"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
            </div>

            <!-- 批量打招呼配置 -->
            <div v-if="form.task_type === 'batch_greet'" class="space-y-3 border-t pt-3">
              <div>
                <label class="block text-sm font-medium mb-1">打招呼模板</label>
                <textarea
                  v-model="form.config.template"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  rows="3"
                  placeholder="留空则使用默认模板"
                ></textarea>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="form.config.auto_execute"
                type="checkbox"
                id="auto_execute"
                class="rounded"
              />
              <label for="auto_execute" class="text-sm">创建后自动执行</label>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button
              type="button"
              @click="showCreateDialog = false"
              class="btn btn-secondary px-4 py-2"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="creating"
              class="btn btn-primary px-4 py-2"
            >
              <LoadingSpinner v-if="creating" size="sm" />
              <span v-else>创建</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

interface Task {
  id: number
  name: string
  task_type: string
  config: Record<string, any>
  status: string
  result?: { success?: number; failed?: number; total?: number }
  error_message?: string
  created_at?: string
}

const tasks = ref<Task[]>([])
const showCreateDialog = ref(false)
const creating = ref(false)
const executing = ref(false)

const form = reactive({
  name: '',
  task_type: 'search_candidate',
  config: {
    keyword: '',
    city: '全国',
    max_pages: 1,
    template: '',
    candidate_ids: [],
    auto_execute: false
  }
})

// 重置表单
function resetForm() {
  form.name = ''
  form.task_type = 'search_candidate'
  form.config = {
    keyword: '',
    city: '全国',
    max_pages: 1,
    template: '',
    candidate_ids: [],
    auto_execute: false
  }
}

// 获取任务列表
async function loadTasks() {
  try {
    const params = new URLSearchParams({
      page: '1',
      page_size: '20'
    })

    const response = await fetch(`/api/tasks/?${params}`)
    const data = await response.json()

    if (data.code === 200) {
      tasks.value = data.data || []
    }
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}

// 创建任务
async function createTask() {
  creating.value = true
  try {
    const response = await fetch('/api/tasks/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name,
        task_type: form.task_type,
        config: form.config
      })
    })

    if (response.ok) {
      showCreateDialog.value = false
      resetForm()
      await loadTasks()
    } else {
      alert('创建任务失败')
    }
  } catch (error) {
    console.error('Failed to create task:', error)
    alert('创建任务失败')
  } finally {
    creating.value = false
  }
}

// 执行任务
async function executeTask(taskId: number) {
  executing.value = true
  try {
    const response = await fetch(`/api/tasks/${taskId}/execute`, {
      method: 'POST'
    })

    if (response.ok) {
      // 刷新任务列表
      setTimeout(async () => {
        await loadTasks()
        executing.value = false
      }, 1000)
    } else {
      alert('执行任务失败')
      executing.value = false
    }
  } catch (error) {
    console.error('Failed to execute task:', error)
    alert('执行任务失败')
    executing.value = false
  }
}

// 刷新任务状态
async function refreshTask(taskId: number) {
  try {
    const response = await fetch(`/api/tasks/${taskId}`)
    const data = await response.json()

    if (data.code === 200) {
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = data.data
      }
    }
  } catch (error) {
    console.error('Failed to refresh task:', error)
  }
}

// 删除任务
async function deleteTask(taskId: number) {
  if (!confirm('确定要删除这个任务吗？')) return

  try {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      await loadTasks()
    } else {
      alert('删除任务失败')
    }
  } catch (error) {
    console.error('Failed to delete task:', error)
    alert('删除任务失败')
  }
}

// 获取状态样式类
function getStatusClass(status: string): string {
  const classes = {
    pending: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    running: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    completed: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    cancelled: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
  }
  return classes[status as keyof typeof classes] || classes.pending
}

// 获取状态文本
function getStatusText(status: string): string {
  const texts = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status as keyof typeof texts] || '未知'
}

// 获取任务类型文本
function getTaskTypeText(type: string): string {
  const texts = {
    search_candidate: '候选人搜索',
    batch_greet: '批量打招呼',
    auto_chat: '自动聊天'
  }
  return texts[type as keyof typeof texts] || type
}

// 格式化日期
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadTasks()
  // 每5秒刷新一次运行中的任务
  setInterval(() => {
    if (tasks.value.some(t => t.status === 'running')) {
      loadTasks()
    }
  }, 5000)
})
</script>
