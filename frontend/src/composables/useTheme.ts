/**
 * useTheme - Theme management composable
 */
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'

export function useTheme() {
  const themeStore = useThemeStore()

  function toggleTheme() {
    themeStore.toggleTheme()
  }

  function setTheme(mode: 'light' | 'dark') {
    themeStore.setTheme(mode)
  }

  onMounted(() => {
    themeStore.loadTheme()
  })

  return {
    mode: themeStore.mode,
    toggleTheme,
    setTheme
  }
}
