/**
 * Axios请求封装
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 响应数据接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应接口
export interface PageResponse<T = any> {
  code: number
  message: string
  data: T[]
  total: number
  page: number
  page_size: number
}

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 如果code不是200，则判断为错误
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// 封装请求方法
export const http = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.get(url, config)
  },

  post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return service.post(url, data, config)
  },

  put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return service.put(url, data, config)
  },

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.delete(url, config)
  },
}

export default service
