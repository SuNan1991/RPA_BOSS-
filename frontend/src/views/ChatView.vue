<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-text-primary">人选沟通</h1>
        <p class="text-text-secondary mt-1">搜索候选人并开始沟通</p>
      </div>
      <button
        @click="handleBatchGreet"
        :disabled="selectedCandidates.length === 0 || hrStore.isGreeting"
        class="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <svg v-if="!hrStore.isGreeting" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
        </svg>
        <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ hrStore.isGreeting ? '打招呼中...' : `批量打招呼 (${selectedCandidates.length})` }}
      </button>
    </div>

    <!-- Search Section -->
    <GlassCard class="p-4">
      <div class="flex items-center gap-4">
        <div class="flex-1">
          <CandidateSearch />
        </div>
      </div>
    </GlassCard>

    <!-- Candidates List -->
    <GlassCard class="p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">候选人列表</h2>
        <div class="flex items-center gap-2">
          <span class="text-sm text-text-secondary">
            已选 {{ selectedCandidates.length }} / 共 {{ hrStore.candidates.length }} 人
          </span>
          <button
            v-if="selectedCandidates.length > 0"
            @click="clearSelection"
            class="px-3 py-1 text-sm rounded-lg text-text-secondary hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            清空选择
          </button>
        </div>
      </div>

      <!-- Selection Info Bar -->
      <div
        v-if="selectedCandidates.length > 0"
        class="mb-4 p-3 bg-primary/10 dark:bg-primary/20 rounded-lg flex items-center justify-between"
      >
        <span class="text-sm text-primary">
          已选择 {{ selectedCandidates.length }} 位候选人
        </span>
        <button
          @click="handleBatchGreet"
          :disabled="hrStore.isGreeting"
          class="px-4 py-1.5 text-sm rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors disabled:opacity-50"
        >
          开始打招呼
        </button>
      </div>

      <CandidateList
        :candidates="hrStore.candidates"
        :loading="hrStore.isSearching"
        @select="handleCandidateSelect"
      />
    </GlassCard>

    <!-- Empty State -->
    <GlassCard
      v-if="hrStore.candidates.length === 0 && !hrStore.isSearching"
      class="p-12 text-center"
    >
      <svg class="w-16 h-16 mx-auto mb-4 text-text-secondary opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <h3 class="text-lg font-medium mb-2">暂无候选人</h3>
      <p class="text-text-secondary">使用上方搜索功能查找合适的候选人</p>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import GlassCard from '@/components/ui/GlassCard.vue'
import CandidateSearch from '@/components/business/CandidateSearch.vue'
import CandidateList from '@/components/business/CandidateList.vue'
import { useHRStore } from '@/stores/hr'
import { useToast } from '@/composables/useToast'

const hrStore = useHRStore()
const toast = useToast()

const selectedCandidates = ref<number[]>([])

// Methods
function handleCandidateSelect(candidateId: number, selected: boolean) {
  if (selected) {
    if (!selectedCandidates.value.includes(candidateId)) {
      selectedCandidates.value.push(candidateId)
    }
  } else {
    selectedCandidates.value = selectedCandidates.value.filter(id => id !== candidateId)
  }
}

function clearSelection() {
  selectedCandidates.value = []
}

async function handleBatchGreet() {
  if (selectedCandidates.value.length === 0) {
    toast.warning('请先选择候选人')
    return
  }

  try {
    const result = await hrStore.batchGreet(selectedCandidates.value)
    if (result.success) {
      toast.success(`已向 ${selectedCandidates.value.length} 位候选人打招呼`)
      clearSelection()
    } else {
      toast.error(result.message || '打招呼失败')
    }
  } catch (error) {
    toast.error('操作失败，请重试')
  }
}

// Load candidates on mount
onMounted(() => {
  if (hrStore.candidates.length === 0) {
    // Optionally load initial candidates
  }
})
</script>
