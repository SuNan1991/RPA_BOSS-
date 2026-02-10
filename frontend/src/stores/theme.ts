/**
 * Theme Store - Manage theme state
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  // State
  const mode = ref<ThemeMode>('light')

  // Actions
  function setTheme(newMode: ThemeMode) {
    mode.value = newMode
    applyTheme(newMode)
    persistTheme(newMode)
  }

  function toggleTheme() {
    const newMode = mode.value === 'light' ? 'dark' : 'light'
    setTheme(newMode)
  }

  function applyTheme(themeMode: ThemeMode) {
    if (themeMode === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function persistTheme(themeMode: ThemeMode) {
    localStorage.setItem('theme', themeMode)
  }

  function loadTheme() {
    // Check localStorage first
    const stored = localStorage.getItem('theme') as ThemeMode | null
    if (stored && (stored === 'light' || stored === 'dark')) {
      mode.value = stored
      applyTheme(stored)
      return
    }

    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      mode.value = 'dark'
      applyTheme('dark')
    } else {
      mode.value = 'light'
      applyTheme('light')
    }
  }

  // Watch for changes and apply
  watch(mode, (newMode) => {
    applyTheme(newMode)
  })

  return {
    mode,
    setTheme,
    toggleTheme,
    loadTheme
  }
})
