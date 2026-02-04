/**
 * 全局类型定义
 */

// 通用响应
declare interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应
declare interface PageResponse<T = any> {
  code: number
  message: string
  data: T[]
  total: number
  page: number
  page_size: number
}
