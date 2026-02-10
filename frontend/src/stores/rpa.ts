/**
 * RPA Store - Manage RPA state
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type RPAStatus = 'idle' | 'browser_opened' | 'waiting_for_login' | 'login_successful' | 'error' | 'timeout'

export const useRPAStore = defineStore('rpa', () => {
  // State
  const status = ref<RPAStatus>('idle')
  const browserId = ref<string | null>(null)
  const lastUpdate = ref<Date | null>(null)
  const errorMessage = ref<string | null>(null)

  // Actions
  function setStatus(newStatus: RPAStatus) {
    status.value = newStatus
    lastUpdate.value = new Date()
  }

  function setBrowserId(id: string | null) {
    browserId.value = id
  }

  function setError(message: string | null) {
    errorMessage.value = message
    if (message) {
      status.value = 'error'
    }
  }

  function reset() {
    status.value = 'idle'
    browserId.value = null
    lastUpdate.value = null
    errorMessage.value = null
  }

  return {
    status,
    browserId,
    lastUpdate,
    errorMessage,
    setStatus,
    setBrowserId,
    setError,
    reset
  }
})
