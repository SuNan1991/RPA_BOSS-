/**
 * HR Store - Manage HR functionality state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// HR 账户接口
export interface HRAccount {
  id: number
  phone: string
  username?: string
  cookie_status: 'none' | 'valid' | 'invalid'
  is_active: boolean
  group_id?: number
  tags?: string[]
  notes?: string
  login_count?: number
  last_login?: string
  last_operation_at?: string
  quota_limit?: number
  quota_used?: number
  created_at: string
  updated_at: string
}

// 账户分组接口
export interface AccountGroup {
  id: number
  name: string
  description?: string
  parent_id?: number
  account_count?: number
  created_at: string
  updated_at: string
}

// 账户统计接口
export interface AccountStatistics {
  total_accounts: number
  active_accounts: number
  valid_cookies: number
  invalid_cookies: number
  none_cookies: number
}

// 候选人接口
export interface Candidate {
  id: number
  name: string
  position?: string
  experience?: string
  education?: string
  expected_salary?: string
  recent_company?: string
  skills?: string
  profile_url: string
  status: 'active' | 'contacted' | 'interviewed' | 'hired' | 'rejected'
  hr_account_id: number
  created_at: string
  updated_at: string
}

// 统计数据接口
export interface HRStatistics {
  candidates_viewed: number
  greetings_sent: number
  greetings_replied: number
  reply_rate: number
  days: number
}

// 打招呼配置接口
export interface GreetConfig {
  max_per_hour?: number
  min_delay?: number
  max_delay?: number
}

export const useHRStore = defineStore('hr', () => {
  // State
  const hrAccounts = ref<HRAccount[]>([])
  const activeAccountId = ref<number | null>(null)
  const candidates = ref<Candidate[]>([])
  const statistics = ref<HRStatistics | null>(null)
  const isSearching = ref(false)
  const isGreeting = ref(false)
  const error = ref<string | null>(null)

  // New state for account management
  const accountGroups = ref<AccountGroup[]>([])
  const accountStatistics = ref<AccountStatistics | null>(null)
  const accountFilters = ref({
    search: '',
    group_id: null as number | null,
    cookie_status: null as string | null,
  })
  const selectedAccountIds = ref<number[]>([])

  // Getters
  const activeAccount = computed(() =>
    hrAccounts.value.find(acc => acc.id === activeAccountId.value)
  )

  const hasActiveSession = computed(() =>
    activeAccount.value?.cookie_status === 'valid'
  )

  const candidateCount = computed(() => candidates.value.length)

  // Actions
  async function loadAccounts() {
    try {
      const response = await fetch('/api/hr/accounts')
      const result = await response.json()

      if (result.code === 200) {
        hrAccounts.value = result.data

        // 如果没有活跃账户且有账户列表，设置第一个为活跃
        if (!activeAccountId.value && hrAccounts.value.length > 0) {
          // 尝试获取服务端记录的活跃账户
          const activeResponse = await fetch('/api/hr/accounts/active')
          const activeResult = await activeResponse.json()
          if (activeResult.code === 200 && activeResult.data) {
            activeAccountId.value = activeResult.data.id
          }
        }
      }
    } catch (e: any) {
      console.error('Error loading HR accounts:', e)
      error.value = e.message
    }
  }

  async function switchAccount(accountId: number) {
    try {
      const response = await fetch(`/api/auth/accounts/${accountId}/switch`, {
        method: 'POST'
      })
      const result = await response.json()

      if (result.status === 'success') {
        activeAccountId.value = accountId
        // 重新加载候选人列表
        await loadCandidates()
        return true
      }
      return false
    } catch (e: any) {
      console.error('Error switching account:', e)
      error.value = e.message
      return false
    }
  }

  async function searchCandidates(filters: {
    keyword: string
    city?: string
    experience?: string
    education?: string
    salary?: string
    age?: string
    gender?: string
    maxPages?: number
  }) {
    isSearching.value = true
    error.value = null

    try {
      const response = await fetch('/api/hr/candidates/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: filters.keyword,
          city: filters.city || '全国',
          experience: filters.experience,
          education: filters.education,
          salary: filters.salary,
          age: filters.age,
          gender: filters.gender,
          max_pages: filters.maxPages || 1
        })
      })
      const result = await response.json()

      if (result.code === 200) {
        // 等待一段时间让后台任务完成
        await new Promise(resolve => setTimeout(resolve, 3000))
        // 加载候选人列表
        await loadCandidates()
        return true
      }
      error.value = result.message
      return false
    } catch (e: any) {
      console.error('Error searching candidates:', e)
      error.value = e.message
      return false
    } finally {
      isSearching.value = false
    }
  }

  async function loadCandidates(status?: string, page = 1, pageSize = 20) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      })
      if (status) {
        params.append('status', status)
      }

      const response = await fetch(`/api/hr/candidates?${params}`)
      const result = await response.json()

      if (result.code === 200) {
        candidates.value = result.data || []
      }
    } catch (e: any) {
      console.error('Error loading candidates:', e)
      error.value = e.message
    }
  }

  async function batchGreet(
    candidateIds: number[],
    template?: string,
    config?: GreetConfig
  ) {
    isGreeting.value = true
    error.value = null

    try {
      // 获取候选人数据
      const candidatesData = candidates.value
        .filter(c => candidateIds.includes(c.id))
        .map(c => ({
          id: c.id,
          profile_url: c.profile_url,
          name: c.name
        }))

      const response = await fetch('/api/hr/greetings/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_ids: candidateIds,
          candidates_data: candidatesData,
          template,
          rate_limit: config
        })
      })
      const result = await response.json()

      return result
    } catch (e: any) {
      console.error('Error in batch greet:', e)
      error.value = e.message
      return { success: false, message: e.message }
    } finally {
      isGreeting.value = false
    }
  }

  async function loadStatistics(days = 7) {
    try {
      const response = await fetch(`/api/hr/statistics?days=${days}`)
      const result = await response.json()

      if (result.code === 200) {
        statistics.value = result.data
      }
    } catch (e: any) {
      console.error('Error loading statistics:', e)
      error.value = e.message
    }
  }

  function clearError() {
    error.value = null
  }

  function reset() {
    hrAccounts.value = []
    activeAccountId.value = null
    candidates.value = []
    statistics.value = null
    isSearching.value = false
    isGreeting.value = false
    error.value = null
    accountGroups.value = []
    accountStatistics.value = null
    selectedAccountIds.value = []
  }

  // New methods for account management
  async function loadAccountGroups() {
    try {
      const response = await fetch('/api/account-groups/')
      const result = await response.json()
      if (result.code === 200) {
        accountGroups.value = result.data
      }
    } catch (e: any) {
      console.error('Error loading account groups:', e)
    }
  }

  async function loadAccountStatistics() {
    try {
      const response = await fetch('/api/accounts/statistics/overview')
      const result = await response.json()
      if (result.code === 200) {
        accountStatistics.value = result.data
      }
    } catch (e: any) {
      console.error('Error loading account statistics:', e)
    }
  }

  async function batchOperation(action: string, accountIds: number[]) {
    try {
      const response = await fetch('/api/accounts/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, account_ids: accountIds }),
      })
      const result = await response.json()
      if (result.code === 200) {
        // Reload accounts after batch operation
        await loadAccounts()
        await loadAccountStatistics()
        return result.data
      }
      return null
    } catch (e: any) {
      console.error('Error in batch operation:', e)
      return null
    }
  }

  async function updateAccountTags(accountId: number, tags: string[]) {
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags }),
      })
      return response.ok
    } catch (e: any) {
      console.error('Error updating account tags:', e)
      return false
    }
  }

  async function updateAccountGroup(accountId: number, groupId: number | null) {
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group_id: groupId }),
      })
      return response.ok
    } catch (e: any) {
      console.error('Error updating account group:', e)
      return false
    }
  }

  return {
    // State
    hrAccounts,
    activeAccountId,
    activeAccount,
    hasActiveSession,
    candidates,
    statistics,
    isSearching,
    isGreeting,
    error,
    candidateCount,

    // New state
    accountGroups,
    accountStatistics,
    accountFilters,
    selectedAccountIds,

    // Actions
    loadAccounts,
    switchAccount,
    searchCandidates,
    loadCandidates,
    batchGreet,
    loadStatistics,
    clearError,
    reset,

    // New actions
    loadAccountGroups,
    loadAccountStatistics,
    batchOperation,
    updateAccountTags,
    updateAccountGroup,
  }
})
