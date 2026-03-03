/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { ROUTES, ROUTE_NAMES } from './routes'

const routes: RouteRecordRaw[] = [
  {
    path: ROUTES.LOGIN,
    name: ROUTE_NAMES.Login,
    component: () => import('@/views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      hideInLayout: true,
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: ROUTES.HOME,
        name: ROUTE_NAMES.Home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
          title: '主页',
        },
      },
      {
        path: ROUTES.SYSTEM,
        name: ROUTE_NAMES.System,
        component: () => import('@/views/SystemSettingsView.vue'),
        meta: {
          title: '系统设置',
        },
      },
      {
        path: ROUTES.WORK,
        name: ROUTE_NAMES.Work,
        component: () => import('@/views/WorkSettingsView.vue'),
        meta: {
          title: '工作设置',
        },
      },
      {
        path: ROUTES.CHAT,
        name: ROUTE_NAMES.Chat,
        component: () => import('@/views/ChatView.vue'),
        meta: {
          title: '人选沟通',
        },
      },
      {
        path: '',
        redirect: ROUTES.HOME,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: ROUTES.LOGIN,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard - 允许未登录用户访问主页
router.beforeEach((to, _from, next) => {
  // 只在显式访问 /login 时重定向到首页
  // 移除了强制登录检查，允许未登录用户直接进入主页
  if (to.name === ROUTE_NAMES.Login) {
    next({ name: ROUTE_NAMES.Home })
  } else {
    next()
  }
})

// Update page title
router.afterEach((to) => {
  const title = to.meta.title as string | undefined
  if (title) {
    document.title = `${title} - BOSS 直聘助手`
  } else {
    document.title = 'BOSS 直聘助手'
  }
})

export default router
