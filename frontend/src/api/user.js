import request from '../utils/request'

// 用户登录
export function login(data) {
  return request.post('/users/login/', data)
}

// 用户登出
export function logout(data) {
  return request.post('/users/logout/', data)
}

// 获取个人信息
export function getProfile() {
  return request.get('/users/profile/')
}

// 更新个人信息
export function updateProfile(data) {
  return request.put('/users/profile/', data)
}

// 修改密码
export function changePassword(data) {
  return request.post('/users/change-password/', data)
}

// 获取用户列表
export function getUserList(params) {
  return request.get('/users/', { params })
}

// 获取用户详情
export function getUser(id) {
  return request.get(`/users/${id}/`)
}

// 创建用户
export function createUser(data) {
  return request.post('/users/', data)
}

// 更新用户
export function updateUser(id, data) {
  return request.put(`/users/${id}/`, data)
}

// 删除用户
export function deleteUser(id) {
  return request.delete(`/users/${id}/`)
}

// 重置用户密码
export function resetUserPassword(id, data) {
  return request.post(`/users/${id}/reset_password/`, data)
}

// 切换用户状态
export function toggleUserStatus(id) {
  return request.post(`/users/${id}/toggle_status/`)
}

// 获取开发人员列表
export function getDevelopers() {
  return request.get('/users/developers/')
}
