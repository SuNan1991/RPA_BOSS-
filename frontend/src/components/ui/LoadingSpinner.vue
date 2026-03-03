<template>
  <div :class="['flex items-center justify-center', containerClass]">
    <div
      :class="[
        'border-4 border-primary border-t-transparent rounded-full',
        'animate-spin',
        sizeClasses
      ]"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
  containerClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  containerClass: ''
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }
  return sizes[props.size]
})
</script>
