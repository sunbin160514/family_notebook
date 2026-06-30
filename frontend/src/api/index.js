import axios from 'axios'

// 创建axios实例
// 生产环境使用相对路径（通过Nginx反向代理）
const isProd = import.meta.env.MODE === 'production'
const api = axios.create({
  baseURL: isProd ? '/api' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('请求:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const data = response.data
    if (!data.success) {
      throw new Error(data.message || '请求失败')
    }
    return data
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络错误'
    console.error('API错误:', message)
    throw new Error(message)
  }
)

// 开发环境API路径前缀
const apiPrefix = isProd ? '' : '/api'

// 家人相关API
export const memberApi = {
  // 获取所有家人
  getAll: (search) => api.get(`${apiPrefix}/members`, { params: { search } }),

  // 获取单个家人
  getById: (id) => api.get(`${apiPrefix}/members/${id}`),

  // 添加家人
  create: (data) => api.post(`${apiPrefix}/members`, data),

  // 更新家人
  update: (id, data) => api.post(`${apiPrefix}/members/${id}/update`, null, { params: data }),

  // 删除家人
  delete: (id) => api.get(`${apiPrefix}/members/${id}/delete`)
}

// 备忘录相关API
export const memoApi = {
  // 获取所有备忘录
  getAll: (params) => api.get(`${apiPrefix}/memos`, { params }),

  // 获取单个备忘录
  getById: (id) => api.get(`${apiPrefix}/memos/${id}`),

  // 创建备忘录
  create: (data) => api.post(`${apiPrefix}/memos`, data),

  // 更新备忘录
  update: (id, data) => api.put(`${apiPrefix}/memos/${id}`, data),

  // 删除备忘录
  delete: (id) => api.get(`${apiPrefix}/memos/${id}/delete`)
}

// 提醒相关API
export const reminderApi = {
  // 获取提醒列表
  getAll: (memoId) => api.get(`${apiPrefix}/reminders`, { params: { memo_id: memoId } }),

  // 创建提醒
  create: (data) => api.post(`${apiPrefix}/reminders`, data),

  // 更新提醒
  update: (id, data) => api.put(`${apiPrefix}/reminders/${id}`, data),

  // 删除提醒
  delete: (id) => api.get(`${apiPrefix}/reminders/${id}/delete`),

  // 测试发送提醒
  test: (id) => api.post(`${apiPrefix}/reminders/${id}/test`)
}

// 设置相关API
export const settingApi = {
  // 获取通知设置
  getNotifications: () => api.get(`${apiPrefix}/settings/notifications`),

  // 保存通知设置
  saveNotifications: (data) => api.post(`${apiPrefix}/settings/notifications`, data)
}

export default api
