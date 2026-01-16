import request from '../utils/request'

// 获取BUG列表
export function getBugList(params) {
  return request.get('/bugs/', { params })
}

// 获取BUG详情
export function getBug(id) {
  return request.get(`/bugs/${id}/`)
}

// 创建BUG
export function createBug(data) {
  return request.post('/bugs/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 更新BUG
export function updateBug(id, data) {
  return request.put(`/bugs/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 删除BUG
export function deleteBug(id) {
  return request.delete(`/bugs/${id}/`)
}

// 更新BUG状态
export function updateBugStatus(id, data) {
  return request.post(`/bugs/${id}/update_status/`, data)
}

// 分配BUG
export function assignBug(id, data) {
  return request.post(`/bugs/${id}/assign/`, data)
}

// 上传BUG附件
export function uploadAttachment(id, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/bugs/${id}/upload_attachment/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 删除BUG附件
export function deleteAttachment(bugId, attachmentId) {
  return request.delete(`/bugs/${bugId}/attachment/${attachmentId}/`)
}
