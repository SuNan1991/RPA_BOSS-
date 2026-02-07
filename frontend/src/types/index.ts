/**
 * Type definitions
 */
export interface UserInfo {
  username?: string
  avatar?: string
  [key: string]: any
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface AuthStatus {
  is_logged_in: boolean
  user_info: UserInfo | null
  browser_status: string | null
  login_in_progress: boolean
  timestamp: string
}
