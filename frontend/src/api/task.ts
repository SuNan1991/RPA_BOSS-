/**
 * 任务相关API
 */
import { http, ApiResponse, PageResponse } from '@/utils/request'

// 任务接口
export interface Task {
  id: string
  name: string
  task_type: string
  config: Record<string, any>
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: Record<string, any>
  error_message?: string
  created_at: string
  updated_at: string
}

// 任务查询参数
export interface TaskQuery {
  page?: number
  page_size?: number
  status?: string
  task_type?: string
}

// 创建任务参数
export interface TaskCreate {
  name: string
  task_type: string
  config: Record<string, any>
}

// 更新任务参数
export interface TaskUpdate {
  status?: string
  config?: Record<string, any>
  result?: Record<string, any>
}

export const taskApi = {
  // 获取任务列表
  getList(params: TaskQuery) {
    return http.get<PageResponse<Task>>('/tasks', { params })
  },

  // 获取任务详情
  getDetail(id: string) {
    return http.get<Task>(`/tasks/${id}`)
  },

  // 创建任务
  create(data: TaskCreate) {
    return http.post<Task>('/tasks', data)
  },

  // 更新任务
  update(id: string, data: TaskUpdate) {
    return http.put<Task>(`/tasks/${id}`, data)
  },

  // 删除任务
  delete(id: string) {
    return http.delete(`/tasks/${id}`)
  },

  // 执行任务
  execute(id: string) {
    return http.post(`/tasks/${id}/execute`)
  },
}
