/**
 * 自动化安全工具函数
 *
 * 用于模拟真实用户行为，避免被检测为自动化程序
 */

/**
 * 随机延迟函数
 * @param baseMs 基础延迟时间（毫秒）
 * @param jitter 抖动比例（0-1），默认 0.2 表示 ±20%
 */
export async function randomDelay(baseMs: number, jitter = 0.2): Promise<void> {
  const randomFactor = 1 + (Math.random() * 2 - 1) * jitter
  const delay = Math.floor(baseMs * randomFactor)
  return new Promise(resolve => setTimeout(resolve, delay))
}

/**
 * 随机用户代理池
 * 从常见的真实浏览器 User-Agent 中随机选择
 */
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

/**
 * 获取随机 User-Agent
 */
export function getRandomUA(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)]
}

/**
 * 平滑滚动到目标位置
 * 模拟真实用户的滚动行为
 * @param element 目标元素
 * @param targetY 目标 Y 坐标
 */
export async function smoothScroll(
  element: Element,
  targetY: number
): Promise<void> {
  return new Promise(resolve => {
    const startY = element.scrollTop
    const distance = targetY - startY
    const duration = 500 + Math.random() * 300 // 500-800ms 随机滚动时间

    const startTime = performance.now()

    function animate(currentTime: number) {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // 使用 easeInOutCubic 缓动函数
      const easeProgress = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2

      element.scrollTop = startY + distance * easeProgress

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        resolve()
      }
    }

    requestAnimationFrame(animate)
  })
}

/**
 * 节流函数
 * 限制函数的执行频率
 * @param fn 要节流的函数
 * @param minMs 最小执行间隔（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  minMs: number
): (...args: Parameters<T>) => void {
  let lastCall = 0
  let lastResult: ReturnType<T>

  return function(this: any, ...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastCall >= minMs) {
      lastCall = now
      lastResult = fn.apply(this, args)
    }
    return lastResult
  }
}

/**
 * 防抖函数
 * 延迟执行函数，如果在延迟时间内再次调用则重新计时
 * @param fn 要防抖的函数
 * @param delayMs 延迟时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delayMs: number
): (...args: Parameters<T>) => void {
  let timeoutId: number | null = null

  return function(this: any, ...args: Parameters<T>) {
    if (timeoutId !== null) {
      clearTimeout(timeoutId)
    }

    timeoutId = window.setTimeout(() => {
      fn.apply(this, args)
      timeoutId = null
    }, delayMs)
  }
}

/**
 * 模拟鼠标移动轨迹
 * 生成贝塞尔曲线路径模拟真实鼠标移动
 * @param startX 起点 X
 * @param startY 起点 Y
 * @param endX 终点 X
 * @param endY 终点 Y
 */
export function simulateMousePath(
  startX: number,
  startY: number,
  endX: number,
  endY: number
): Array<{ x: number; y: number; delay: number }> {
  const path: Array<{ x: number; y: number; delay: number }> = []

  // 控制点，用于生成贝塞尔曲线
  const controlPoint1X = startX + (endX - startX) * 0.25 + (Math.random() - 0.5) * 50
  const controlPoint1Y = startY + (endY - startY) * 0.25 + (Math.random() - 0.5) * 50
  const controlPoint2X = startX + (endX - startX) * 0.75 + (Math.random() - 0.5) * 50
  const controlPoint2Y = startY + (endY - startY) * 0.75 + (Math.random() - 0.5) * 50

  const steps = 20 + Math.floor(Math.random() * 10) // 20-30 个点

  for (let i = 0; i <= steps; i++) {
    const t = i / steps

    // 三次贝塞尔曲线公式
    const x =
      Math.pow(1 - t, 3) * startX +
      3 * Math.pow(1 - t, 2) * t * controlPoint1X +
      3 * (1 - t) * Math.pow(t, 2) * controlPoint2X +
      Math.pow(t, 3) * endX

    const y =
      Math.pow(1 - t, 3) * startY +
      3 * Math.pow(1 - t, 2) * t * controlPoint1Y +
      3 * (1 - t) * Math.pow(t, 2) * controlPoint2Y +
      Math.pow(t, 3) * endY

    // 每个点的延迟，模拟移动速度变化
    const delay = 10 + Math.random() * 20 // 10-30ms

    path.push({ x: Math.round(x), y: Math.round(y), delay })
  }

  return path
}

/**
 * 安全的 API 请求包装器
 * 自动添加随机延迟和 User-Agent
 */
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  options?: {
    delayBefore?: number
    delayAfter?: number
    jitter?: number
  }
): Promise<T> {
  const {
    delayBefore = 500,
    delayAfter = 300,
    jitter = 0.3,
  } = options || {}

  // 请求前延迟
  await randomDelay(delayBefore, jitter)

  try {
    const result = await apiCall()

    // 请求后延迟
    await randomDelay(delayAfter, jitter)

    return result
  } catch (error) {
    throw error
  }
}

/**
 * AutomationSafe 类
 * 提供面向对象的安全操作接口
 */
export class AutomationSafe {
  private config = {
    defaultDelay: 500,
    jitter: 0.2,
    enableScrollSimulation: true,
    enableMouseSimulation: false, // 前端难以实现真实的鼠标模拟
  }

  /**
   * 执行安全操作
   */
  async execute<T>(
    operation: () => Promise<T>,
    options?: Partial<typeof this.config>
  ): Promise<T> {
    const config = { ...this.config, ...options }

    await randomDelay(config.defaultDelay, config.jitter)

    return operation()
  }

  /**
   * 批量操作，带随机间隔
   */
  async batchExecute<T>(
    operations: Array<() => Promise<T>>,
    options?: {
      minDelay?: number
      maxDelay?: number
    }
  ): Promise<T[]> {
    const { minDelay = 1000, maxDelay = 3000 } = options || {}
    const results: T[] = []

    for (const operation of operations) {
      const result = await this.execute(operation)
      results.push(result)

      // 随机等待
      const delay = minDelay + Math.random() * (maxDelay - minDelay)
      await new Promise(resolve => setTimeout(resolve, delay))
    }

    return results
  }
}

// 导出单例实例
export const automationSafe = new AutomationSafe()
