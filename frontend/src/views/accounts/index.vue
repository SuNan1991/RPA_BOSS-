<template>
  <el-container class="accounts-container">
    <el-header>
      <div class="header-content">
        <h2>账户管理</h2>
        <el-button type="primary" @click="handleCreate">添加账户</el-button>
      </div>
    </el-header>

    <el-main>
      <!-- 账户表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column label="Cookie状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getCookieStatusType(row.cookie_status)">
              {{ getCookieStatusText(row.cookie_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleRefreshCookie(row)">刷新Cookie</el-button>
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
import { accountApi, type Account } from '@/api'

const loading = ref(false)
const tableData = ref<Account[]>([])

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 获取账户列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await accountApi.getList({
      page: pagination.page,
      page_size: pagination.page_size,
    })
    tableData.value = res.data
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取账户列表失败')
  } finally {
    loading.value = false
  }
}

// 创建账户
const handleCreate = () => {
  ElMessage.info('功能开发中')
}

// 编辑账户
const handleEdit = (row: Account) => {
  ElMessage.info('功能开发中')
}

// 刷新Cookie
const handleRefreshCookie = async (row: Account) => {
  try {
    await ElMessageBox.confirm('确定要刷新该账户的Cookie吗?', '提示', {
      type: 'warning',
    })
    await accountApi.refreshCookie(row.id)
    ElMessage.success('Cookie刷新成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('刷新失败')
    }
  }
}

// 删除账户
const handleDelete = async (row: Account) => {
  try {
    await ElMessageBox.confirm('确定要删除该账户吗?', '提示', {
      type: 'warning',
    })
    await accountApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取Cookie状态类型
const getCookieStatusType = (status: string) => {
  const map: Record<string, any> = {
    none: 'info',
    valid: 'success',
    invalid: 'danger',
  }
  return map[status] || ''
}

// 获取Cookie状态文本
const getCookieStatusText = (status: string) => {
  const map: Record<string, string> = {
    none: '未登录',
    valid: '有效',
    invalid: '失效',
  }
  return map[status] || status
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.accounts-container {
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
