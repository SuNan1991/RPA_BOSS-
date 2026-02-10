<template>
  <div :class="['glass', 'rounded-2xl', containerClass]">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  containerClass?: string
}

withDefaults(defineProps<Props>(), {
  containerClass: 'p-6'
})
</script>
