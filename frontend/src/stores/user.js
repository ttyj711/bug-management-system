import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import { login as loginApi, logout as logoutApi, getProfile } from '../api/user'
import router from '../router'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(Cookies.get('access_token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const isSuperAdmin = computed(() => userRole.value === 'super_admin')
  const isAdmin = computed(() => ['super_admin', 'admin'].includes(userRole.value))
  const isTester = computed(() => userRole.value === 'tester')
  const isDeveloper = computed(() => userRole.value === 'developer')

  // 登录
  async function login(credentials) {
    const res = await loginApi(credentials)
    token.value = res.access
    user.value = res.user
    Cookies.set('access_token', res.access, { expires: 1 })
    Cookies.set('refresh_token', res.refresh, { expires: 7 })
    return res
  }

  // 登出
  async function logout() {
    try {
      const refreshToken = Cookies.get('refresh_token')
      if (refreshToken) {
        await logoutApi({ refresh: refreshToken })
      }
    } catch (e) {
      // ignore
    }
    token.value = ''
    user.value = null
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
    router.push('/login')
  }

  // 获取用户信息
  async function fetchProfile() {
    if (!token.value) return
    try {
      const res = await getProfile()
      user.value = res
    } catch (e) {
      logout()
    }
  }

  // 检查权限
  function hasPermission(permission) {
    if (isSuperAdmin.value) return true
    
    const permissions = {
      'user:manage': isSuperAdmin.value,
      'bug:create': isAdmin.value || isTester.value,
      'bug:delete': isSuperAdmin.value,
      'bug:edit': isSuperAdmin.value || isTester.value,
      'bug:status': isSuperAdmin.value || isDeveloper.value,
      'bug:assign': isAdmin.value
    }
    
    return permissions[permission] || false
  }

  return {
    user,
    token,
    isLoggedIn,
    userRole,
    isSuperAdmin,
    isAdmin,
    isTester,
    isDeveloper,
    login,
    logout,
    fetchProfile,
    hasPermission
  }
})
