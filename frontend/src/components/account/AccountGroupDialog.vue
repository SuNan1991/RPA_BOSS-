<template>
  <!-- Dialog Overlay -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 z-40 flex items-center justify-center"
    @click.self="handleCancel"
  >
    <!-- Dialog -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
      <h2 class="text-lg font-semibold mb-4">{{ group ? '编辑分组' : '新建分组' }}</h2>

      <div class="space-y-4">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            分组名称 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.name"
            type="text"
            placeholder="请输入分组名称"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            描述
          </label>
          <textarea
            v-model="form.description"
            placeholder="请输入分组描述（可选）"
            rows="3"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
          ></textarea>
        </div>

        <!-- Parent Group -->
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-1">
            父分组
          </label>
          <select
            v-model="form.parent_id"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option :value="null">无（顶级分组）</option>
            <option
              v-for="g in availableParentGroups"
              :key="g.id"
              :value="g.id"
            >
              {{ g.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <button
          @click="handleCancel"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleSave"
          :disabled="!form.name || loading"
          :class="[
            'px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors',
            (!form.name || loading) ? 'opacity-50 cursor-not-allowed' : ''
          ]"
        >
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  group: any | null
  groups: any[]
  loading: boolean
}>()

const emit = defineEmits<{
  save: [data: { name: string; description?: string; parent_id: number | null }]
  'update:visible': [value: boolean]
}>()

const form = ref({
  name: '',
  description: '',
  parent_id: null as number | null,
})

const availableParentGroups = computed(() => {
  if (!props.group) return props.groups
  // Exclude self and children when editing
  return props.groups.filter(g => g.id !== props.group?.id)
})

function handleCancel() {
  emit('update:visible', false)
}

function handleSave() {
  if (!form.value.name) return

  emit('save', {
    name: form.value.name,
    description: form.value.description || undefined,
    parent_id: form.value.parent_id,
  })
}

// Reset form when dialog opens
watch(() => props.visible, (visible) => {
  if (visible) {
    if (props.group) {
      form.value = {
        name: props.group.name || '',
        description: props.group.description || '',
        parent_id: props.group.parent_id || null,
      }
    } else {
      form.value = {
        name: '',
        description: '',
        parent_id: null,
      }
    }
  }
})
</script>
