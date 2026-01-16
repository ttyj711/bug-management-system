<template>
  <div class="bug-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑BUG' : '提报BUG' }}</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-loading="loading">
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
          <el-col :span="12">
            <el-form-item label="所属模块">
              <el-input v-model="form.module" placeholder="请输入所属模块" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="版本号">
              <el-input v-model="form.version" placeholder="请输入版本号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="问题描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="6" placeholder="请详细描述BUG的复现步骤、预期结果和实际结果" />
        </el-form-item>

        <el-form-item label="附件截图">
          <el-upload ref="uploadRef" :auto-upload="false" :file-list="fileList" list-type="picture-card" :on-change="handleFileChange" :on-remove="handleFileRemove" accept="image/*" multiple>
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <div class="existing-attachments" v-if="isEdit && existingAttachments.length">
          <h4>已有附件</h4>
          <div class="attachment-list">
            <div v-for="att in existingAttachments" :key="att.id" class="attachment-item">
              <el-image :src="att.file" fit="cover" class="attachment-img" :preview-src-list="existingAttachments.map(a => a.file)" />
              <el-button type="danger" size="small" circle class="delete-btn" @click="handleDeleteAttachment(att.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBug, createBug, updateBug, deleteAttachment } from '../api/bug'
import { getDevelopers } from '../api/user'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const uploadRef = ref(null)

const form = reactive({
  title: '',
  description: '',
  severity: 'minor',
  priority: 'medium',
  module: '',
  version: '',
  assignee: null
})

const rules = {
  title: [{ required: true, message: '请输入BUG标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

const developers = ref([])
const fileList = ref([])
const existingAttachments = ref([])

const fetchDevelopers = async () => {
  developers.value = await getDevelopers()
}

const fetchBug = async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const bug = await getBug(route.params.id)
    Object.assign(form, {
      title: bug.title,
      description: bug.description,
      severity: bug.severity,
      priority: bug.priority,
      module: bug.module || '',
      version: bug.version || '',
      assignee: bug.assignee
    })
    existingAttachments.value = bug.attachments || []
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const handleDeleteAttachment = async (attachmentId) => {
  await deleteAttachment(route.params.id, attachmentId)
  existingAttachments.value = existingAttachments.value.filter(a => a.id !== attachmentId)
  ElMessage.success('删除成功')
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const formData = new FormData()
    Object.keys(form).forEach(key => {
      if (form[key] !== null && form[key] !== '') {
        formData.append(key, form[key])
      }
    })
    
    fileList.value.forEach(file => {
      if (file.raw) {
        formData.append('attachments', file.raw)
      }
    })

    if (isEdit.value) {
      await updateBug(route.params.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createBug(formData)
      ElMessage.success('提报成功')
    }
    router.push('/bugs')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDevelopers()
  fetchBug()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.existing-attachments {
  margin-bottom: 20px;
}

.existing-attachments h4 {
  margin-bottom: 10px;
  color: #606266;
}

.attachment-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.attachment-item {
  position: relative;
}

.attachment-img {
  width: 100px;
  height: 100px;
  border-radius: 4px;
}

.delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
}
</style>
