/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/jobs',
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: () => import('@/views/jobs/index.vue'),
    meta: { title: '职位管理' },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/tasks/index.vue'),
    meta: { title: '任务管理' },
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/views/accounts/index.vue'),
    meta: { title: '账户管理' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/index.vue'),
    meta: { title: '系统设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
