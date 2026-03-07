<template>
  <!-- Dialog Overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 z-40 flex items-center justify-center"
    @click.self="$emit('cancel')"
  >
    <!-- Dialog -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
      <h2 class="text-lg font-semibold mb-4">{{ title }}</h2>

      <p class="text-text-secondary mb-6">
        {{ message }}
      </p>

      <div class="flex justify-end gap-3">
        <button
          @click="$emit('cancel')"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          取消
        </button>
        <button
          @click="$emit('confirm')"
          :disabled="loading"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            action === 'delete'
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-primary hover:bg-primary-dark text-white',
            loading ? 'opacity-50 cursor-not-allowed' : ''
          ]"
        >
          {{ loading ? '处理中...' : '确认' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  visible: boolean
  action: string
  accountIds: number[]
  loading: boolean
}>()

defineEmits<{
  confirm: []
  cancel: []
}>()

const title = computed(() => {
  switch (props.action) {
    case 'activate':
      return '批量激活'
    case 'deactivate':
      return '批量停用'
    case 'delete':
      return '批量删除'
    case 'refresh_cookies':
      return '批量刷新 Cookie'
    default:
      return '批量操作'
  }
})

const message = computed(() => {
  const count = props.accountIds.length
  switch (props.action) {
    case 'activate':
      return `确定要激活选中的 ${count} 个账号吗？`
    case 'deactivate':
      return `确定要停用选中的 ${count} 个账号吗？`
    case 'delete':
      return `确定要删除选中的 ${count} 个账号吗？此操作不可撤销。`
    case 'refresh_cookies':
      return `确定要重置选中的 ${count} 个账号的 Cookie 状态吗？`
    default:
      return `确定要执行此操作吗？`
  }
})
</script>
