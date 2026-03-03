<template>
  <div class="account-switcher">
    <div class="relative" ref="dropdownRef">
      <button
        @click="toggleDropdown"
        class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-semibold">
          {{ avatarLetter }}
        </div>
        <span class="font-medium">{{ displayName }}</span>
        <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': isOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Dropdown Menu -->
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
      >
        <div class="p-2">
          <div class="text-xs text-text-secondary uppercase tracking-wide px-2 py-1">
            HR 账户
          </div>
          <div
            v-for="account in hrAccounts"
            :key="account.id"
            @click="selectAccount(account.id)"
            :class="[
              'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors',
              account.id === activeAccountId ? 'bg-primary/10' : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            ]"
          >
            <div class="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-semibold text-sm">
              {{ getAvatarLetter(account) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">{{ account.username || account.phone }}</div>
              <div class="text-xs text-text-secondary flex items-center gap-1">
                <span
                  :class="[
                    'w-1.5 h-1.5 rounded-full',
                    account.cookie_status === 'valid' ? 'bg-green-500' : 'bg-gray-400'
                  ]"
                />
                {{ getStatusText(account) }}
              </div>
            </div>
            <svg v-if="account.id === activeAccountId" class="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>

          <div v-if="hrAccounts.length === 0" class="text-center py-4 text-text-secondary text-sm">
            暂无 HR 账户
          </div>
        </div>

        <div class="border-t border-gray-200 dark:border-gray-700 p-2">
          <button
            @click="openAddDialog"
            class="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加 HR 账户
          </button>
        </div>
      </div>
    </div>

    <!-- 添加账户对话框 -->
    <AddAccountDialog ref="addDialogRef" @success="onAccountAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useHRStore, type HRAccount } from '@/stores/hr'
import AddAccountDialog from '@/components/business/AddAccountDialog.vue'

const hrStore = useHRStore()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const addDialogRef = ref<InstanceType<typeof AddAccountDialog> | null>(null)

const hrAccounts = computed(() => hrStore.hrAccounts)
const activeAccountId = computed(() => hrStore.activeAccountId)
const activeAccount = computed(() => hrStore.activeAccount)

const displayName = computed(() => {
  return activeAccount.value?.username || activeAccount.value?.phone || '选择账户'
})

const avatarLetter = computed(() => {
  if (!activeAccount.value) return '?'
  return getAvatarLetter(activeAccount.value)
})

function getAvatarLetter(account: HRAccount): string {
  const name = account.username || account.phone || '?'
  return name.charAt(0).toUpperCase()
}

function getStatusText(account: HRAccount): string {
  switch (account.cookie_status) {
    case 'valid': return '已登录'
    case 'invalid': return '需重新登录'
    default: return '未登录'
  }
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

async function selectAccount(accountId: number) {
  if (accountId === activeAccountId.value) {
    isOpen.value = false
    return
  }

  const success = await hrStore.switchAccount(accountId)
  if (success) {
    isOpen.value = false
  }
}

function openAddDialog() {
  isOpen.value = false
  addDialogRef.value?.open()
}

async function onAccountAdded() {
  // 刷新账户列表
  await hrStore.loadAccounts()
}

// Close dropdown when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  hrStore.loadAccounts()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
