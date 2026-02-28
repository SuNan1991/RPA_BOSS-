<template>
  <div class="hr-dashboard min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">HR 招聘助手</h1>
        <p class="text-text-secondary mt-1">管理候选人、批量打招呼、查看统计</p>
      </div>
      <div class="flex items-center gap-4">
        <AccountSwitcher />
        <button
          @click="toggleTheme"
          class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          <svg v-if="mode === 'light'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="statistics" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <GlassCard>
        <div class="text-center">
          <div class="text-3xl font-bold text-primary">{{ statistics.candidates_viewed }}</div>
          <div class="text-sm text-text-secondary mt-1">浏览候选人</div>
        </div>
      </GlassCard>
      <GlassCard>
        <div class="text-center">
          <div class="text-3xl font-bold text-green-500">{{ statistics.greetings_sent }}</div>
          <div class="text-sm text-text-secondary mt-1">已打招呼</div>
        </div>
      </GlassCard>
      <GlassCard>
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-500">{{ statistics.greetings_replied }}</div>
          <div class="text-sm text-text-secondary mt-1">收到回复</div>
        </div>
      </GlassCard>
      <GlassCard>
        <div class="text-center">
          <div class="text-3xl font-bold text-purple-500">{{ statistics.reply_rate }}%</div>
          <div class="text-sm text-text-secondary mt-1">回复率</div>
        </div>
      </GlassCard>
    </div>

    <!-- 检查登录状态 -->
    <div v-if="!hasActiveSession" class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
      <div class="flex items-center gap-3">
        <svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <h3 class="font-semibold text-yellow-800 dark:text-yellow-200">未登录 HR 账户</h3>
          <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
            请先登录 HR 账户才能使用招聘功能
          </p>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：搜索 -->
      <div class="lg:col-span-1">
        <CandidateSearch />
      </div>

      <!-- 右侧：候选人列表 -->
      <div class="lg:col-span-2">
        <CandidateList />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useHRStore } from '@/stores/hr'
import { useTheme } from '@/composables/useTheme'
import AccountSwitcher from '@/components/AccountSwitcher.vue'
import CandidateSearch from '@/components/CandidateSearch.vue'
import CandidateList from '@/components/CandidateList.vue'
import GlassCard from '@/components/GlassCard.vue'

const hrStore = useHRStore()
const { mode, toggleTheme } = useTheme()

const statistics = computed(() => hrStore.statistics)
const hasActiveSession = computed(() => hrStore.hasActiveSession)

onMounted(async () => {
  await hrStore.loadAccounts()
  await hrStore.loadStatistics()
  await hrStore.loadCandidates()
})
</script>
