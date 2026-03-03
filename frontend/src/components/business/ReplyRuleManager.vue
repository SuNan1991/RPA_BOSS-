<template>
  <GlassCard class="reply-rule-manager">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">自动回复规则</h2>
      <button
        @click="showCreateDialog = true"
        class="btn btn-primary text-sm px-4 py-2"
      >
        <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        创建规则
      </button>
    </div>

    <!-- 规则列表 -->
    <div class="space-y-2">
      <div
        v-for="rule in rules"
        :key="rule.id"
        :class="[
          'p-4 rounded-lg border transition-colors',
          rule.is_active
            ? 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
            : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-60'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <h3 class="font-semibold">规则 #{{ rule.id }}</h3>
              <span :class="['px-2 py-0.5 rounded text-xs font-medium', rule.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300']">
                {{ rule.is_active ? '启用' : '禁用' }}
              </span>
              <span class="text-xs text-text-secondary">
                优先级: {{ rule.priority }}
              </span>
            </div>

            <div class="space-y-2 text-sm">
              <div>
                <span class="text-text-secondary">触发关键词:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span
                    v-for="(keyword, index) in parseKeywords(rule.trigger_keywords)"
                    :key="index"
                    class="px-2 py-0.5 bg-primary/10 text-primary rounded text-xs"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>

              <div>
                <span class="text-text-secondary">回复模板:</span>
                <p class="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono">
                  {{ rule.reply_template }}
                </p>
              </div>

              <div v-if="rule.auto_invite" class="flex items-center gap-1 text-xs text-primary">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>自动打招呼已启用</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="toggleRule(rule)"
              :class="['btn text-sm px-2 py-1', rule.is_active ? 'btn-secondary' : 'btn-primary']"
            >
              {{ rule.is_active ? '禁用' : '启用' }}
            </button>
            <button
              @click="editRule(rule)"
              class="btn btn-secondary text-sm px-2 py-1"
            >
              编辑
            </button>
            <button
              @click="deleteRule(rule.id)"
              class="btn btn-danger text-sm px-2 py-1"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <div v-if="rules.length === 0" class="text-center py-8 text-text-secondary">
        <p>暂无回复规则</p>
        <button
          @click="showCreateDialog = true"
          class="text-primary hover:underline mt-2"
        >
          创建第一个规则
        </button>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="showCreateDialog = false"></div>
      <div class="relative bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ editingRule ? '编辑规则' : '创建规则' }}</h2>

        <form @submit.prevent="saveRule">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">触发关键词 <span class="text-red-500">*</span></label>
              <input
                v-model="form.trigger_keywords"
                type="text"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                placeholder="多个关键词用逗号分隔，如: 你好,在吗,感兴趣"
                required
              />
              <p class="text-xs text-text-secondary mt-1">当消息包含任一关键词时触发回复</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">回复模板 <span class="text-red-500">*</span></label>
              <textarea
                v-model="form.reply_template"
                class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                rows="4"
                placeholder="可用变量: {candidate_name} - 候选人姓名"
                required
              ></textarea>
              <p class="text-xs text-text-secondary mt-1">使用 {candidate_name} 代表候选人姓名</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">优先级</label>
                <input
                  v-model.number="form.priority"
                  type="number"
                  min="0"
                  max="100"
                  class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                />
                <p class="text-xs text-text-secondary mt-1">数字越大优先级越高</p>
              </div>

              <div class="flex items-end">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="form.auto_invite"
                    type="checkbox"
                    class="rounded"
                  />
                  <span class="text-sm">自动打招呼</span>
                </label>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button
              type="button"
              @click="closeDialog"
              class="btn btn-secondary px-4 py-2"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="btn btn-primary px-4 py-2"
            >
              <LoadingSpinner v-if="saving" size="sm" />
              <span v-else>{{ editingRule ? '保存' : '创建' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 测试对话框 -->
    <div v-if="showTestDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="showTestDialog = false"></div>
      <div class="relative bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">测试规则匹配</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">测试消息</label>
            <textarea
              v-model="testMessage"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
              rows="3"
              placeholder="输入测试消息..."
            ></textarea>
          </div>

          <div v-if="testResult" class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div v-if="testResult.matched" class="space-y-2">
              <p class="text-sm text-green-600 dark:text-green-400">✓ 匹配成功</p>
              <div class="text-sm">
                <span class="text-text-secondary">匹配规则:</span> #{{ testResult.rule_id }}
              </div>
              <div class="text-sm">
                <span class="text-text-secondary">回复:</span>
                <p class="p-2 bg-white dark:bg-gray-800 rounded mt-1">{{ testResult.reply }}</p>
              </div>
            </div>
            <p v-else class="text-sm text-red-600 dark:text-red-400">✗ 没有匹配的规则</p>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button
            type="button"
            @click="showTestDialog = false"
            class="btn btn-secondary px-4 py-2"
          >
            关闭
          </button>
          <button
            @click="testRule"
            :disabled="testing"
            class="btn btn-primary px-4 py-2"
          >
            <LoadingSpinner v-if="testing" size="sm" />
            <span v-else>测试</span>
          </button>
        </div>
      </div>
    </div>
  </GlassCard>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import GlassCard from '@/components/ui/GlassCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

interface ReplyRule {
  id: number
  hr_account_id: number
  trigger_keywords: string
  reply_template: string
  auto_invite: boolean
  priority: number
  is_active: boolean
}

const rules = ref<ReplyRule[]>([])
const showCreateDialog = ref(false)
const showTestDialog = ref(false)
const editingRule = ref<ReplyRule | null>(null)
const saving = ref(false)
const testing = ref(false)

const form = reactive({
  trigger_keywords: '',
  reply_template: '',
  auto_invite: false,
  priority: 0
})

const testMessage = ref('')
const testResult = ref<any>(null)

function parseKeywords(keywords: string): string[] {
  return keywords.split(',').map(k => k.trim()).filter(k => k)
}

async function loadRules() {
  try {
    const response = await fetch('/api/hr/reply-rules/')
    const data = await response.json()
    if (data.code === 200) {
      rules.value = data.data || []
    }
  } catch (error) {
    console.error('Failed to load rules:', error)
  }
}

async function saveRule() {
  saving.value = true
  try {
    const url = editingRule.value ? `/api/hr/reply-rules/${editingRule.value.id}` : '/api/hr/reply-rules/'
    const method = editingRule.value ? 'PUT' : 'POST'

    const params = new URLSearchParams({
      hr_account_id: '1', // TODO: 从当前活跃账户获取
      trigger_keywords: form.trigger_keywords,
      reply_template: form.reply_template,
      auto_invite: form.auto_invite.toString(),
      priority: form.priority.toString()
    })

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    })

    if (response.ok) {
      closeDialog()
      await loadRules()
    } else {
      alert('保存失败')
    }
  } catch (error) {
    console.error('Failed to save rule:', error)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

function editRule(rule: ReplyRule) {
  editingRule.value = rule
  form.trigger_keywords = rule.trigger_keywords
  form.reply_template = rule.reply_template
  form.auto_invite = rule.auto_invite
  form.priority = rule.priority
  showCreateDialog.value = true
}

async function toggleRule(rule: ReplyRule) {
  try {
    const response = await fetch(`/api/hr/reply-rules/${rule.id}?is_active=${(!rule.is_active).toString()}`, {
      method: 'PUT'
    })
    if (response.ok) {
      await loadRules()
    }
  } catch (error) {
    console.error('Failed to toggle rule:', error)
  }
}

async function deleteRule(ruleId: number) {
  if (!confirm('确定要删除这个规则吗？')) return

  try {
    const response = await fetch(`/api/hr/reply-rules/${ruleId}`, {
      method: 'DELETE'
    })
    if (response.ok) {
      await loadRules()
    } else {
      alert('删除失败')
    }
  } catch (error) {
    console.error('Failed to delete rule:', error)
    alert('删除失败')
  }
}

function closeDialog() {
  showCreateDialog.value = false
  editingRule.value = null
  form.trigger_keywords = ''
  form.reply_template = ''
  form.auto_invite = false
  form.priority = 0
}

async function testRule() {
  testing.value = true
  testResult.value = null

  try {
    const params = new URLSearchParams({
      message: testMessage.value,
      hr_account_id: '1'
    })

    const response = await fetch(`/api/hr/reply-rules/test?${params}`, {
      method: 'POST'
    })

    const data = await response.json()
    if (data.code === 200) {
      testResult.value = data.data
    }
  } catch (error) {
    console.error('Failed to test rule:', error)
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadRules()
})
</script>
