<template>
  <GlassCard class="resume-manager">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">收到的简历</h2>
      <div class="flex items-center gap-2">
        <select
          v-model="filterStatus"
          class="px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 text-sm"
          @change="loadResumes"
        >
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="contacted">已联系</option>
          <option value="rejected">已拒绝</option>
          <option value="hired">已录用</option>
        </select>
        <button
          @click="syncResumes"
          :disabled="syncing"
          class="btn btn-secondary text-sm px-3 py-2"
        >
          <LoadingSpinner v-if="syncing" size="sm" />
          <span v-else>同步</span>
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div v-if="statistics" class="grid grid-cols-4 gap-3 mb-4">
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-2xl font-bold text-primary">{{ statistics.total || 0 }}</div>
        <div class="text-xs text-text-secondary">总计</div>
      </div>
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-2xl font-bold text-green-500">{{ statistics.today_count || 0 }}</div>
        <div class="text-xs text-text-secondary">今日新增</div>
      </div>
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-2xl font-bold text-yellow-500">{{ statistics.by_status?.pending || 0 }}</div>
        <div class="text-xs text-text-secondary">待处理</div>
      </div>
      <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-2xl font-bold text-blue-500">{{ statistics.by_status?.contacted || 0 }}</div>
        <div class="text-xs text-text-secondary">已联系</div>
      </div>
    </div>

    <!-- 简历列表 -->
    <div class="space-y-2">
      <div
        v-for="resume in resumes"
        :key="resume.id"
        class="flex items-center justify-between p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-colors"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <span class="font-medium">候选人 #{{ resume.candidate_id }}</span>
            <span :class="['px-2 py-0.5 rounded text-xs font-medium', getStatusClass(resume.status)]">
              {{ getStatusText(resume.status) }}
            </span>
            <span v-if="resume.match_score" class="text-xs text-text-secondary">
              匹配度: {{ (resume.match_score * 100).toFixed(0) }}%
            </span>
          </div>
          <div class="text-sm text-text-secondary mt-1">
            {{ formatDate(resume.received_at) }}
          </div>
          <div v-if="resume.notes" class="text-sm text-text-secondary mt-1">
            备注: {{ resume.notes }}
          </div>
        </div>

        <div class="flex items-center gap-2">
          <select
            :value="resume.status"
            @change="updateStatus(resume.id, $event)"
            class="px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 text-xs"
          >
            <option value="pending">待处理</option>
            <option value="contacted">已联系</option>
            <option value="rejected">已拒绝</option>
            <option value="hired">已录用</option>
          </select>
          <button
            @click="downloadResume(resume.id)"
            class="btn btn-ghost text-sm px-2 py-1"
          >
            下载
          </button>
        </div>
      </div>

      <div v-if="resumes.length === 0" class="text-center py-8 text-text-secondary">
        <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>暂无收到的简历</p>
        <button
          @click="syncResumes"
          class="text-primary hover:underline mt-2"
        >
          同步简历
        </button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-4">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary text-sm px-3 py-1"
      >
        上一页
      </button>
      <span class="text-sm text-text-secondary">
        第 {{ currentPage }} / {{ totalPages }} 页
      </span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary text-sm px-3 py-1"
      >
        下一页
      </button>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import GlassCard from '@/components/ui/GlassCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

interface Resume {
  id: number
  hr_job_id: number
  candidate_id: number
  resume_url: string
  status: string
  match_score: number
  notes: string
  received_at: string
  updated_at: string
}

const resumes = ref<Resume[]>([])
const statistics = ref<any>(null)
const filterStatus = ref('')
const syncing = ref(false)

const currentPage = ref(1)
const pageSize = 10
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize))

async function loadResumes() {
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.toString()
    })

    if (filterStatus.value) {
      params.append('status', filterStatus.value)
    }

    const response = await fetch(`/api/hr/resumes/?${params}`)
    const data = await response.json()

    if (data.code === 200) {
      resumes.value = data.data || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('Failed to load resumes:', error)
  }
}

async function loadStatistics() {
  try {
    const response = await fetch('/api/hr/resumes/statistics/summary')
    const data = await response.json()

    if (data.code === 200) {
      statistics.value = data.data
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

async function updateStatus(resumeId: number, event: Event) {
  const newStatus = (event.target as HTMLSelectElement).value
  try {
    const response = await fetch(`/api/hr/resumes/${resumeId}/status?status=${newStatus}`, {
      method: 'PUT'
    })

    if (response.ok) {
      await loadResumes()
      await loadStatistics()
    }
  } catch (error) {
    console.error('Failed to update status:', error)
  }
}

async function downloadResume(resumeId: number) {
  try {
    const response = await fetch(`/api/hr/resumes/${resumeId}/download`)
    const data = await response.json()

    if (data.code === 200 && data.data?.resume_url) {
      window.open(data.data.resume_url, '_blank')
    } else {
      alert('简历下载功能需要通过RPA模块实现')
    }
  } catch (error) {
    console.error('Failed to download resume:', error)
  }
}

async function syncResumes() {
  syncing.value = true
  try {
    const response = await fetch('/api/hr/resumes/sync', {
      method: 'POST'
    })

    if (response.ok) {
      await loadResumes()
      await loadStatistics()
    }
  } catch (error) {
    console.error('Failed to sync resumes:', error)
  } finally {
    syncing.value = false
  }
}

function changePage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadResumes()
  }
}

function getStatusClass(status: string): string {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    contacted: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    rejected: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    hired: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
  }
  return classes[status as keyof typeof classes] || classes.pending
}

function getStatusText(status: string): string {
  const texts = {
    pending: '待处理',
    contacted: '已联系',
    rejected: '已拒绝',
    hired: '已录用'
  }
  return texts[status as keyof typeof texts] || status
}

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
  loadResumes()
  loadStatistics()
})
</script>
