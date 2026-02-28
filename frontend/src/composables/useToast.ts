/**
 * Toast通知管理
 * 提供全局的Toast通知功能
 */

import { h, render } from 'vue'
import Toast from '@/components/Toast.vue'

export type ToastVariant = 'success' | 'error' | 'warning' | 'info'

interface ToastOptions {
  message: string
  variant?: ToastVariant
  duration?: number
}

/**
 * 显示Toast通知
 * @param options Toast配置选项
 */
function showToast(options: ToastOptions): void {
  const container = document.getElementById('toast-container') || createToastContainer()

  // 创建Toast组件实例
  const toastComponent = h(Toast, {
    ...options,
    onClose: () => {
      // 动画结束后移除元素
      setTimeout(() => {
        if (toastEl && toastEl.parentNode) {
          toastEl.parentNode.removeChild(toastEl)
        }
      }, 300) // 等待退出动画完成
    }
  })

  // 创建DOM元素
  const toastEl = document.createElement('div')
  toastEl.className = 'toast-item'
  container.appendChild(toastEl)

  // 渲染组件
  render(toastComponent, toastEl)
}

/**
 * 创建Toast容器
 */
function createToastContainer(): HTMLElement {
  const container = document.createElement('div')
  container.id = 'toast-container'
  container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none'
  document.body.appendChild(container)
  return container
}

/**
 * Toast通知Hook
 */
export function useToast() {
  return {
    success: (message: string, duration?: number) => {
      showToast({ message, variant: 'success', duration })
    },
    error: (message: string, duration?: number) => {
      showToast({ message, variant: 'error', duration })
    },
    warning: (message: string, duration?: number) => {
      showToast({ message, variant: 'warning', duration })
    },
    info: (message: string, duration?: number) => {
      showToast({ message, variant: 'info', duration })
    }
  }
}
