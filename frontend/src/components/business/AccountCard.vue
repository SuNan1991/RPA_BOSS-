<template>
  <div class="glass-card">
    <div class="flex items-center gap-4">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div
          :class="[
            'w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold',
            'bg-primary text-white'
          ]"
        >
          {{ avatarLetter }}
        </div>
      </div>

      <!-- User Info -->
      <div class="flex-1 min-w-0">
        <h2 class="text-xl font-bold truncate">{{ userName }}</h2>
        <p class="text-text-secondary text-sm mt-1">
          <span class="inline-flex items-center gap-1">
            <span
              :class="[
                'w-2 h-2 rounded-full',
                statusColor
              ]"
            />
            {{ statusText }}
          </span>
        </p>
      </div>

      <!-- Edit Button (Placeholder) -->
      <button
        class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        title="编辑资料 (即将推出)"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
      </button>
    </div>

    <!-- Connection Duration -->
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between text-sm">
        <span class="text-text-secondary">连接时长</span>
        <span class="font-semibold">{{ formattedDuration }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loginTime = ref<Date>(new Date())
const currentTime = ref<Date>(new Date())
let timeUpdateInterval: number | null = null

const userName = computed(() => authStore.userName)

const avatarLetter = computed(() => {
  const name = authStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const statusColor = computed(() => {
  return 'bg-green-500'
})

const statusText = computed(() => {
  return '已连接'
})

const formattedDuration = computed(() => {
  const diff = currentTime.value.getTime() - loginTime.value.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (hours > 0) {
    return `${hours}小时 ${minutes}分`
  } else {
    return `${minutes}分`
  }
})

onMounted(() => {
  loginTime.value = new Date()
  currentTime.value = new Date()

  timeUpdateInterval = window.setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timeUpdateInterval) {
    clearInterval(timeUpdateInterval)
  }
})
</script>
