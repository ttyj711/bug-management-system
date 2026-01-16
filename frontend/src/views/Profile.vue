<template>
  <div class="profile">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>个人信息</template>
          <el-form ref="profileFormRef" :model="profileForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="角色">
              <el-input v-model="profileForm.role_display" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="profileLoading" @click="handleUpdateProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>修改密码</template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile, changePassword } from '../api/user'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const profileFormRef = ref(null)
const profileLoading = ref(false)
const profileForm = reactive({
  username: '',
  role_display: '',
  email: '',
  phone: ''
})

const passwordFormRef = ref(null)
const passwordLoading = ref(false)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' }
  ],
  confirm_password: [{ required: true, message: '请确认新密码', trigger: 'blur' }]
}

const fetchProfile = async () => {
  const res = await getProfile()
  Object.assign(profileForm, res)
}

const handleUpdateProfile = async () => {
  profileLoading.value = true
  try {
    await updateProfile({
      email: profileForm.email,
      phone: profileForm.phone
    })
    ElMessage.success('更新成功')
    userStore.fetchProfile()
  } finally {
    profileLoading.value = false
  }
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次密码输入不一致')
    return
  }

  passwordLoading.value = true
  try {
    await changePassword(passwordForm)
    ElMessage.success('密码修改成功，请重新登录')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    userStore.logout()
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile {
  max-width: 1000px;
}
</style>
