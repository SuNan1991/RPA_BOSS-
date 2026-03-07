<template>
  <!-- Dialog Overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center"
    @click.self="handleCancel"
  >
    <!-- Dialog -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold">检测到重复账号</h2>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
          共发现 {{ duplicates.length }} 组重复账号
        </p>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        <!-- Empty State -->
        <div v-if="duplicates.length === 0" class="text-center py-8 text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>未检测到重复账号</p>
        </div>

        <!-- Duplicate Groups -->
        <div
          v-for="(group, index) in duplicates"
          :key="`${group.type}-${group.value}`"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <span class="font-medium text-gray-900 dark:text-gray-100">
                {{ group.type === 'phone' ? '手机号' : '用户名' }}重复
              </span>
              <span class="text-gray-500 dark:text-gray-400 ml-2">{{ group.value }}</span>
            </div>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ group.count }} 个账号
            </span>
          </div>

          <!-- Accounts in this group -->
          <div class="space-y-2 mb-3">
            <div
              v-for="accountId in group.account_ids"
              :key="accountId"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <input
                  type="radio"
                  :name="`group-${group.type}-${group.value}`"
                  :checked="selectedTargets[`${group.type}-${group.value}`] === accountId"
                  @change="selectTarget(group, accountId)"
                  class="w-4 h-4 text-primary focus:ring-primary border-gray-300"
                />
                <div>
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    {{ getAccount(accountId)?.username || '未命名' }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ getAccount(accountId)?.phone || '无手机号' }}
                  </div>
                </div>
              </div>
              <div class="text-sm">
                <span
                  :class="
                    getAccount(accountId)?.cookie_status === 'valid'
                      ? 'text-green-600'
                      : 'text-red-600'
                  "
                >
                  {{ getAccount(accountId)?.cookie_status === 'valid' ? '有效' : '无效' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Merge Strategy -->
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500 dark:text-gray-400">合并策略：</span>
            <select
              v-model="strategies[`${group.type}-${group.value}`]"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="keep_target">保留目标账号</option>
              <option value="keep_source">保留源账号</option>
              <option value="keep_newer">保留更新的账号</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between">
        <button
          @click="handleCancel"
          :disabled="loading"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          取消
        </button>
        <div class="flex gap-3">
          <button
            v-if="duplicates.length > 0"
            @click="handleDetect"
            :disabled="loading"
            class="px-4 py-2 rounded-lg border border-primary text-primary hover:bg-primary hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            重新检测
          </button>
          <button
            @click="handleMergeAll"
            :disabled="loading || duplicates.length === 0"
            class="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? '合并中...' : '合并所有' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface DuplicateGroup {
  type: string // 'phone' | 'username'
  value: string
  account_ids: number[]
  count: number
}

interface Props {
  visible: boolean
  duplicates: DuplicateGroup[]
  accounts: any[]
  loading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  duplicates: () => [],
  accounts: () => [],
  loading: false
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  merge: [sourceId: number, targetId: number, strategy: string]
  detect: []
}>()

const selectedTargets = ref<Record<string, number>>({})
const strategies = ref<Record<string, string>>({})

function selectTarget(group: DuplicateGroup, accountId: number) {
  const key = `${group.type}-${group.value}`
  selectedTargets.value[key] = accountId
}

function getAccount(accountId: number) {
  return props.accounts.find((a) => a.id === accountId)
}

async function handleMergeAll() {
  // Validate all groups have selected targets
  for (const group of props.duplicates) {
    const key = `${group.type}-${group.value}`
    if (!selectedTargets.value[key]) {
      alert(`请为"${group.type === 'phone' ? '手机号' : '用户名'}: ${group.value}"选择要保留的账号`)
      return
    }
  }

  // Execute merge for each group
  for (const group of props.duplicates) {
    const key = `${group.type}-${group.value}`
    const targetId = selectedTargets.value[key]
    const strategy = strategies.value[key] || 'keep_target'

    for (const sourceId of group.account_ids) {
      if (sourceId !== targetId) {
        emit('merge', sourceId, targetId, strategy)
      }
    }
  }

  emit('update:visible', false)
}

function handleCancel() {
  emit('update:visible', false)
}

function handleDetect() {
  emit('detect')
}
</script>
