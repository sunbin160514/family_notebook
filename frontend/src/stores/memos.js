import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { memoApi, reminderApi } from '../api'

export const useMemoStore = defineStore('memos', () => {
  // State
  const memos = ref([])
  const currentMemo = ref(null)
  const reminders = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const memoCount = computed(() => memos.value.length)

  const getMemoById = computed(() => {
    return (id) => memos.value.find(m => m.id === Number(id))
  })

  const memosByCategory = computed(() => {
    return (category) => memos.value.filter(m => m.category === category)
  })

  // Actions
  const fetchMemos = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await memoApi.getAll(params)
      memos.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMemoById = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await memoApi.getById(id)
      currentMemo.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createMemo = async (data) => {
    loading.value = true
    try {
      const response = await memoApi.create(data)
      memos.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateMemo = async (id, data) => {
    loading.value = true
    try {
      const response = await memoApi.update(id, data)
      const index = memos.value.findIndex(m => m.id === Number(id))
      if (index !== -1) {
        memos.value[index] = response.data
      }
      if (currentMemo.value?.id === Number(id)) {
        currentMemo.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteMemo = async (id) => {
    loading.value = true
    try {
      await memoApi.delete(id)
      memos.value = memos.value.filter(m => m.id !== Number(id))
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 提醒相关
  const fetchReminders = async (memoId) => {
    try {
      const response = await reminderApi.getAll(memoId)
      reminders.value = response.data
      return response.data
    } catch (err) {
      console.error('获取提醒失败:', err)
      throw err
    }
  }

  const createReminder = async (data) => {
    try {
      const response = await reminderApi.create(data)
      reminders.value.push(response.data)
      return response.data
    } catch (err) {
      throw err
    }
  }

  const updateReminder = async (id, data) => {
    try {
      const response = await reminderApi.update(id, data)
      const index = reminders.value.findIndex(r => r.id === Number(id))
      if (index !== -1) {
        reminders.value[index] = response.data
      }
      return response.data
    } catch (err) {
      throw err
    }
  }

  const deleteReminder = async (id) => {
    try {
      await reminderApi.delete(id)
      reminders.value = reminders.value.filter(r => r.id !== Number(id))
    } catch (err) {
      throw err
    }
  }

  const testReminder = async (id) => {
    return await reminderApi.test(id)
  }

  return {
    memos,
    currentMemo,
    reminders,
    loading,
    error,
    memoCount,
    getMemoById,
    memosByCategory,
    fetchMemos,
    fetchMemoById,
    createMemo,
    updateMemo,
    deleteMemo,
    fetchReminders,
    createReminder,
    updateReminder,
    deleteReminder,
    testReminder
  }
})
