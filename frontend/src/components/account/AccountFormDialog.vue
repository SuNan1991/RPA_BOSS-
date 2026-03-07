<template>
  <!-- Dialog Overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 z-40 flex items-center justify-center"
    @click.self="handleCancel"
  >
    <!-- Dialog -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4 p-6 max-h-[90vh] overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4">{{ account ? '编辑账号' : '添加账号' }}</h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Phone -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            手机号 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.phone"
            type="tel"
            maxlength="11"
            placeholder="请输入手机号"
            required
            :disabled="!!account"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <p v-if="account" class="text-xs text-text-muted mt-1">手机号不可修改</p>
        </div>

        <!-- Account Type -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            账户类型
          </label>
          <select
            v-model="form.account_type"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="hr">HR账户</option>
            <option value="seeker">求职者账户</option>
          </select>
        </div>

        <!-- Username -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            备注名称
          </label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入备注名称（可选）"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- Group -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            分组
          </label>
          <select
            v-model="form.group_id"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option :value="null">无分组</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            标签
          </label>
          <input
            v-model="tagsInput"
            type="text"
            placeholder="多个标签用逗号分隔"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            备注
          </label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="请输入备注（可选）"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
          ></textarea>
        </div>

        <!-- Tip -->
        <div class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p class="text-sm text-blue-700 dark:text-blue-300">
            {{ account ? '修改后需要重新登录以更新Cookie' : '创建后需要通过扫码登录来获取Cookie' }}
          </p>
        </div>

        <!-- Buttons -->
        <div class="flex justify-end gap-3 pt-2">
          <button
            type="button"
            @click="handleCancel"
            :disabled="loading"
            class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="!isFormValid || loading"
            :class="[
              'px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors',
              (!isFormValid || loading) ? 'opacity-50 cursor-not-allowed' : ''
            ]"
          >
            {{ loading ? '保存中...' : '确认' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  visible: boolean
  account: any | null
  groups: any[]
  loading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  account: null,
  groups: () => [],
  loading: false
})

const emit = defineEmits<{
  save: [data: any]
  'update:visible': [value: boolean]
}>()

const form = ref({
  phone: '',
  account_type: 'hr',
  username: '',
  group_id: null as number | null,
  tags: [] as string[],
  notes: '',
})

const tagsInput = computed({
  get: () => form.value.tags.join(', '),
  set: (value: string) => {
    form.value.tags = value.split(',').map(t => t.trim()).filter(Boolean)
  }
})

const isFormValid = computed(() => {
  return form.value.phone.length >= 11
})

function handleCancel() {
  emit('update:visible', false)
}

function handleSubmit() {
  if (!isFormValid.value) return

  const data: any = {
    phone: form.value.phone,
    account_type: form.value.account_type,
    username: form.value.username || form.value.phone,
    group_id: form.value.group_id,
    tags: form.value.tags.length > 0 ? form.value.tags : undefined,
    notes: form.value.notes || undefined,
  }

  if (props.account) {
    // 编辑模式：不发送手机号
    delete data.phone
  }

  emit('save', data)
}

// 监听对话框打开
watch(() => props.visible, (visible) => {
  if (visible) {
    if (props.account) {
      // 编辑模式：填充现有数据
      form.value = {
        phone: props.account.phone || '',
        account_type: props.account.account_type || 'hr',
        username: props.account.username || '',
        group_id: props.account.group_id || null,
        tags: props.account.tags || [],
        notes: props.account.notes || '',
      }
    } else {
      // 添加模式：重置表单
      form.value = {
        phone: '',
        account_type: 'hr',
        username: '',
        group_id: null,
        tags: [],
        notes: '',
      }
    }
  }
})
</script>
