import request from '../utils/request'

// 获取级联数据（项目-产品-模块）
export function getModuleCascade() {
  return request.get('/modules/cascade/')
}

// 项目管理
export function getProjectList(params) {
  return request.get('/modules/projects/', { params })
}

export function createProject(data) {
  return request.post('/modules/projects/', data)
}

export function updateProject(id, data) {
  return request.put(`/modules/projects/${id}/`, data)
}

export function deleteProject(id) {
  return request.delete(`/modules/projects/${id}/`)
}

// 产品管理
export function getProductList(params) {
  return request.get('/modules/products/', { params })
}

export function createProduct(data) {
  return request.post('/modules/products/', data)
}

export function updateProduct(id, data) {
  return request.put(`/modules/products/${id}/`, data)
}

export function deleteProduct(id) {
  return request.delete(`/modules/products/${id}/`)
}

// 模块管理
export function getModuleList(params) {
  return request.get('/modules/modules/', { params })
}

export function createModule(data) {
  return request.post('/modules/modules/', data)
}

export function updateModule(id, data) {
  return request.put(`/modules/modules/${id}/`, data)
}

export function deleteModule(id) {
  return request.delete(`/modules/modules/${id}/`)
}
