import axios from 'axios'
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error(data.detail || '没有权限执行此操作')
      } else if (status === 400) {
        const msg = data.detail || Object.values(data)[0]?.[0] || '请求参数错误'
        ElMessage.error(msg)
      } else {
        ElMessage.error(data.detail || '服务器错误')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
