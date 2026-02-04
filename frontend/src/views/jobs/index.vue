<template>
  <el-container class="jobs-container">
    <el-header>
      <div class="header-content">
        <h2>职位管理</h2>
        <el-button type="primary" @click="handleCreate">添加职位</el-button>
      </div>
    </el-header>

    <el-main>
      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="城市">
          <el-input v-model="queryForm.city" placeholder="请输入城市" clearable />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="queryForm.keyword" placeholder="请输入关键词" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 职位表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="job_name" label="职位名称" min-width="150" />
        <el-table-column prop="company_name" label="公司名称" min-width="150" />
        <el-table-column prop="salary" label="薪资" width="120" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="area" label="区域" width="100" />
        <el-table-column prop="experience" label="经验" width="100" />
        <el-table-column prop="education" label="学历" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(row)">编辑</el-button>
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
import { jobApi, type Job, type JobQuery } from '@/api'

const loading = ref(false)
const tableData = ref<Job[]>([])

const queryForm = reactive<JobQuery>({
  city: '',
  keyword: '',
  page: 1,
  page_size: 10,
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 获取职位列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await jobApi.getList({
      ...queryForm,
      page: pagination.page,
      page_size: pagination.page_size,
    })
    tableData.value = res.data
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取职位列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  queryForm.city = ''
  queryForm.keyword = ''
  handleSearch()
}

// 创建
const handleCreate = () => {
  ElMessage.info('功能开发中')
}

// 查看
const handleView = (row: Job) => {
  ElMessage.info('功能开发中')
}

// 编辑
const handleEdit = (row: Job) => {
  ElMessage.info('功能开发中')
}

// 删除
const handleDelete = async (row: Job) => {
  try {
    await ElMessageBox.confirm('确定要删除该职位吗?', '提示', {
      type: 'warning',
    })
    await jobApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: '',
    applied: 'success',
    rejected: 'danger',
  }
  return map[status] || ''
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待投递',
    applied: '已投递',
    rejected: '已拒绝',
  }
  return map[status] || status
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.jobs-container {
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

    .search-form {
      margin-bottom: 20px;
    }

    .el-pagination {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
