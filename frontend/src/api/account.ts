/**
 * 账户相关API
 */
import { http, ApiResponse, PageResponse } from '@/utils/request'

// 账户接口
export interface Account {
  id: string
  phone: string
  username?: string
  is_active: boolean
  cookie_status: 'none' | 'valid' | 'invalid'
  last_login?: string
  created_at: string
  updated_at: string
}

// 账户查询参数
export interface AccountQuery {
  page?: number
  page_size?: number
  is_active?: boolean
}

// 创建账户参数
export interface AccountCreate {
  phone: string
  username?: string
  password: string
  is_active?: boolean
}

// 更新账户参数
export interface AccountUpdate {
  username?: string
  is_active?: boolean
  cookie_status?: string
}

export const accountApi = {
  // 获取账户列表
  getList(params: AccountQuery) {
    return http.get<PageResponse<Account>>('/accounts', { params })
  },

  // 获取账户详情
  getDetail(id: string) {
    return http.get<Account>(`/accounts/${id}`)
  },

  // 创建账户
  create(data: AccountCreate) {
    return http.post<Account>('/accounts', data)
  },

  // 更新账户
  update(id: string, data: AccountUpdate) {
    return http.put<Account>(`/accounts/${id}`, data)
  },

  // 删除账户
  delete(id: string) {
    return http.delete(`/accounts/${id}`)
  },

  // 刷新Cookie
  refreshCookie(id: string) {
    return http.post(`/accounts/${id}/refresh-cookie`)
  },
}
