/**
 * 导航状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ROUTES, ROUTE_NAMES } from '@/router/routes'

export const useNavigationStore = defineStore(
  'navigation',
  () => {
    // State
    const sidebarCollapsed = ref(false)
    const currentRoute = ref<string>(ROUTES.HOME)
    const mobileMenuOpen = ref(false)

    // Actions
    function toggleSidebar() {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }

    function setSidebarCollapsed(collapsed: boolean) {
      sidebarCollapsed.value = collapsed
    }

    function setCurrentRoute(route: string) {
      currentRoute.value = route
    }

    function toggleMobileMenu() {
      mobileMenuOpen.value = !mobileMenuOpen.value
    }

    function closeMobileMenu() {
      mobileMenuOpen.value = false
    }

    function getRouteName(path: string): string {
      const routeMap: Record<string, string> = {
        [ROUTES.HOME]: ROUTE_NAMES.Home,
        [ROUTES.SYSTEM]: ROUTE_NAMES.System,
        [ROUTES.WORK]: ROUTE_NAMES.Work,
        [ROUTES.CHAT]: ROUTE_NAMES.Chat,
      }
      return routeMap[path] || ROUTE_NAMES.Home
    }

    // Computed
    const isMobile = computed(() => {
      if (typeof window === 'undefined') return false
      return window.innerWidth < 768
    })

    // Watch for sidebar collapse changes to persist
    function watchSidebarCollapse() {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('sidebar_collapsed')
        if (saved !== null) {
          sidebarCollapsed.value = saved === 'true'
        }
      }
    }

    // Initialize from storage
    watchSidebarCollapse()

    return {
      // State
      sidebarCollapsed,
      currentRoute,
      mobileMenuOpen,
      isMobile,
      // Actions
      toggleSidebar,
      setSidebarCollapsed,
      setCurrentRoute,
      toggleMobileMenu,
      closeMobileMenu,
      getRouteName,
    }
  }
)
