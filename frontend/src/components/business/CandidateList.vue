<template>
  <div class="candidate-list">
    <GlassCard>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">
          候选人列表
          <span class="text-text-secondary font-normal text-sm ml-2">
            (共 {{ candidates.length }} 位)
          </span>
        </h3>

        <div class="flex items-center gap-2">
          <Button
            v-if="selectedCandidates.length > 0"
            variant="primary"
            :loading="isGreeting"
            @click="handleBatchGreet"
          >
            打招呼 ({{ selectedCandidates.length }})
          </Button>
          <Button
            variant="ghost"
            @click="refreshList"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </Button>
        </div>
      </div>

      <!-- 全选 -->
      <div v-if="candidates.length > 0" class="mb-3 flex items-center gap-2">
        <input
          type="checkbox"
          :id="`select-all-${Date.now()}`"
          :checked="isAllSelected"
          @change="toggleSelectAll"
          class="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
        />
        <label :for="`select-all-${Date.now()}`" class="text-sm text-text-secondary">
          全选
        </label>
      </div>

      <!-- 候选人列表 -->
      <div v-if="candidates.length > 0" class="space-y-3">
        <div
          v-for="candidate in candidates"
          :key="candidate.id"
          :class="[
            'p-4 rounded-lg border transition-colors',
            selectedCandidates.includes(candidate.id)
              ? 'border-primary bg-primary/5'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
          ]"
        >
          <div class="flex items-start gap-3">
            <!-- 选择框 -->
            <input
              type="checkbox"
              :id="`candidate-${candidate.id}`"
              :checked="selectedCandidates.includes(candidate.id)"
              @change="toggleCandidate(candidate.id)"
              class="mt-1 w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />

            <!-- 候选人信息 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h4 class="font-semibold">{{ candidate.name }}</h4>
                <span
                  :class="[
                    'text-xs px-2 py-0.5 rounded',
                    candidate.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ getStatusText(candidate.status) }}
                </span>
              </div>

              <div class="mt-1 text-sm text-text-secondary">
                <span v-if="candidate.position">{{ candidate.position }}</span>
                <span v-if="candidate.experience" class="mx-1">·</span>
                <span v-if="candidate.experience">{{ candidate.experience }}</span>
                <span v-if="candidate.education" class="mx-1">·</span>
                <span v-if="candidate.education">{{ candidate.education }}</span>
              </div>

              <div class="mt-1 flex items-center gap-4 text-sm">
                <span v-if="candidate.expected_salary" class="text-primary font-medium">
                  {{ candidate.expected_salary }}
                </span>
                <span v-if="candidate.recent_company" class="text-text-secondary">
                  {{ candidate.recent_company }}
                </span>
              </div>

              <div v-if="candidate.skills" class="mt-2 flex flex-wrap gap-1">
                <span
                  v-for="(skill, idx) in candidate.skills.split(',').slice(0, 3)"
                  :key="idx"
                  class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded"
                >
                  {{ skill.trim() }}
                </span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex items-center gap-1">
              <button
                @click="greetSingle(candidate.id)"
                class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="打招呼"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </button>
              <a
                v-if="candidate.profile_url"
                :href="candidate.profile_url"
                target="_blank"
                class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="查看详情"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-8 text-text-secondary">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p>暂无候选人</p>
        <p class="text-sm mt-1">请先进行候选人搜索</p>
      </div>
    </GlassCard>

    <!-- 打招呼模板选择 -->
    <div v-if="showTemplateDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">选择打招呼模板</h3>
        <div class="space-y-2 mb-4">
          <label
            v-for="(template, idx) in greetTemplates"
            :key="idx"
            :class="[
              'flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
              selectedTemplate === idx
                ? 'border-primary bg-primary/5'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
            ]"
          >
            <input
              type="radio"
              :name="`greet-template-${Date.now()}`"
              :value="idx"
              v-model="selectedTemplate"
              class="mt-1"
            />
            <span class="text-sm">{{ template }}</span>
          </label>
        </div>
        <div class="flex gap-2">
          <Button variant="ghost" @click="showTemplateDialog = false">取消</Button>
          <Button variant="primary" @click="confirmGreet">确定</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useHRStore } from '@/stores/hr'
import Button from '@/components/ui/Button.vue'
import GlassCard from '@/components/ui/GlassCard.vue'

const hrStore = useHRStore()

const candidates = computed(() => hrStore.candidates)
const isGreeting = ref(false)
const selectedCandidates = ref<number[]>([])
const showTemplateDialog = ref(false)
const selectedTemplate = ref(0)
const greetTemplates = [
  '您好，看了您的简历觉得很匹配，方便沟通一下吗？',
  '您好，我们这边有合适的职位，了解一下？',
  '您好，看到您的经验很丰富，想和您聊聊',
  '您好，看了您的背景很不错，期待与您进一步交流'
]

const isAllSelected = computed(() => {
  return candidates.value.length > 0 && selectedCandidates.value.length === candidates.value.length
})

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    active: '活跃',
    contacted: '已联系',
    interviewed: '面试中',
    hired: '已录用',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

function toggleCandidate(id: number) {
  const index = selectedCandidates.value.indexOf(id)
  if (index > -1) {
    selectedCandidates.value.splice(index, 1)
  } else {
    selectedCandidates.value.push(id)
  }
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedCandidates.value = []
  } else {
    selectedCandidates.value = candidates.value.map(c => c.id)
  }
}

async function greetSingle(id: number) {
  selectedCandidates.value = [id]
  showTemplateDialog.value = true
}

async function handleBatchGreet() {
  if (selectedCandidates.value.length === 0) return
  showTemplateDialog.value = true
}

async function confirmGreet() {
  const template = greetTemplates[selectedTemplate.value]
  isGreeting.value = true

  try {
    await hrStore.batchGreet(selectedCandidates.value, template, {
      max_per_hour: 30,
      min_delay: 3,
      max_delay: 8
    })
    selectedCandidates.value = []
    showTemplateDialog.value = false
  } finally {
    isGreeting.value = false
  }
}

function refreshList() {
  hrStore.loadCandidates()
}
</script>
