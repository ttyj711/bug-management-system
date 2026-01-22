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
            <el-button @click="openEditDialog" v-if="canEdit">编辑</el-button>
            <el-button type="primary" @click="showStatusDialog = true" v-if="canChangeStatus">修改状态</el-button>
            <el-button type="warning" @click="showAssignDialog = true" v-if="canAssign">分配</el-button>
            <el-button type="info" @click="handleCopyBug">复制BUG</el-button>
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
    
    <!-- 编辑BUG弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑BUG" width="700px">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入BUG标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="editForm.severity" style="width: 100%">
                <el-option label="致命" value="critical" />
                <el-option label="严重" value="major" />
                <el-option label="一般" value="minor" />
                <el-option label="轻微" value="trivial" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="editForm.priority" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="处理人">
              <el-select v-model="editForm.assignee" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="dev in developers" :key="dev.id" :label="dev.username" :value="dev.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="所属模块">
              <el-cascader
                v-model="editForm.moduleCascade"
                :options="moduleCascadeOptions"
                :props="{ value: 'value', label: 'label', children: 'children' }"
                placeholder="请选择项目/产品/模块"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="版本号">
              <el-input v-model="editForm.version" placeholder="请输入版本号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="问题描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="5" placeholder="请详细描述BUG的复现步骤、预期结果和实际结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEditSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBug, updateBugStatus, assignBug, copyBug, updateBug } from '../api/bug'
import { getDevelopers } from '../api/user'
import { getModuleCascade } from '../api/module'
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

// 编辑BUG
const showEditDialog = ref(false)
const editFormRef = ref(null)
const moduleCascadeOptions = ref([])
const editForm = reactive({ 
  title: '', 
  description: '', 
  severity: 'minor', 
  priority: 'medium', 
  moduleCascade: [], 
  version: '', 
  assignee: null 
})

const editRules = {
  title: [{ required: true, message: '请输入BUG标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

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

const fetchModuleCascade = async () => {
  try {
    moduleCascadeOptions.value = await getModuleCascade()
  } catch (error) {
    console.error('获取模块层级失败:', error)
  }
}

// 打开编辑对话框
const openEditDialog = () => {
  if (!bug.value) return
  
  // 填充表单数据
  Object.assign(editForm, {
    title: bug.value.title,
    description: bug.value.description,
    severity: bug.value.severity,
    priority: bug.value.priority,
    moduleCascade: bug.value.module_cascade || [],
    version: bug.value.version || '',
    assignee: bug.value.assignee
  })
  
  showEditDialog.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('title', editForm.title)
    formData.append('description', editForm.description)
    formData.append('severity', editForm.severity)
    formData.append('priority', editForm.priority)
    formData.append('version', editForm.version || '')
    
    // 处理级联选择的模块ID（取最后一级的ID）
    if (editForm.moduleCascade && editForm.moduleCascade.length === 3) {
      formData.append('module', editForm.moduleCascade[2])
    } else {
      formData.append('module', '')
    }
    
    if (editForm.assignee) {
      formData.append('assignee', editForm.assignee)
    }
    
    await updateBug(bug.value.id, formData)
    ElMessage.success('编辑成功')
    showEditDialog.value = false
    fetchBug() // 重新获取最新数据
  } catch (error) {
    console.error('编辑BUG失败:', error)
    ElMessage.error('编辑失败')
  } finally {
    submitting.value = false
  }
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

const handleCopyBug = async () => {
  submitting.value = true
  try {
    const copyData = await copyBug(bug.value.id)
    // 将复制的数据存储到会话存储中，供创建页面使用
    sessionStorage.setItem('copiedBugData', JSON.stringify(copyData))
    // 跳转到BUG列表页，自动打开创建对话框
    router.push('/bugs?copy=true')
    ElMessage.success('BUG复制成功，可直接修改后提交')
  } catch (error) {
    ElMessage.error('复制BUG失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchBug()
  fetchDevelopers()
  fetchModuleCascade()
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
