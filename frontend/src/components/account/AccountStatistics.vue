<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
    <!-- Total Accounts -->
    <GlassCard class="p-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-text-secondary">总账号数</p>
          <p class="text-xl font-bold text-text-primary">
            {{ loading ? '...' : stats?.total_accounts || 0 }}
          </p>
        </div>
      </div>
    </GlassCard>

    <!-- Active Accounts -->
    <GlassCard class="p-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-text-secondary">活跃账号</p>
          <p class="text-xl font-bold text-text-primary">
            {{ loading ? '...' : stats?.active_accounts || 0 }}
          </p>
        </div>
      </div>
    </GlassCard>

    <!-- Valid Cookies -->
    <GlassCard class="p-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-text-secondary">有效 Cookie</p>
          <p class="text-xl font-bold text-text-primary">
            {{ loading ? '...' : stats?.valid_cookies || 0 }}
          </p>
        </div>
      </div>
    </GlassCard>

    <!-- Invalid/None Cookies -->
    <GlassCard class="p-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-text-secondary">待登录</p>
          <p class="text-xl font-bold text-text-primary">
            {{ loading ? '...' : (stats?.none_cookies || 0) + (stats?.invalid_cookies || 0) }}
          </p>
        </div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stats: any
  loading?: boolean
}>()
</script>
