<template>
  <!-- Drawer Overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 z-40"
    @click="$emit('update:visible', false)"
  ></div>

  <!-- Drawer -->
  <div
    :class="[
      'fixed top-0 right-0 h-full w-full md:w-96 bg-white dark:bg-gray-800 shadow-xl z-50 transform transition-transform duration-300',
      visible ? 'translate-x-0' : 'translate-x-full'
    ]"
  >
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <div v-else-if="account" class="h-full flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">账号详情</h2>
          <button
            @click="$emit('update:visible', false)"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4 space-y-6">
        <!-- Basic Info -->
        <div>
          <h3 class="text-sm font-medium text-text-secondary mb-2">基本信息</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-text-secondary">用户名</span>
              <span class="font-medium">{{ account.username || '未设置' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">手机号</span>
              <span class="font-medium">{{ account.phone }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">状态</span>
              <span :class="statusClass">{{ statusText }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">登录次数</span>
              <span class="font-medium">{{ account.login_count || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Group & Tags -->
        <div>
          <h3 class="text-sm font-medium text-text-secondary mb-2">分组和标签</h3>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-text-secondary">分组</span>
              <span class="font-medium">{{ groupName || '未分组' }}</span>
            </div>
            <div class="flex justify-between items-start">
              <span class="text-text-secondary">标签</span>
              <div v-if="account.tags && account.tags.length > 0" class="flex flex-wrap gap-1">
                <span
                  v-for="tag in account.tags"
                  :key="tag"
                  class="px-2 py-0.5 text-xs rounded bg-gray-100 dark:bg-gray-700"
                >
                  {{ tag }}
                </span>
              </div>
              <span v-else class="text-text-secondary">无标签</span>
            </div>
          </div>
        </div>

        <!-- Quota -->
        <div>
          <h3 class="text-sm font-medium text-text-secondary mb-2">配额使用</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-text-secondary">今日已用</span>
              <span class="font-medium">{{ account.quota_used || 0 }} / {{ account.quota_limit || 100 }}</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                class="bg-primary h-2 rounded-full transition-all"
                :style="{ width: quotaPercentage + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Timestamps -->
        <div>
          <h3 class="text-sm font-medium text-text-secondary mb-2">时间信息</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-text-secondary">创建时间</span>
              <span>{{ formatDateTime(account.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">最后登录</span>
              <span>{{ account.last_login ? formatDateTime(account.last_login) : '从未' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">最后操作</span>
              <span>{{ account.last_operation_at ? formatDateTime(account.last_operation_at) : '从未' }}</span>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div v-if="account.notes">
          <h3 class="text-sm font-medium text-text-secondary mb-2">备注</h3>
          <p class="text-sm bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">{{ account.notes }}</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="handleClose"
          class="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  accountId: number | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const account = ref<any>(null)
const loading = ref(false)
const groups = ref<any[]>([])

const statusClass = computed(() => {
  switch (account.value?.cookie_status) {
    case 'valid':
      return 'text-green-500'
    case 'invalid':
      return 'text-red-500'
    default:
      return 'text-gray-500'
  }
})

const statusText = computed(() => {
  switch (account.value?.cookie_status) {
    case 'valid':
      return '有效'
    case 'invalid':
      return '无效'
    default:
      return '未登录'
  }
})

const groupName = computed(() => {
  if (!account.value?.group_id) return null
  const group = groups.value.find(g => g.id === account.value.group_id)
  return group?.name
})

const quotaPercentage = computed(() => {
  if (!account.value) return 0
  const used = account.value.quota_used || 0
  const limit = account.value.quota_limit || 100
  return Math.min((used / limit) * 100, 100)
})

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function handleClose() {
  emit('update:visible', false)
}

async function loadAccountDetail() {
  if (!props.accountId) return

  loading.value = true
  try {
    const [accountRes, groupsRes] = await Promise.all([
      fetch(`/api/accounts/${props.accountId}`),
      fetch('/api/account-groups/')
    ])

    const accountResult = await accountRes.json()
    const groupsResult = await groupsRes.json()

    if (accountResult.code === 200) {
      account.value = accountResult.data
    }
    if (groupsResult.code === 200) {
      groups.value = groupsResult.data
    }
  } catch (e) {
    console.error('Error loading account detail:', e)
  } finally {
    loading.value = false
  }
}

watch(() => props.visible, (visible) => {
  if (visible && props.accountId) {
    loadAccountDetail()
  }
})
</script>
