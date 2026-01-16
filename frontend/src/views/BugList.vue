<template>
  <div class="bug-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-form inline>
            <el-form-item label="状态">
              <el-select v-model="filters.status" placeholder="全部" clearable style="width: 110px" @change="fetchList">
                <el-option label="待处理" value="pending" />
                <el-option label="处理中" value="processing" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已驳回" value="rejected" />
                <el-option label="已关闭" value="closed" />
              </el-select>
            </el-form-item>
            <el-form-item label="严重程度">
              <el-select v-model="filters.severity" placeholder="全部" clearable style="width: 100px" @change="fetchList">
                <el-option label="致命" value="critical" />
                <el-option label="严重" value="major" />
                <el-option label="一般" value="minor" />
                <el-option label="轻微" value="trivial" />
              </el-select>
            </el-form-item>
            <el-form-item label="优先级">
              <el-select v-model="filters.priority" placeholder="全部" clearable style="width: 80px" @change="fetchList">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
            <el-form-item label="我的BUG">
              <el-select v-model="filters.my_bugs" placeholder="全部" clearable style="width: 120px" @change="fetchList">
                <el-option label="我创建的" value="created" />
                <el-option label="分配给我的" value="assigned" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-input v-model="filters.search" placeholder="搜索标题/描述" clearable @keyup.enter="fetchList" style="width: 180px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchList">搜索</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="openCreateDialog" v-if="userStore.hasPermission('bug:create')">
            提报BUG
          </el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe @row-click="handleRowClick" style="cursor: pointer">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="severity_display" label="严重程度" width="90">
          <template #default="{ row }">
            <el-tag :type="severityType[row.severity]" size="small">{{ row.severity_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority_display" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="priorityType[row.priority]" size="small">{{ row.priority_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module_path" label="所属模块" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.module_path || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建人" width="90" />
        <el-table-column prop="assignee_name" label="处理人" width="90">
          <template #default="{ row }">
            {{ row.assignee_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click.stop="router.push(`/bugs/${row.id}`)">查看</el-button>
            <el-button size="small" link type="primary" @click.stop="openEditDialog(row)" v-if="canEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click.stop="handleDelete(row)" v-if="userStore.isSuperAdmin">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="fetchList" @current-change="fetchList" />
      </div>
    </el-card>

    <!-- 提报/编辑BUG弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingBug ? '编辑BUG' : '提报BUG'" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入BUG标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="form.severity" style="width: 100%">
                <el-option label="致命" value="critical" />
                <el-option label="严重" value="major" />
                <el-option label="一般" value="minor" />
                <el-option label="轻微" value="trivial" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="处理人">
              <el-select v-model="form.assignee" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="dev in developers" :key="dev.id" :label="dev.username" :value="dev.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="所属模块">
              <el-cascader
                v-model="form.moduleCascade"
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
              <el-input v-model="form.version" placeholder="请输入版本号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="问题描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请详细描述BUG的复现步骤、预期结果和实际结果" />
        </el-form-item>

        <el-form-item label="附件截图">
          <el-upload ref="uploadRef" :auto-upload="false" :file-list="fileList" list-type="picture-card" :on-change="handleFileChange" :on-remove="handleFileRemove" accept="image/*" multiple>
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBugList, getBug, createBug, updateBug, deleteBug } from '../api/bug'
import { getDevelopers } from '../api/user'
import { getModuleCascade } from '../api/module'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  status: '',
  severity: '',
  priority: '',
  my_bugs: '',
  search: ''
})

const severityType = {
  critical: 'danger',
  major: 'warning',
  minor: 'info',
  trivial: ''
}

const priorityType = {
  high: 'danger',
  medium: 'warning',
  low: 'info'
}

const statusType = {
  pending: 'info',
  processing: 'warning',
  resolved: 'success',
  rejected: 'danger',
  closed: ''
}

// 弹窗相关
const dialogVisible = ref(false)
const editingBug = ref(null)
const formRef = ref(null)
const submitting = ref(false)
const developers = ref([])
const fileList = ref([])
const moduleCascadeOptions = ref([])

const form = reactive({
  title: '',
  description: '',
  severity: 'minor',
  priority: 'medium',
  moduleCascade: [],
  version: '',
  assignee: null
})

const rules = {
  title: [{ required: true, message: '请输入BUG标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getBugList({
      page: page.value,
      page_size: pageSize.value,
      ...filters
    })
    list.value = res.results
    total.value = res.count
  } finally {
    loading.value = false
  }
}

const fetchDevelopers = async () => {
  try {
    developers.value = await getDevelopers()
  } catch (e) {
    // ignore
  }
}

const fetchModuleCascade = async () => {
  try {
    moduleCascadeOptions.value = await getModuleCascade()
  } catch (e) {
    // ignore
  }
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => filters[key] = '')
  fetchList()
}

const canEdit = (bug) => {
  if (userStore.isSuperAdmin) return true
  if (userStore.isTester && bug.creator === userStore.user?.id && bug.status === 'pending') return true
  return false
}

const handleRowClick = (row) => {
  router.push(`/bugs/${row.id}`)
}

const handleDelete = async (bug) => {
  await ElMessageBox.confirm(`确定要删除BUG "${bug.title}" 吗？`, '警告', { type: 'error' })
  await deleteBug(bug.id)
  ElMessage.success('删除成功')
  fetchList()
}

// 打开创建弹窗
const openCreateDialog = () => {
  editingBug.value = null
  Object.assign(form, {
    title: '',
    description: '',
    severity: 'minor',
    priority: 'medium',
    moduleCascade: [],
    version: '',
    assignee: null
  })
  fileList.value = []
  dialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = async (bug) => {
  editingBug.value = bug
  try {
    const detail = await getBug(bug.id)
    Object.assign(form, {
      title: detail.title,
      description: detail.description,
      severity: detail.severity,
      priority: detail.priority,
      moduleCascade: detail.module_cascade || [],
      version: detail.version || '',
      assignee: detail.assignee
    })
    fileList.value = []
    dialogVisible.value = true
  } catch (e) {
    // error handled by interceptor
  }
}

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('description', form.description)
    formData.append('severity', form.severity)
    formData.append('priority', form.priority)
    formData.append('version', form.version || '')
    
    // 处理级联选择的模块ID（取最后一级的ID）
    if (form.moduleCascade && form.moduleCascade.length === 3) {
      formData.append('module', form.moduleCascade[2])
    }
    
    if (form.assignee) {
      formData.append('assignee', form.assignee)
    }
    
    fileList.value.forEach(file => {
      if (file.raw) {
        formData.append('attachments', file.raw)
      }
    })

    if (editingBug.value) {
      await updateBug(editingBug.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createBug(formData)
      ElMessage.success('提报成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchList()
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
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
