<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" @click="close"></div>
    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
      <h2 class="text-xl font-bold mb-4">添加账户</h2>

      <form @submit.prevent="submit">
        <div class="space-y-4">
          <!-- 手机号 -->
          <div>
            <label class="block text-sm font-medium mb-1">手机号 <span class="text-red-500">*</span></label>
            <input
              v-model="form.phone"
              type="tel"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="请输入手机号"
              maxlength="11"
              required
            />
            <p v-if="errors.phone" class="text-red-500 text-xs mt-1">{{ errors.phone }}</p>
          </div>

          <!-- 账户类型 -->
          <div>
            <label class="block text-sm font-medium mb-1">账户类型</label>
            <select
              v-model="form.account_type"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="hr">HR账户</option>
              <option value="seeker">求职者账户</option>
            </select>
          </div>

          <!-- 备注名称 -->
          <div>
            <label class="block text-sm font-medium mb-1">备注名称</label>
            <input
              v-model="form.username"
              type="text"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="方便识别的名称（可选）"
            />
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-blue-700 dark:text-blue-300">
              创建账户后，需要通过扫码或密码登录来获取Cookie
            </p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end gap-3 mt-6">
          <button
            type="button"
            @click="close"
            :disabled="submitting"
            class="btn btn-secondary px-4 py-2"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="btn btn-primary px-4 py-2 flex items-center gap-2"
          >
            <LoadingSpinner v-if="submitting" size="sm" />
            <span>确认</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const emit = defineEmits<{
  success: []
  close: []
}>()

const visible = ref(false)
const submitting = ref(false)

const form = reactive({
  phone: '',
  account_type: 'hr',
  username: ''
})

const errors = reactive({
  phone: ''
})

function validatePhone(): boolean {
  errors.phone = ''

  if (!form.phone) {
    errors.phone = '请输入手机号'
    return false
  }

  // 简单的手机号验证
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(form.phone)) {
    errors.phone = '请输入正确的手机号'
    return false
  }

  return true
}

async function submit() {
  if (!validatePhone()) {
    return
  }

  submitting.value = true
  errors.phone = ''

  try {
    const response = await fetch('/api/accounts/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: form.phone,
        account_type: form.account_type,
        username: form.username || form.phone
      })
    })

    const data = await response.json()

    if (response.ok && data.code === 200) {
      // 成功
      close()
      emit('success')
    } else if (response.status === 400 && data.message?.includes('已注册')) {
      errors.phone = '该手机号已存在'
    } else {
      alert(data.message || '创建账户失败')
    }
  } catch (error) {
    console.error('Failed to create account:', error)
    alert('创建账户失败，请重试')
  } finally {
    submitting.value = false
  }
}

function open() {
  visible.value = true
  // 重置表单
  form.phone = ''
  form.account_type = 'hr'
  form.username = ''
  errors.phone = ''
}

function close() {
  if (!submitting.value) {
    visible.value = false
    emit('close')
  }
}

defineExpose({ open })
</script>
