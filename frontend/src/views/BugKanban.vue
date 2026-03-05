<template>
  <div class="bug-kanban">
    <div class="kanban-header">
      <h2>BUG看板</h2>
      <div class="kanban-actions">
        <el-select v-model="filters.module" placeholder="筛选模块" clearable style="width: 200px" @change="fetchBugs">
          <el-option v-for="module in modules" :key="module.id" :label="module.path" :value="module.id" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="筛选优先级" clearable style="width: 120px" @change="fetchBugs">
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
        <el-button type="primary" @click="router.push('/bugs')">列表视图</el-button>
      </div>
    </div>

    <div class="kanban-board" v-loading="loading">
      <div
        v-for="column in columns"
        :key="column.status"
        class="kanban-column"
        @dragover.prevent
        @drop="handleDrop($event, column.status)"
      >
        <div class="column-header" :class="column.status">
          <span class="column-title">{{ column.title }}</span>
          <el-badge :value="getBugsByStatus(column.status).length" type="primary" />
        </div>
        <div class="column-content">
          <div
            v-for="bug in getBugsByStatus(column.status)"
            :key="bug.id"
            class="bug-card"
            :class="bug.priority"
            draggable="true"
            @dragstart="handleDragStart($event, bug)"
            @click="router.push(`/bugs/${bug.id}`)"
          >
            <div class="card-header">
              <span class="bug-id">#{{ bug.id }}</span>
              <el-tag :type="severityType[bug.severity]" size="small">{{ bug.severity_display }}</el-tag>
            </div>
            <div class="card-title">{{ bug.title }}</div>
            <div class="card-footer">
              <span class="creator">{{ bug.creator_name }}</span>
              <span v-if="bug.assignee_name" class="assignee">
                <el-icon><User /></el-icon>
                {{ bug.assignee_name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { getBugList, updateBugStatus } from '../api/bug'
import { getModuleCascade } from '../api/module'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const bugs = ref([])
const modules = ref([])

const filters = reactive({
  module: '',
  priority: ''
})

const columns = [
  { status: 'pending', title: '待处理' },
  { status: 'processing', title: '处理中' },
  { status: 'resolved', title: '已解决' },
  { status: 'rejected', title: '已驳回' },
  { status: 'closed', title: '已关闭' }
]

const severityType = {
  critical: 'danger',
  major: 'warning',
  minor: 'info',
  trivial: ''
}

const draggedBug = ref(null)

const fetchBugs = async () => {
  loading.value = true
  try {
    const params = { page_size: 1000 }
    if (filters.module) params.module = filters.module
    if (filters.priority) params.priority = filters.priority
    
    const res = await getBugList(params)
    bugs.value = res.results
  } finally {
    loading.value = false
  }
}

const fetchModules = async () => {
  try {
    const data = await getModuleCascade()
    const result = []
    const flattenModules = (items, path = '') => {
      items.forEach(item => {
        if (item.children && item.children.length > 0) {
          flattenModules(item.children, path ? `${path} / ${item.label}` : item.label)
        } else {
          result.push({
            id: item.value,
            path: path ? `${path} / ${item.label}` : item.label
          })
        }
      })
    }
    flattenModules(data)
    modules.value = result
  } catch (e) {
    // ignore
  }
}

const getBugsByStatus = (status) => {
  return bugs.value.filter(bug => bug.status === status)
}

const handleDragStart = (event, bug) => {
  draggedBug.value = bug
  event.dataTransfer.effectAllowed = 'move'
}

const handleDrop = async (event, newStatus) => {
  event.preventDefault()
  
  if (!draggedBug.value) return
  
  const bug = draggedBug.value
  const oldStatus = bug.status
  
  if (oldStatus === newStatus) {
    draggedBug.value = null
    return
  }
  
  if (newStatus === 'resolved') {
    try {
      await ElMessageBox.prompt('请输入解决说明', '解决BUG', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /\S+/,
        inputErrorMessage: '请输入解决说明'
      }).then(async ({ value }) => {
        await updateBugStatus(bug.id, { status: newStatus, solution: value })
        bug.status = newStatus
        ElMessage.success('状态更新成功')
      })
    } catch {
      // cancelled
    }
  } else if (newStatus === 'rejected') {
    try {
      await ElMessageBox.prompt('请输入驳回原因', '驳回BUG', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /\S+/,
        inputErrorMessage: '请输入驳回原因'
      }).then(async ({ value }) => {
        await updateBugStatus(bug.id, { status: newStatus, reject_reason: value })
        bug.status = newStatus
        ElMessage.success('状态更新成功')
      })
    } catch {
      // cancelled
    }
  } else {
    try {
      await updateBugStatus(bug.id, { status: newStatus })
      bug.status = newStatus
      ElMessage.success('状态更新成功')
    } catch (e) {
      // error handled by interceptor
    }
  }
  
  draggedBug.value = null
}

onMounted(() => {
  fetchBugs()
  fetchModules()
})
</script>

<style scoped>
.bug-kanban {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.kanban-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kanban-header h2 {
  margin: 0;
  font-size: 20px;
}

.kanban-actions {
  display: flex;
  gap: 12px;
}

.kanban-board {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 16px;
}

.kanban-column {
  flex: 0 0 280px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 200px);
}

.column-header {
  padding: 12px 16px;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.column-header.pending {
  background: #e6a23c;
  color: white;
}

.column-header.processing {
  background: #409eff;
  color: white;
}

.column-header.resolved {
  background: #67c23a;
  color: white;
}

.column-header.rejected {
  background: #f56c6c;
  color: white;
}

.column-header.closed {
  background: #909399;
  color: white;
}

.column-title {
  font-size: 14px;
}

.column-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  min-height: 100px;
}

.bug-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 3px solid transparent;
}

.bug-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.bug-card.high {
  border-left-color: #f56c6c;
}

.bug-card.medium {
  border-left-color: #e6a23c;
}

.bug-card.low {
  border-left-color: #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.bug-id {
  font-size: 12px;
  color: #909399;
  font-weight: 600;
}

.card-title {
  font-size: 14px;
  color: #303133;
  line-height: 1.4;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.assignee {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
