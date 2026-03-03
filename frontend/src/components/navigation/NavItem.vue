<template>
  <router-link
    :to="item.path"
    custom
    v-slot="{ href, navigate, isActive }"
  >
    <a
      :href="href"
      @click="navigate"
      :class="[
        'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
        'group relative',
        isActive
          ? 'bg-primary/10 text-primary font-medium'
          : 'text-text-secondary hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-text-primary',
      ]"
      :title="collapsed ? item.label : ''"
    >
      <!-- Icon -->
      <component :is="getIcon(item.icon)" class="w-5 h-5 flex-shrink-0" />

      <!-- Label -->
      <span
        v-show="!collapsed"
        class="transition-opacity duration-200 whitespace-nowrap"
      >
        {{ item.label }}
      </span>

      <!-- Active Indicator -->
      <span
        v-if="isActive"
        class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-full"
      ></span>
    </a>
  </router-link>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue'
import type { NavItem as NavItemType } from '@/router/routes'

interface Props {
  item: NavItemType
  collapsed: boolean
}

defineProps<Props>()

// Icon components as render functions
const icons: Record<string, ReturnType<typeof defineComponent>> = {
  home: defineComponent({
    render: () =>
      h('svg', {
        fill: 'none',
        stroke: 'currentColor',
        viewBox: '0 0 24 24',
        class: 'w-5 h-5',
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
        }),
      ]),
  }),
  settings: defineComponent({
    render: () =>
      h('svg', {
        fill: 'none',
        stroke: 'currentColor',
        viewBox: '0 0 24 24',
        class: 'w-5 h-5',
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
        }),
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z',
        }),
      ]),
  }),
  work: defineComponent({
    render: () =>
      h('svg', {
        fill: 'none',
        stroke: 'currentColor',
        viewBox: '0 0 24 24',
        class: 'w-5 h-5',
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
        }),
      ]),
  }),
  chat: defineComponent({
    render: () =>
      h('svg', {
        fill: 'none',
        stroke: 'currentColor',
        viewBox: '0 0 24 24',
        class: 'w-5 h-5',
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
        }),
      ]),
  }),
}

function getIcon(name: string) {
  return icons[name] || icons.home
}
</script>
