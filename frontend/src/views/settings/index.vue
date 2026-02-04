<template>
  <el-container class="settings-container">
    <el-header>
      <h2>系统设置</h2>
    </el-header>

    <el-main>
      <el-card>
        <template #header>
          <div class="card-header">
            <span>RPA配置</span>
          </div>
        </template>

        <el-form :model="settings" label-width="150px">
          <el-form-item label="无头模式">
            <el-switch v-model="settings.headless" />
            <span class="form-tip">启用后浏览器将在后台运行，不显示界面</span>
          </el-form-item>

          <el-form-item label="超时时间(ms)">
            <el-input-number v-model="settings.timeout" :min="5000" :max="60000" :step="1000" />
          </el-form-item>

          <el-form-item label="自动截图">
            <el-switch v-model="settings.autoScreenshot" />
            <span class="form-tip">出现错误时自动保存截图</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSave">保存设置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="mt-20">
        <template #header>
          <div class="card-header">
            <span>任务配置</span>
          </div>
        </template>

        <el-form :model="taskSettings" label-width="150px">
          <el-form-item label="默认延迟(秒)">
            <el-input-number v-model="taskSettings.delay" :min="0.5" :max="10" :step="0.5" />
          </el-form-item>

          <el-form-item label="最大重试次数">
            <el-input-number v-model="taskSettings.maxRetries" :min="1" :max="10" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSaveTaskSettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const settings = reactive({
  headless: false,
  timeout: 30000,
  autoScreenshot: true,
})

const taskSettings = reactive({
  delay: 2.0,
  maxRetries: 3,
})

const handleSave = () => {
  // TODO: 保存设置到后端
  ElMessage.success('设置保存成功')
}

const handleSaveTaskSettings = () => {
  // TODO: 保存设置到后端
  ElMessage.success('设置保存成功')
}
</script>

<style scoped lang="scss">
.settings-container {
  height: 100%;

  .el-header {
    height: 60px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    align-items: center;
  }

  .el-main {
    padding: 20px;

    .card-header {
      font-weight: bold;
    }

    .form-tip {
      margin-left: 10px;
      color: #999;
      font-size: 12px;
    }
  }
}
</style>
