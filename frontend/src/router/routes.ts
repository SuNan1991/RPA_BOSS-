/**
 * 路由常量定义
 */
export const ROUTES = {
  LOGIN: '/login',
  HOME: '/',
  SYSTEM: '/system',
  WORK: '/work',
  CHAT: '/chat',
} as const

/**
 * 路由名称常量
 */
export const ROUTE_NAMES = {
  Login: 'Login',
  Home: 'Home',
  System: 'System',
  Work: 'Work',
  Chat: 'Chat',
} as const

/**
 * 导航菜单配置
 */
export interface NavItem {
  name: string
  path: string
  icon: string
  label: string
}

export const NAV_ITEMS: NavItem[] = [
  {
    name: ROUTE_NAMES.Home,
    path: ROUTES.HOME,
    icon: 'home',
    label: '主页',
  },
  {
    name: ROUTE_NAMES.System,
    path: ROUTES.SYSTEM,
    icon: 'settings',
    label: '系统设置',
  },
  {
    name: ROUTE_NAMES.Work,
    path: ROUTES.WORK,
    icon: 'work',
    label: '工作设置',
  },
  {
    name: ROUTE_NAMES.Chat,
    path: ROUTES.CHAT,
    icon: 'chat',
    label: '人选沟通',
  },
] as const
