<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-bold text-text-primary">工作设置</h1>
      <p class="text-text-secondary mt-1">配置自动化任务和回复规则</p>
    </div>

    <!-- Settings Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex gap-4 -mb-px overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
            activeTab === tab.key
              ? 'border-primary text-primary'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="mt-6">
      <!-- Tasks Tab -->
      <div v-if="activeTab === 'tasks'">
        <TaskManager />
      </div>

      <!-- Reply Rules Tab -->
      <div v-if="activeTab === 'replies'">
        <ReplyRuleManager />
      </div>

      <!-- Jobs Tab -->
      <div v-if="activeTab === 'jobs'">
        <JobManager />
      </div>

      <!-- Resumes Tab -->
      <div v-if="activeTab === 'resumes'">
        <ResumeManager />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TaskManager from '@/components/business/TaskManager.vue'
import ReplyRuleManager from '@/components/business/ReplyRuleManager.vue'
import JobManager from '@/components/business/JobManager.vue'
import ResumeManager from '@/components/business/ResumeManager.vue'

// Tabs
const tabs = [
  { key: 'tasks', label: '任务管理' },
  { key: 'replies', label: '自动回复' },
  { key: 'jobs', label: '职位管理' },
  { key: 'resumes', label: '简历管理' },
]
const activeTab = ref('tasks')
</script>
