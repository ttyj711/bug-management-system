import request from '../utils/request'

// 获取通知列表
export function getNotifications(params) {
  return request.get('/notifications/', { params })
}

// 获取未读通知数量
export function getUnreadCount() {
  return request.get('/notifications/unread_count/')
}

// 标记所有已读
export function markAllRead() {
  return request.post('/notifications/mark_all_read/')
}

// 标记单条已读
export function markRead(id) {
  return request.post(`/notifications/${id}/mark_read/`)
}
