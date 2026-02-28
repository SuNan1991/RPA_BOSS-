<template>
  <GlassCard class="job-manager">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">职位管理</h2>
      <button
        @click="showCreateDialog = true"
        class="btn btn-primary text-sm px-4 py-2"
      >
        <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        发布职位
      </button>
    </div>

    <!-- 职位列表 -->
    <div class="space-y-2">
      <div
        v-for="job in jobs"
        :key="job.id"
        class="flex items-center justify-between p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-colors"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <h3 class="font-semibold">{{ job.job_name }}</h3>
            <span :class="['px-2 py-0.5 rounded text-xs font-medium', getStatusClass(job.status)]">
              {{ getStatusText(job.status) }}
            </span>
            <span v-if="job.department" class="text-sm text-text-secondary">
              {{ job.department }}
            </span>
          </div>

          <div class="flex items-center gap-4 mt-2 text-sm text-text-secondary">
            <span v-if="job.salary_range">薪资: {{ job.salary_range }}</span>
            <span v-if="job.experience_requirement">经验: {{ job.experience_requirement }}</span>
            <span v-if="job.education_requirement">学历: {{ job.education_requirement }}</span>
          </div>

          <div class="flex items-center gap-4 mt-2 text-xs text-text-secondary">
            <span>浏览: {{ job.view_count || 0 }}</span>
            <span>申请: {{ job.applicant_count || 0 }}</span>
            <span>刷新: {{ job.refresh_count || 0 }}次</span>
            <span v-if="job.published_at">
              发布于 {{ formatDate(job.published_at) }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="refreshJob(job.id)"
            :disabled="refreshing"
            class="btn btn-secondary text-sm px-3 py-1"
          >
            <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新
          </button>
          <select
            :value="job.status"
            @change="updateJobStatus(job.id, $event)"
            class="px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 text-xs"
          >
            <option value="active">招聘中</option>
            <option value="paused">暂停</option>
            <option value="closed">关闭</option>
          </select>
        </div>
      </div>

      <div v-if="jobs.length === 0" class="text-center py-8 text-text-secondary">
        <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p>暂无职位</p>
        <button
          @click="showCreateDialog = true"
          class="text-primary hover:underline mt-2"
        >
          发布第一个职位
        </button>
      </div>
    </div>

    <!-- 发布职位对话框 -->
    <div v-if="showCreateDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="showCreateDialog = false"></div>
      <div class="relative bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">发布职位</h2>

        <form @submit.prevent="createJob">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">职位名称 <span class="text-red-500">*</span></label>
              <input
                v-model="form.job_name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                placeholder="如: Java开发工程师"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">部门</label>
              <input
                v-model="form.department"
                type="text"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                placeholder="如: 技术部"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">薪资范围</label>
                <input
                  v-model="form.salary_range"
                  type="text"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  placeholder="如: 15-25K"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">工作年限</label>
                <select
                  v-model="form.experience_requirement"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                >
                  <option value="">不限</option>
                  <option value="应届生">应届生</option>
                  <option value="1年以下">1年以下</option>
                  <option value="1-3年">1-3年</option>
                  <option value="3-5年">3-5年</option>
                  <option value="5-10年">5-10年</option>
                  <option value="10年以上">10年以上</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">学历要求</label>
              <select
                v-model="form.education_requirement"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
              >
                <option value="">不限</option>
                <option value="初中及以下">初中及以下</option>
                <option value="中专/中技">中专/中技</option>
                <option value="高中">高中</option>
                <option value="大专">大专</option>
                <option value="本科">本科</option>
                <option value="硕士">硕士</option>
                <option value="博士">博士</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">职位描述</label>
              <textarea
                v-model="form.description"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                rows="4"
                placeholder="请输入职位描述、职责等..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">任职要求</label>
              <textarea
                v-model="form.requirements"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                rows="3"
                placeholder="请输入任职要求..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">福利待遇</label>
              <textarea
                v-model="form.benefits"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                rows="2"
                placeholder="如: 五险一金、年终奖、带薪年假..."
              ></textarea>
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
              <span v-else>发布</span>
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

interface Job {
  id: number
  hr_account_id: number
  job_name: string
  department: string
  salary_range: string
  experience_requirement: string
  education_requirement: string
  description: string
  requirements: string
  benefits: string
  status: string
  boss_job_id: string
  refresh_count: number
  view_count: number
  applicant_count: number
  published_at: string
  created_at: string
}

const jobs = ref<Job[]>([])
const showCreateDialog = ref(false)
const creating = ref(false)
const refreshing = ref(false)

const form = reactive({
  job_name: '',
  department: '',
  salary_range: '',
  experience_requirement: '',
  education_requirement: '',
  description: '',
  requirements: '',
  benefits: ''
})

async function loadJobs() {
  try {
    const response = await fetch('/api/hr/jobs')
    const data = await response.json()
    if (data.code === 200) {
      jobs.value = data.data || []
    }
  } catch (error) {
    console.error('Failed to load jobs:', error)
  }
}

async function createJob() {
  creating.value = true
  try {
    const params = new URLSearchParams()
    Object.entries(form).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })

    const response = await fetch(`/api/hr/jobs?${params}`, {
      method: 'POST'
    })

    if (response.ok) {
      showCreateDialog.value = false
      resetForm()
      await loadJobs()
    } else {
      alert('发布失败')
    }
  } catch (error) {
    console.error('Failed to create job:', error)
    alert('发布失败')
  } finally {
    creating.value = false
  }
}

async function refreshJob(jobId: number) {
  refreshing.value = true
  try {
    const response = await fetch(`/api/hr/jobs/${jobId}/refresh`, {
      method: 'POST'
    })

    if (response.ok) {
      await loadJobs()
    } else {
      alert('刷新失败')
    }
  } catch (error) {
    console.error('Failed to refresh job:', error)
    alert('刷新失败')
  } finally {
    refreshing.value = false
  }
}

async function updateJobStatus(jobId: number, event: Event) {
  const newStatus = (event.target as HTMLSelectElement).value
  try {
    const response = await fetch(`/api/hr/jobs/${jobId}/status?status=${newStatus}`, {
      method: 'PUT'
    })

    if (response.ok) {
      await loadJobs()
    }
  } catch (error) {
    console.error('Failed to update job status:', error)
  }
}

function resetForm() {
  form.job_name = ''
  form.department = ''
  form.salary_range = ''
  form.experience_requirement = ''
  form.education_requirement = ''
  form.description = ''
  form.requirements = ''
  form.benefits = ''
}

function getStatusClass(status: string): string {
  const classes = {
    active: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    paused: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    closed: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
  return classes[status as keyof typeof classes] || classes.active
}

function getStatusText(status: string): string {
  const texts = {
    active: '招聘中',
    paused: '暂停',
    closed: '关闭'
  }
  return texts[status as keyof typeof texts] || status
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadJobs()
})
</script>
