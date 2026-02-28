<template>
  <div class="candidate-search">
    <GlassCard>
      <h3 class="text-lg font-semibold mb-4">搜索候选人</h3>

      <form @submit.prevent="handleSearch" class="space-y-4">
        <!-- 关键词 -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">职位关键词 *</label>
          <input
            v-model="filters.keyword"
            type="text"
            required
            placeholder="例如: 前端工程师、产品经理"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- 城市和经验 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1">城市</label>
            <select
              v-model="filters.city"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="全国">全国</option>
              <option value="北京">北京</option>
              <option value="上海">上海</option>
              <option value="深圳">深圳</option>
              <option value="杭州">杭州</option>
              <option value="广州">广州</option>
              <option value="成都">成都</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1">工作经验</label>
            <select
              v-model="filters.experience"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">不限</option>
              <option value="应届生">应届生</option>
              <option value="1年以下">1年以下</option>
              <option value="1-3年">1-3年</option>
              <option value="3-5年">3-5年</option>
              <option value="5-10年">5-10年</option>
              <option value="10年以上">10年以上</option>
            </select>
          </div>
        </div>

        <!-- 学历和薪资 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1">学历要求</label>
            <select
              v-model="filters.education"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">不限</option>
              <option value="初中及以下">初中及以下</option>
              <option value="中专/中技">中专/中技</option>
              <option value="高中">高中</option>
              <option value="大专">大专</option>
              <option value="本科">本科</option>
              <option value="硕士">硕士</option>
              <option value="博士">博士</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-text-secondary mb-1">期望薪资</label>
            <select
              v-model="filters.salary"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">不限</option>
              <option value="3K以下">3K以下</option>
              <option value="3-5K">3-5K</option>
              <option value="5-10K">5-10K</option>
              <option value="10-15K">10-15K</option>
              <option value="15-20K">15-20K</option>
              <option value="20-30K">20-30K</option>
              <option value="30-50K">30-50K</option>
              <option value="50K以上">50K以上</option>
            </select>
          </div>
        </div>

        <!-- 搜索按钮 -->
        <Button
          type="submit"
          variant="primary"
          :loading="isSearching"
          class="w-full"
        >
          {{ isSearching ? '搜索中...' : '开始搜索' }}
        </Button>
      </form>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useHRStore } from '@/stores/hr'
import Button from './Button.vue'
import GlassCard from './GlassCard.vue'

const hrStore = useHRStore()

const isSearching = ref(false)
const filters = ref({
  keyword: '',
  city: '全国',
  experience: '',
  education: '',
  salary: '',
  age: '',
  gender: '',
  maxPages: 1
})

async function handleSearch() {
  if (!filters.value.keyword.trim()) {
    return
  }

  isSearching.value = true
  try {
    await hrStore.searchCandidates(filters.value)
  } finally {
    isSearching.value = false
  }
}
</script>
