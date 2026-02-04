/**
 * 职位相关API
 */
import { http, ApiResponse, PageResponse } from '@/utils/request'

// 职位接口
export interface Job {
  id: string
  job_name: string
  company_name: string
  salary: string
  city: string
  area?: string
  experience?: string
  education?: string
  company_size?: string
  industry?: string
  job_url: string
  boss_title?: string
  status: string
  is_applied: boolean
  notes?: string
  created_at: string
  updated_at: string
}

// 职位查询参数
export interface JobQuery {
  page?: number
  page_size?: number
  city?: string
  keyword?: string
}

// 创建职位参数
export interface JobCreate {
  job_name: string
  company_name: string
  salary: string
  city: string
  area?: string
  experience?: string
  education?: string
  company_size?: string
  industry?: string
  job_url: string
  boss_title?: string
}

// 更新职位参数
export interface JobUpdate {
  status?: string
  is_applied?: boolean
  notes?: string
}

export const jobApi = {
  // 获取职位列表
  getList(params: JobQuery) {
    return http.get<PageResponse<Job>>('/jobs', { params })
  },

  // 获取职位详情
  getDetail(id: string) {
    return http.get<Job>(`/jobs/${id}`)
  },

  // 创建职位
  create(data: JobCreate) {
    return http.post<Job>('/jobs', data)
  },

  // 更新职位
  update(id: string, data: JobUpdate) {
    return http.put<Job>(`/jobs/${id}`, data)
  },

  // 删除职位
  delete(id: string) {
    return http.delete(`/jobs/${id}`)
  },

  // 批量创建职位
  batchCreate(data: JobCreate[]) {
    return http.post<{ count: number }>('/jobs/batch', data)
  },
}
