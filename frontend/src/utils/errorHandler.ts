/**
 * 全局错误处理器
 * 统一捕获和处理所有错误，自动显示toast通知
 */

import { useToast } from '@/composables/useToast'

/**
 * 设置全局错误处理
 */
export function setupErrorHandling() {
  // 1. 全局未捕获的同步错误
  window.onerror = (message, source, lineno, colno, error) => {
    const toast = useToast()
    toast.error(`系统错误: ${message}`)
    console.error('Global error:', { message, source, lineno, colno, error })
    return false
  }

  // 2. 全局未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    const toast = useToast()
    const errorMessage = event.reason?.message || event.reason || '未知错误'
    toast.error(`异步错误: ${errorMessage}`)
    console.error('Unhandled rejection:', event.reason)
  })

  // 3. Vue错误处理（在main.ts中会配置app.config.errorHandler）
  console.log('[Error Handler] Global error handling setup complete')
}

/**
 * API错误处理器
 *
 * @param error - 错误对象
 * @param operation - 操作名称（用于提示消息）
 */
export function handleApiError(error: any, operation: string = '操作') {
  const toast = useToast()

  if (error.response) {
    // 服务器返回错误响应
    const message = error.response.data?.message || error.response.statusText || '服务器错误'
    toast.error(`${operation}失败: ${message}`)
    console.error(`API Error [${operation}]:`, {
      status: error.response.status,
      data: error.response.data,
      error
    })
  } else if (error.request) {
    // 请求已发送但无响应
    toast.error(`${operation}失败: 网络错误，请检查连接`)
    console.error(`Network Error [${operation}]:`, error)
  } else {
    // 请求配置错误
    const message = error.message || '未知错误'
    toast.error(`${operation}失败: ${message}`)
    console.error(`Request Error [${operation}]:`, error)
  }
}

/**
 * 创建带错误处理的async函数包装器
 *
 * @param fn - 要执行的异步函数
 * @param operation - 操作名称
 * @returns 包装后的函数
 */
export function withErrorHandling<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  operation: string
): T {
  return (async (...args: any[]) => {
    try {
      return await fn(...args)
    } catch (error) {
      handleApiError(error, operation)
      throw error
    }
  }) as T
}

/**
 * Vue组件错误处理mixin
 * 在组件中使用，自动捕获方法中的错误
 */
export const errorHandlingMixin = {
  methods: {
    /**
     * 安全执行async方法
     * 自动捕获错误并显示toast
     */
    async safeAsync<T>(operation: string, fn: () => Promise<T>): Promise<T | undefined> {
      try {
        return await fn()
      } catch (error) {
        handleApiError(error, operation)
        return undefined
      }
    }
  }
}
