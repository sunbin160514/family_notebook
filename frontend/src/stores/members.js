import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { memberApi } from '../api'

export const useMemberStore = defineStore('members', () => {
  // State
  const members = ref([])
  const currentMember = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const memberCount = computed(() => members.value.length)

  const getMemberById = computed(() => {
    return (id) => members.value.find(m => m.id === Number(id))
  })

  // Actions
  const fetchMembers = async (search = '') => {
    loading.value = true
    error.value = null
    try {
      const response = await memberApi.getAll(search)
      members.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMemberById = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await memberApi.getById(id)
      currentMember.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createMember = async (data) => {
    loading.value = true
    try {
      const response = await memberApi.create(data)
      members.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateMember = async (id, data) => {
    loading.value = true
    try {
      const response = await memberApi.update(id, data)
      const index = members.value.findIndex(m => m.id === Number(id))
      if (index !== -1) {
        members.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteMember = async (id) => {
    loading.value = true
    try {
      await memberApi.delete(id)
      members.value = members.value.filter(m => m.id !== Number(id))
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    members,
    currentMember,
    loading,
    error,
    memberCount,
    getMemberById,
    fetchMembers,
    fetchMemberById,
    createMember,
    updateMember,
    deleteMember
  }
})
