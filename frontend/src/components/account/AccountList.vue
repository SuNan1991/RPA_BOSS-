<template>
  <div class="space-y-3">
    <!-- Select All -->
    <div v-if="accounts.length > 0" class="flex items-center gap-2 px-2">
      <input
        type="checkbox"
        :checked="selectedIds.length === accounts.length && accounts.length > 0"
        :indeterminate="selectedIds.length > 0 && selectedIds.length < accounts.length"
        @change="$emit('select-all')"
        class="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
      />
      <span class="text-sm text-text-secondary">全选</span>
    </div>

    <!-- Account Cards -->
    <AccountCard
      v-for="account in accounts"
      :key="account.id"
      :account="account"
      :selected="selectedIds.includes(account.id)"
      :is-active="account.id === activeAccountId"
      :browser-running="browserStatus?.[account.id]"
      :is-restoring-browser="restoringAccountId === account.id"
      @select="$emit('select', $event)"
      @login="$emit('login', $event)"
      @refresh="$emit('refresh', $event)"
      @switch="$emit('switch', $event)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
      @view-detail="$emit('view-detail', $event)"
      @restore-browser="$emit('restore-browser', $event)"
    />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && accounts.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <p class="text-text-secondary">暂无账号</p>
      <p class="text-sm text-text-secondary mt-1">点击上方"添加账号"按钮开始</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import AccountCard from './AccountCard.vue'
import type { HRAccount } from '@/stores/hr'

defineProps<{
  accounts: HRAccount[]
  loading: boolean
  selectedIds: number[]
  activeAccountId: number | null
  browserStatus?: Record<number, boolean>  // 账号ID -> 浏览器是否运行
  restoringAccountId?: number | null  // 正在恢复浏览器的账号ID
}>()

defineEmits<{
  select: [accountId: number]
  'select-all': []
  login: [accountId: number]
  refresh: [accountId: number]
  switch: [accountId: number]
  edit: [accountId: number]
  delete: [accountId: number]
  'view-detail': [accountId: number]
  'restore-browser': [accountId: number]  // 恢复浏览器会话
}>()
</script>
