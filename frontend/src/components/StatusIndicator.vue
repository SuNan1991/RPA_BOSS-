<template>
  <div
    :class="['flex items-center gap-2', containerClass]"
    :title="tooltip"
  >
    <div
      :class="[
        'w-3 h-3 rounded-full transition-all duration-300',
        statusClasses,
        { 'animate-pulse': status === 'connected' }
      ]"
    />
    <span v-if="showLabel" class="text-sm">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  status: 'connected' | 'disconnected' | 'connecting'
  showLabel?: boolean
  containerClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: false,
  containerClass: ''
})

const statusClasses = computed(() => {
  const classes = {
    connected: 'bg-green-500 shadow-lg shadow-green-500/50',
    disconnected: 'bg-red-500',
    connecting: 'bg-primary animate-spin'
  }
  return classes[props.status]
})

const tooltip = computed(() => {
  const tooltips = {
    connected: '连接正常',
    disconnected: '连接断开',
    connecting: '正在连接...'
  }
  return tooltips[props.status]
})

const label = computed(() => {
  const labels = {
    connected: '已连接',
    disconnected: '未连接',
    connecting: '连接中...'
  }
  return labels[props.status]
})
</script>
