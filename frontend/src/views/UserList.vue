<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-form inline>
            <el-form-item label="角色">
              <el-select v-model="filters.role" placeholder="全部" clearable style="width: 120px" @change="fetchList">
                <el-option label="超级管理员" value="super_admin" />
                <el-option label="普通管理员" value="admin" />
                <el-option label="测试人员" value="tester" />
                <el-option label="开发人员" value="developer" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filters.status" placeholder="全部" clearable style="width: 100px" @change="fetchList">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="disabled" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-input v-model="filters.search" placeholder="搜索用户名" clearable @keyup.enter="fetchList" style="width: 180px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchList">搜索</el-button>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="openDialog()">新增用户</el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role_display" label="角色" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleToggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="info" @click="openPasswordDialog(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="fetchList" @current-change="fetchList" />
      </div>
    </el-card>

    <!-- 用户表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingUser ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="普通管理员" value="admin" />
            <el-option label="测试人员" value="tester" />
            <el-option label="开发人员" value="developer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="!editingUser">
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="form.confirm_password" type="password" show-password />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="passwordDialogVisible" title="重置密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleResetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser, resetUserPassword, toggleUserStatus } from '../api/user'

const loading = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  role: '',
  status: '',
  search: ''
})

const dialogVisible = ref(false)
const editingUser = ref(null)
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  username: '',
  email: '',
  phone: '',
  role: 'tester',
  status: 'active',
  password: '',
  confirm_password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 8 }],
  confirm_password: [{ required: true, message: '请确认密码', trigger: 'blur' }]
}

const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const resetUserId = ref(null)

const passwordForm = reactive({
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur', min: 8 }],
  confirm_password: [{ required: true, message: '请确认密码', trigger: 'blur' }]
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getUserList({
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

const openDialog = (user = null) => {
  editingUser.value = user
  if (user) {
    Object.assign(form, {
      username: user.username,
      email: user.email || '',
      phone: user.phone || '',
      role: user.role,
      status: user.status,
      password: '',
      confirm_password: ''
    })
  } else {
    Object.assign(form, {
      username: '',
      email: '',
      phone: '',
      role: 'tester',
      status: 'active',
      password: '',
      confirm_password: ''
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingUser.value) {
      await updateUser(editingUser.value.id, {
        email: form.email,
        phone: form.phone,
        role: form.role,
        status: form.status
      })
      ElMessage.success('更新成功')
    } else {
      await createUser(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

const handleToggleStatus = async (user) => {
  await ElMessageBox.confirm(
    `确定要${user.status === 'active' ? '禁用' : '启用'}用户 ${user.username} 吗？`,
    '提示',
    { type: 'warning' }
  )
  await toggleUserStatus(user.id)
  ElMessage.success('操作成功')
  fetchList()
}

const handleDelete = async (user) => {
  await ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '警告', { type: 'error' })
  await deleteUser(user.id)
  ElMessage.success('删除成功')
  fetchList()
}

const openPasswordDialog = (user) => {
  resetUserId.value = user.id
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

const handleResetPassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次密码输入不一致')
    return
  }

  submitting.value = true
  try {
    await resetUserPassword(resetUserId.value, passwordForm)
    ElMessage.success('密码重置成功')
    passwordDialogVisible.value = false
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
