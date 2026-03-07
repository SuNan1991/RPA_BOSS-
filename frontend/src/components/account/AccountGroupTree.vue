<template>
  <GlassCard class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-text-primary">分组管理</h3>
      <button
        @click="$emit('create')"
        class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="新建分组"
      >
        <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
    </div>

    <!-- Group List -->
    <div v-else class="space-y-1">
      <!-- All Accounts -->
      <button
        @click="$emit('select', null)"
        :class="[
          'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
          selectedGroup === null
            ? 'bg-primary/10 text-primary'
            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-text-primary'
        ]"
      >
        <span>全部账号</span>
        <span class="text-xs text-text-secondary">{{ totalAccountCount }}</span>
      </button>

      <!-- Groups -->
      <div v-for="group in groups" :key="group.id">
        <button
          @click="$emit('select', group.id)"
          :class="[
            'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors group',
            selectedGroup === group.id
              ? 'bg-primary/10 text-primary'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-text-primary'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            {{ group.name }}
          </span>
          <span class="flex items-center gap-1">
            <span class="text-xs text-text-secondary">{{ group.account_count || 0 }}</span>
            <span
              class="opacity-0 group-hover:opacity-100 flex gap-0.5 transition-opacity"
            >
              <button
                @click.stop="$emit('edit', group)"
                class="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                title="编辑"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click.stop="$emit('delete', group.id)"
                class="p-0.5 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500 rounded"
                title="删除"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </span>
          </span>
        </button>
      </div>

      <!-- Empty -->
      <div v-if="groups.length === 0" class="text-center py-4 text-sm text-text-secondary">
        <p>暂无分组</p>
      </div>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  groups: any[]
  selectedGroup: number | null
  loading: boolean
}>()

defineEmits<{
  select: [groupId: number | null]
  create: []
  edit: [group: any]
  delete: [groupId: number]
}>()

const totalAccountCount = computed(() => {
  return props.groups.reduce((sum, g) => sum + (g.account_count || 0), 0)
})
</script>
