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
  async error => {
    if (error.response) {
      const { status, data, config } = error.response
      
      if (status === 401) {
        const refreshToken = Cookies.get('refresh_token')
        
        // 如果有refresh token，尝试刷新access token
        if (refreshToken && !config._retry) {
          config._retry = true
          try {
            // 调用refresh token接口获取新的access token
            const response = await axios({
              method: 'post',
              url: '/api/users/token/refresh/',
              data: { refresh: refreshToken },
              baseURL: '/' // 确保使用正确的baseURL
            })
            
            const { access } = response.data
            
            // 更新本地存储的access token
            Cookies.set('access_token', access, { expires: 1 })
            
            // 更新请求头的Authorization
            axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
            config.headers['Authorization'] = `Bearer ${access}`
            
            // 重试原始请求
            return request(config)
          } catch (refreshError) {
            // refresh token也过期了，清除所有token并跳转到登录页
            Cookies.remove('access_token')
            Cookies.remove('refresh_token')
            ElMessage.error('登录已过期，请重新登录')
            router.push('/login')
            return Promise.reject(refreshError)
          }
        } else {
          // 没有refresh token或已经重试过，直接跳转到登录页
          Cookies.remove('access_token')
          Cookies.remove('refresh_token')
          ElMessage.error('登录已过期，请重新登录')
          router.push('/login')
        }
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
