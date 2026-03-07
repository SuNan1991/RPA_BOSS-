<template>
  <div class="account-management">
    <!-- Statistics Overview -->
    <AccountStatistics :stats="accountStatistics" :loading="statsLoading" />

    <!-- Toolbar -->
    <AccountToolbar
      v-model:search="searchQuery"
      v-model:selectedGroup="selectedGroup"
      v-model:selectedStatus="selectedStatus"
      :groups="accountGroups"
      :selected-count="selectedAccountIds.length"
      @batch-action="handleBatchAction"
      @add-account="openAddDialog"
      @refresh="loadData"
      @detect-duplicates="handleDetectDuplicates"
    />

    <div class="flex gap-4 mt-4">
      <!-- Left: Group Tree -->
      <div class="w-64 flex-shrink-0 hidden md:block">
        <AccountGroupTree
          :groups="accountGroups"
          :selected-group="selectedGroup"
          :loading="groupsLoading"
          @select="handleGroupSelect"
          @create="openCreateGroupDialog"
          @edit="openEditGroupDialog"
          @delete="handleDeleteGroup"
        />
      </div>

      <!-- Right: Account List -->
      <div class="flex-1">
        <AccountList
          :accounts="filteredAccounts"
          :loading="accountsLoading"
          :selected-ids="selectedAccountIds"
          :active-account-id="hrStore.activeAccountId"
          :browser-status="browserStatus"
          :restoring-account-id="restoringAccountId"
          @select="handleAccountSelect"
          @select-all="handleSelectAll"
          @login="handleLogin"
          @refresh="handleRefresh"
          @switch="handleSwitch"
          @edit="openEditDialog"
          @delete="handleDelete"
          @view-detail="openDetailDrawer"
          @restore-browser="handleRestoreBrowser"
        />
      </div>
    </div>

    <!-- Detail Drawer -->
    <AccountDetailDrawer
      v-model:visible="detailDrawerVisible"
      :account-id="selectedAccountId"
    />

    <!-- Batch Operation Dialog -->
    <BatchOperationDialog
      v-model:visible="batchDialogVisible"
      :action="batchAction"
      :account-ids="selectedAccountIds"
      :loading="batchLoading"
      @confirm="executeBatchAction"
      @cancel="batchDialogVisible = false"
    />

    <!-- Create/Edit Group Dialog -->
    <AccountGroupDialog
      v-model:visible="groupDialogVisible"
      :group="editingGroup"
      :groups="accountGroups"
      :loading="groupDialogLoading"
      @save="handleSaveGroup"
    />

    <!-- Account Form Dialog -->
    <AccountFormDialog
      v-model:visible="accountFormVisible"
      :account="editingAccount"
      :groups="accountGroups"
      :loading="accountFormLoading"
      @save="handleSaveAccount"
    />

    <!-- Account Merge Dialog -->
    <AccountMergeDialog
      v-model:visible="mergeDialogVisible"
      :duplicates="duplicateGroups"
      :accounts="hrStore.hrAccounts"
      :loading="mergeLoading"
      @merge="handleMerge"
      @detect="handleDetectDuplicates"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useHRStore } from '@/stores/hr'
import { useToast } from '@/composables/useToast'
import { useAccountLogin } from '@/composables/useAccountLogin'
import AccountStatistics from './AccountStatistics.vue'
import AccountToolbar from './AccountToolbar.vue'
import AccountGroupTree from './AccountGroupTree.vue'
import AccountList from './AccountList.vue'
import AccountDetailDrawer from './AccountDetailDrawer.vue'
import BatchOperationDialog from './BatchOperationDialog.vue'
import AccountGroupDialog from './AccountGroupDialog.vue'
import AccountFormDialog from './AccountFormDialog.vue'
import AccountMergeDialog from './AccountMergeDialog.vue'

const hrStore = useHRStore()
const toast = useToast()
const { loginAccount } = useAccountLogin()

// State
const searchQuery = ref('')
const selectedGroup = ref<number | null>(null)
const selectedStatus = ref<string | null>(null)
const selectedAccountIds = ref<number[]>([])
const accountStatistics = ref<any>(null)
const accountGroups = ref<any[]>([])
const accountsLoading = ref(false)
const statsLoading = ref(false)
const groupsLoading = ref(false)

// Account form dialog state
const accountFormVisible = ref(false)
const editingAccount = ref<any>(null)
const accountFormLoading = ref(false)

// Merge dialog state
const mergeDialogVisible = ref(false)
const duplicateGroups = ref<any[]>([])
const mergeLoading = ref(false)

// Browser restore state
const browserStatus = ref<Record<number, boolean>>({})
const restoringAccountId = ref<number | null>(null)

// Dialogs
const detailDrawerVisible = ref(false)
const batchDialogVisible = ref(false)
const groupDialogVisible = ref(false)
const batchAction = ref('')
const batchLoading = ref(false)
const groupDialogLoading = ref(false)
const editingGroup = ref<any>(null)
const selectedAccountId = ref<number | null>(null)

// Computed
const filteredAccounts = computed(() => {
  let accounts = hrStore.hrAccounts

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    accounts = accounts.filter(
      (acc) =>
        acc.username?.toLowerCase().includes(query) ||
        acc.phone.includes(query)
    )
  }

  // Filter by group
  if (selectedGroup.value !== null) {
    accounts = accounts.filter((acc) => acc.group_id === selectedGroup.value)
  }

  // Filter by status
  if (selectedStatus.value) {
    accounts = accounts.filter((acc) => acc.cookie_status === selectedStatus.value)
  }

  return accounts
})

// Methods
async function loadData() {
  accountsLoading.value = true
  try {
    await Promise.all([
      loadAccounts(),
      loadStatistics(),
      loadGroups(),
    ])
  } finally {
    accountsLoading.value = false
  }
}

async function loadAccounts() {
  await hrStore.loadAccounts()
}

async function loadStatistics() {
  statsLoading.value = true
  try {
    const response = await fetch('/api/accounts/statistics/overview')
    const result = await response.json()
    if (result.code === 200) {
      accountStatistics.value = result.data
    }
  } catch (e) {
    console.error('Error loading statistics:', e)
  } finally {
    statsLoading.value = false
  }
}

async function loadGroups() {
  groupsLoading.value = true
  try {
    const response = await fetch('/api/account-groups/')
    const result = await response.json()
    if (result.code === 200) {
      accountGroups.value = result.data
    }
  } catch (e) {
    console.error('Error loading groups:', e)
  } finally {
    groupsLoading.value = false
  }
}

function handleAccountSelect(accountId: number) {
  const index = selectedAccountIds.value.indexOf(accountId)
  if (index > -1) {
    selectedAccountIds.value.splice(index, 1)
  } else {
    selectedAccountIds.value.push(accountId)
  }
}

function handleSelectAll() {
  if (selectedAccountIds.value.length === filteredAccounts.value.length) {
    selectedAccountIds.value = []
  } else {
    selectedAccountIds.value = filteredAccounts.value.map((acc) => acc.id)
  }
}

function handleGroupSelect(groupId: number | null) {
  selectedGroup.value = groupId
}

function handleBatchAction(action: string) {
  batchAction.value = action
  batchDialogVisible.value = true
}

async function executeBatchAction() {
  batchLoading.value = true
  try {
    const response = await fetch('/api/accounts/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: batchAction.value,
        account_ids: selectedAccountIds.value,
      }),
    })
    const result = await response.json()
    if (result.code === 200) {
      selectedAccountIds.value = []
      batchDialogVisible.value = false
      await loadData()
    }
  } catch (e) {
    console.error('Batch operation failed:', e)
  } finally {
    batchLoading.value = false
  }
}

async function handleLogin(accountId: number) {
  try {
    const result = await loginAccount(accountId)

    if (result.success) {
      toast.success(result.message || '登录已启动，请在浏览器中扫码登录')
      // 登录成功后会由 WebSocket 事件自动刷新列表
    } else {
      toast.error(result.message || '登录启动失败')
    }
  } catch (e: any) {
    console.error('Login error:', e)
    toast.error(e.message || '登录出错，请重试')
  }
}

async function handleRefresh(accountId: number) {
  try {
    const response = await fetch(`/api/accounts/${accountId}/refresh-cookie`, {
      method: 'POST',
    })
    if (response.ok) {
      await loadAccounts()
    }
  } catch (e) {
    console.error('Refresh failed:', e)
  }
}

async function handleSwitch(accountId: number) {
  await hrStore.switchAccount(accountId)
}

async function handleRestoreBrowser(accountId: number) {
  restoringAccountId.value = accountId
  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await fetch(`${apiBaseUrl}/api/auth/accounts/${accountId}/restore-browser`, {
      method: 'POST'
    })

    if (response.ok) {
      const result = await response.json()
      if (result.browser_opened) {
        browserStatus.value[accountId] = true
        toast.success('浏览器会话已恢复')
        await loadAccounts()
      } else {
        toast.error(result.message || '恢复失败')
      }
    } else {
      const errorData = await response.json()
      toast.error(errorData.detail || '恢复失败，请重试')
    }
  } catch (e: any) {
    console.error('Restore browser error:', e)
    toast.error(e.message || '恢复失败，请重试')
  } finally {
    restoringAccountId.value = null
  }
}

function openAddDialog() {
  editingAccount.value = null
  accountFormVisible.value = true
}

function openEditDialog(accountId: number) {
  const account = hrStore.hrAccounts.find(a => a.id === accountId)
  editingAccount.value = account || null
  accountFormVisible.value = true
}

function openDetailDrawer(accountId: number) {
  selectedAccountId.value = accountId
  detailDrawerVisible.value = true
}

async function handleDelete(accountId: number) {
  if (confirm('确定要删除这个账号吗？此操作不可撤销。')) {
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        await loadAccounts()
        await loadStatistics()
      }
    } catch (e) {
      console.error('Delete failed:', e)
    }
  }
}

function openCreateGroupDialog() {
  editingGroup.value = null
  groupDialogVisible.value = true
}

function openEditGroupDialog(group: any) {
  editingGroup.value = group
  groupDialogVisible.value = true
}

async function handleSaveGroup(groupData: any) {
  groupDialogLoading.value = true
  try {
    const url = editingGroup.value
      ? `/api/account-groups/${editingGroup.value.id}`
      : '/api/account-groups/'
    const method = editingGroup.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(groupData),
    })

    if (response.ok) {
      groupDialogVisible.value = false
      await loadGroups()
    }
  } catch (e) {
    console.error('Save group failed:', e)
  } finally {
    groupDialogLoading.value = false
  }
}

async function handleSaveAccount(accountData: any) {
  accountFormLoading.value = true
  try {
    const url = editingAccount.value
      ? `/api/accounts/${editingAccount.value.id}`
      : '/api/accounts/'
    const method = editingAccount.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(accountData),
    })

    const result = await response.json()
    if (result.code === 200) {
      accountFormVisible.value = false
      await loadAccounts()
      await loadStatistics()
      toast.success(editingAccount.value ? '账号已更新' : '账号已创建')
    } else {
      toast.error(result.message || '保存失败')
    }
  } catch (e) {
    console.error('Save account failed:', e)
    toast.error('保存失败，请重试')
  } finally {
    accountFormLoading.value = false
  }
}

async function handleDeleteGroup(groupId: number) {
  if (confirm('确定要删除这个分组吗？分组下的账号将移至无分组状态。')) {
    try {
      const response = await fetch(`/api/account-groups/${groupId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        if (selectedGroup.value === groupId) {
          selectedGroup.value = null
        }
        await loadGroups()
      }
    } catch (e) {
      console.error('Delete group failed:', e)
    }
  }
}

async function handleDetectDuplicates() {
  mergeLoading.value = true
  try {
    const response = await fetch('/api/accounts/duplicates')
    const result = await response.json()
    if (result.code === 200) {
      duplicateGroups.value = result.data.duplicates || []
      mergeDialogVisible.value = true
    } else {
      toast.error(result.message || '检测重复失败')
    }
  } catch (e) {
    console.error('Detect duplicates failed:', e)
    toast.error('检测重复失败，请重试')
  } finally {
    mergeLoading.value = false
  }
}

async function handleMerge(sourceId: number, targetId: number, strategy: string) {
  try {
    const response = await fetch(`/api/accounts/${sourceId}/merge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_id: targetId,
        strategy: strategy
      }),
    })
    const result = await response.json()
    if (result.code === 200) {
      toast.success('账号合并成功')
    } else {
      toast.error(result.message || '合并失败')
    }
  } catch (e) {
    console.error('Merge failed:', e)
    toast.error('合并失败，请重试')
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>
