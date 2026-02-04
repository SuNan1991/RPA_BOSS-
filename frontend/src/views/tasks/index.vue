<template>
  <el-container class="tasks-container">
    <el-header>
      <div class="header-content">
        <h2>任务管理</h2>
        <el-button type="primary" @click="handleCreate">创建任务</el-button>
      </div>
    </el-header>

    <el-main>
      <!-- 任务表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="name" label="任务名称" min-width="150" />
        <el-table-column prop="task_type" label="任务类型" width="150">
          <template #default="{ row }">
            <el-tag>{{ getTaskTypeText(row.task_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              type="success"
              link
              @click="handleExecute(row)"
              :disabled="row.status === 'running'"
            >
              执行
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi, type Task } from '@/api'

const loading = ref(false)
const tableData = ref<Task[]>([])

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 获取任务列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await taskApi.getList({
      page: pagination.page,
      page_size: pagination.page_size,
    })
    tableData.value = res.data
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 创建任务
const handleCreate = () => {
  ElMessage.info('功能开发中')
}

// 查看任务
const handleView = (row: Task) => {
  ElMessage.info('功能开发中')
}

// 执行任务
const handleExecute = async (row: Task) => {
  try {
    await ElMessageBox.confirm('确定要执行该任务吗?', '提示', {
      type: 'warning',
    })
    await taskApi.execute(row.id)
    ElMessage.success('任务开始执行')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败')
    }
  }
}

// 删除任务
const handleDelete = async (row: Task) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗?', '提示', {
      type: 'warning',
    })
    await taskApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取任务类型文本
const getTaskTypeText = (type: string) => {
  const map: Record<string, string> = {
    search_job: '职位搜索',
    auto_apply: '自动投递',
    auto_chat: '自动聊天',
  }
  return map[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || ''
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.tasks-container {
  height: 100%;

  .el-header {
    height: 60px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    align-items: center;

    .header-content {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .el-main {
    padding: 20px;

    .el-pagination {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
