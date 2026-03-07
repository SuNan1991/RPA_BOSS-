<template>
  <GlassCard class="p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            :value="search"
            @input="$emit('update:search', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="搜索账号（手机号/用户名）"
            class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-2">
        <!-- Group Filter -->
        <select
          :value="selectedGroup"
          @change="$emit('update:selectedGroup', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
          class="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option :value="null">全部分组</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }}
          </option>
        </select>

        <!-- Status Filter -->
        <select
          :value="selectedStatus"
          @change="$emit('update:selectedStatus', ($event.target as HTMLSelectElement).value || null)"
          class="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option :value="null">全部状态</option>
          <option value="valid">有效</option>
          <option value="invalid">无效</option>
          <option value="none">未登录</option>
        </select>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- Batch Actions -->
        <div v-if="selectedCount > 0" class="flex items-center gap-2">
          <span class="text-sm text-text-secondary">已选 {{ selectedCount }} 项</span>
          <button
            @click="$emit('batch-action', 'activate')"
            class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            批量激活
          </button>
          <button
            @click="$emit('batch-action', 'deactivate')"
            class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            批量停用
          </button>
          <button
            @click="$emit('batch-action', 'delete')"
            class="px-3 py-1.5 text-sm rounded-lg border border-red-300 dark:border-red-700 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            批量删除
          </button>
        </div>

        <!-- Detect Duplicates Button -->
        <button
          @click="$emit('detect-duplicates')"
          class="px-3 py-2 rounded-lg border border-orange-300 dark:border-orange-700 text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors flex items-center gap-2"
          title="检测重复账号"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          检测重复
        </button>

        <!-- Refresh Button -->
        <button
          @click="$emit('refresh')"
          class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="刷新"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <!-- Add Account Button -->
        <button
          @click="$emit('add-account')"
          class="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加账号
        </button>
      </div>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
defineProps<{
  search: string
  selectedGroup: number | null
  selectedStatus: string | null
  groups: any[]
  selectedCount: number
}>()

defineEmits<{
  'update:search': [value: string]
  'update:selectedGroup': [value: number | null]
  'update:selectedStatus': [value: string | null]
  'batch-action': [action: string]
  'add-account': []
  'refresh': []
  'detect-duplicates': []
}>()
</script>
