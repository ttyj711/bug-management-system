<template>
  <el-container class="main-layout">
    <el-aside width="200px" class="sidebar">
      <div class="logo">BUG管理系统</div>
      <el-menu :default-active="activeMenu" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/bugs">
          <el-icon><List /></el-icon>
          <span>BUG列表</span>
        </el-menu-item>
        <el-menu-item index="/bugs/kanban">
          <el-icon><Grid /></el-icon>
          <span>BUG看板</span>
        </el-menu-item>

        <el-menu-item index="/users" v-if="userStore.isSuperAdmin">
          <el-icon><UserFilled /></el-icon>
          <span>账号管理</span>
        </el-menu-item>
        <el-menu-item index="/modules" v-if="userStore.isSuperAdmin">
          <el-icon><Menu /></el-icon>
          <span>模块管理</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><Setting /></el-icon>
          <span>个人信息</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
            <el-popover placement="bottom" :width="360" trigger="click" @show="fetchNotifications">
              <template #reference>
                <el-button :icon="Bell" circle />
              </template>
              <div class="notification-panel">
                <div class="notification-header">
                  <span>消息通知</span>
                  <el-button type="primary" link size="small" @click="handleMarkAllRead" v-if="unreadCount > 0">
                    全部已读
                  </el-button>
                </div>
                <div class="notification-list" v-loading="notificationLoading">
                  <div v-if="notifications.length === 0" class="no-notification">
                    暂无消息
                  </div>
                  <div 
                    v-for="notification in notifications" 
                    :key="notification.id" 
                    class="notification-item"
                    :class="{ unread: !notification.is_read }"
                    @click="handleNotificationClick(notification)"
                  >
                    <div class="notification-title">{{ notification.title }}</div>
                    <div class="notification-content">{{ notification.content }}</div>
                    <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>
                </div>
              </div>
            </el-popover>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ userStore.user?.username }}</span>
              <span class="role-tag">{{ userStore.user?.role_display }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { getNotifications, getUnreadCount, markAllRead, markRead } from '../api/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const unreadCount = ref(0)
const notifications = ref([])
const notificationLoading = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/bugs/') && path !== '/bugs/kanban') {
    return '/bugs'
  }
  return path
})

const fetchUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.count
  } catch (e) {
    // ignore
  }
}

const fetchNotifications = async () => {
  notificationLoading.value = true
  try {
    const res = await getNotifications({ page_size: 20 })
    notifications.value = res.results
  } finally {
    notificationLoading.value = false
  }
}

const handleMarkAllRead = async () => {
  await markAllRead()
  unreadCount.value = 0
  notifications.value.forEach(n => n.is_read = true)
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await markRead(notification.id)
    notification.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
  if (notification.bug_id) {
    router.push(`/bugs/${notification.bug_id}`)
  }
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  userStore.fetchProfile()
  fetchUnreadCount()
  
  // 每30秒刷新未读数量
  const timer = setInterval(fetchUnreadCount, 30000)
  onUnmounted(() => clearInterval(timer))
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #263445;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  cursor: pointer;
}

.notification-panel {
  max-height: 400px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
  font-weight: 600;
}

.notification-list {
  max-height: 340px;
  overflow-y: auto;
}

.no-notification {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.notification-item {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-item.unread {
  background: #ecf5ff;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: #303133;
}

.notification-content {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  font-size: 14px;
}

.role-tag {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
