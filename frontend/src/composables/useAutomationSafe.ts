/**
 * 自动化安全组合式函数
 *
 * 提供便捷的安全操作接口
 */
import { ref } from 'vue'
import {
  randomDelay,
  throttle,
  safeApiCall,
  automationSafe,
} from '@/utils/automation-safe'

/**
 * 自动化安全操作 Composable
 */
export function useAutomationSafe() {
  const isExecuting = ref(false)
  const lastExecution = ref<number>(0)

  /**
   * 执行安全操作
   */
  async function execute<T>(
    operation: () => Promise<T>,
    options?: {
      delayBefore?: number
      delayAfter?: number
      jitter?: number
    }
  ): Promise<T> {
    isExecuting.value = true
    lastExecution.value = Date.now()

    try {
      const result = await safeApiCall(operation, options)
      return result
    } finally {
      isExecuting.value = false
    }
  }

  /**
   * 节流执行
   */
  function throttledExecute<T extends (...args: any[]) => any>(
    fn: T,
    minMs: number
  ): (...args: Parameters<T>) => void {
    return throttle(fn, minMs)
  }

  /**
   * 检查是否可以执行（基于上次执行时间）
   */
  function canExecute(minInterval = 1000): boolean {
    const now = Date.now()
    return now - lastExecution.value >= minInterval
  }

  /**
   * 等待直到可以执行
   */
  async function waitUntilCanExecute(minInterval = 1000): Promise<void> {
    const now = Date.now()
    const elapsed = now - lastExecution.value

    if (elapsed < minInterval) {
      await randomDelay(minInterval - elapsed, 0.1)
    }
  }

  return {
    // 状态
    isExecuting,
    lastExecution,
    // 方法
    execute,
    throttledExecute,
    canExecute,
    waitUntilCanExecute,
    // 工具函数
    randomDelay,
    automationSafe,
  }
}
