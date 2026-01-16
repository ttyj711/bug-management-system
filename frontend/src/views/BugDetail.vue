<template>
  <div class="bug-detail" v-loading="loading">
    <el-card v-if="bug">
      <template #header>
        <div class="card-header">
          <div class="title-section">
            <el-tag :type="severityType[bug.severity]" size="large">{{ bug.severity_display }}</el-tag>
            <el-tag :type="statusType[bug.status]" size="large">{{ bug.status_display }}</el-tag>
            <h2 class="bug-title">{{ bug.title }}</h2>
          </div>
          <div class="actions">
            <el-button @click="router.push('/bugs')" v-if="canEdit">编辑</el-button>
            <el-button type="primary" @click="showStatusDialog = true" v-if="canChangeStatus">修改状态</el-button>
            <el-button type="warning" @click="showAssignDialog = true" v-if="canAssign">分配</el-button>
            <el-button @click="router.back()">返回</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="BUG ID">{{ bug.id }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="priorityType[bug.priority]" size="small">{{ bug.priority_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="所属模块">{{ bug.module_path || '-' }}</el-descriptions-item>
        <el-descriptions-item label="版本号">{{ bug.version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ bug.creator_name }}</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ bug.assignee_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(bug.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(bug.updated_at) }}</el-descriptions-item>
      </el-descriptions>

      <div class="section">
        <h3>问题描述</h3>
        <div class="content-box">{{ bug.description }}</div>
      </div>

      <div class="section" v-if="bug.solution">
        <h3>解决说明</h3>
        <div class="content-box success">{{ bug.solution }}</div>
      </div>

      <div class="section" v-if="bug.reject_reason">
        <h3>驳回原因</h3>
        <div class="content-box danger">{{ bug.reject_reason }}</div>
      </div>

      <div class="section" v-if="bug.attachments && bug.attachments.length">
        <h3>附件截图</h3>
        <div class="attachments">
          <el-image v-for="att in bug.attachments" :key="att.id" :src="att.file" :preview-src-list="bug.attachments.map(a => a.file)" fit="cover" class="attachment-img" />
        </div>
      </div>
    </el-card>

    <!-- 状态修改弹窗 -->
    <el-dialog v-model="showStatusDialog" title="修改状态" width="500px">
      <el-form ref="statusFormRef" :model="statusForm" :rules="statusRules" label-width="80px">
        <el-form-item label="状态" prop="status">
          <el-select v-model="statusForm.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="解决说明" prop="solution" v-if="statusForm.status === 'resolved'">
          <el-input v-model="statusForm.solution" type="textarea" :rows="4" placeholder="请输入解决说明" />
        </el-form-item>
        <el-form-item label="驳回原因" prop="reject_reason" v-if="statusForm.status === 'rejected'">
          <el-input v-model="statusForm.reject_reason" type="textarea" :rows="4" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleStatusChange">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配弹窗 -->
    <el-dialog v-model="showAssignDialog" title="分配处理人" width="400px">
      <el-form label-width="80px">
        <el-form-item label="处理人">
          <el-select v-model="assigneeId" placeholder="请选择开发人员" style="width: 100%">
            <el-option v-for="dev in developers" :key="dev.id" :label="dev.username" :value="dev.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBug, updateBugStatus, assignBug } from '../api/bug'
import { getDevelopers } from '../api/user'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const bug = ref(null)
const submitting = ref(false)

const severityType = { critical: 'danger', major: 'warning', minor: 'info', trivial: '' }
const priorityType = { high: 'danger', medium: 'warning', low: 'info' }
const statusType = { pending: 'info', processing: 'warning', resolved: 'success', rejected: 'danger', closed: '' }

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : ''

const canEdit = computed(() => {
  if (!bug.value) return false
  if (userStore.isSuperAdmin) return true
  if (userStore.isTester && bug.value.creator === userStore.user?.id && bug.value.status === 'pending') return true
  return false
})

const canChangeStatus = computed(() => {
  if (!bug.value) return false
  if (userStore.isSuperAdmin) return true
  if (userStore.isDeveloper && bug.value.assignee === userStore.user?.id) return true
  return false
})

const canAssign = computed(() => userStore.isAdmin)

// 状态修改
const showStatusDialog = ref(false)
const statusFormRef = ref(null)
const statusForm = reactive({ status: '', solution: '', reject_reason: '' })
const statusRules = {
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  solution: [{ required: true, message: '请输入解决说明', trigger: 'blur' }],
  reject_reason: [{ required: true, message: '请输入驳回原因', trigger: 'blur' }]
}

// 分配
const showAssignDialog = ref(false)
const developers = ref([])
const assigneeId = ref(null)

const fetchBug = async () => {
  loading.value = true
  try {
    bug.value = await getBug(route.params.id)
    statusForm.status = bug.value.status
  } finally {
    loading.value = false
  }
}

const fetchDevelopers = async () => {
  developers.value = await getDevelopers()
}

const handleStatusChange = async () => {
  const valid = await statusFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await updateBugStatus(bug.value.id, statusForm)
    ElMessage.success('状态更新成功')
    showStatusDialog.value = false
    fetchBug()
  } finally {
    submitting.value = false
  }
}

const handleAssign = async () => {
  if (!assigneeId.value) {
    ElMessage.warning('请选择处理人')
    return
  }
  submitting.value = true
  try {
    await assignBug(bug.value.id, { assignee: assigneeId.value })
    ElMessage.success('分配成功')
    showAssignDialog.value = false
    fetchBug()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchBug()
  fetchDevelopers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 15px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.bug-title {
  margin: 0;
  font-size: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.section {
  margin-top: 24px;
}

.section h3 {
  margin-bottom: 12px;
  font-size: 16px;
  color: #303133;
}

.content-box {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.content-box.success {
  background: #f0f9eb;
  border-left: 4px solid #67c23a;
}

.content-box.danger {
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
}

.attachments {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.attachment-img {
  width: 150px;
  height: 150px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
