<template>
  <div class="module-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目-产品-模块管理</span>
          <el-button type="primary" @click="openProjectDialog()" v-if="userStore.isSuperAdmin">新增项目</el-button>
        </div>
      </template>

      <el-tree
        :data="treeData"
        :props="{ label: 'name', children: 'children' }"
        default-expand-all
        :expand-on-click-node="false"
        v-loading="loading"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">
              <el-tag :type="getNodeType(data)" size="small">{{ getNodeTag(data) }}</el-tag>
              {{ data.name }}
              <el-tag v-if="!data.is_active" type="info" size="small">已禁用</el-tag>
            </span>
            <span class="node-actions" v-if="userStore.isSuperAdmin">
              <el-button size="small" link type="primary" @click.stop="handleAdd(data)">
                {{ getAddText(data) }}
              </el-button>
              <el-button size="small" link type="primary" @click.stop="handleEdit(data)">编辑</el-button>
              <el-button size="small" link type="danger" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </el-card>

    <!-- 项目弹窗 -->
    <el-dialog v-model="projectDialogVisible" :title="editingProject ? '编辑项目' : '新增项目'" width="500px">
      <el-form ref="projectFormRef" :model="projectForm" :rules="formRules" label-width="80px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="projectForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="projectForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitProject">确定</el-button>
      </template>
    </el-dialog>

    <!-- 产品弹窗 -->
    <el-dialog v-model="productDialogVisible" :title="editingProduct ? '编辑产品' : '新增产品'" width="500px">
      <el-form ref="productFormRef" :model="productForm" :rules="formRules" label-width="80px">
        <el-form-item label="所属项目">
          <el-input :value="currentProjectName" disabled />
        </el-form-item>
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="productForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="productForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitProduct">确定</el-button>
      </template>
    </el-dialog>

    <!-- 模块弹窗 -->
    <el-dialog v-model="moduleDialogVisible" :title="editingModule ? '编辑模块' : '新增模块'" width="500px">
      <el-form ref="moduleFormRef" :model="moduleForm" :rules="formRules" label-width="80px">
        <el-form-item label="所属产品">
          <el-input :value="currentProductName" disabled />
        </el-form-item>
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="moduleForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="moduleForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitModule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProjectList, createProject, updateProject, deleteProject,
  getProductList, createProduct, updateProduct, deleteProduct,
  getModuleList, createModule, updateModule, deleteModule
} from '../api/module'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const treeData = ref([])

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

// 项目
const projectDialogVisible = ref(false)
const projectFormRef = ref(null)
const editingProject = ref(null)
const projectForm = reactive({ name: '', description: '', is_active: true })

// 产品
const productDialogVisible = ref(false)
const productFormRef = ref(null)
const editingProduct = ref(null)
const currentProjectId = ref(null)
const currentProjectName = ref('')
const productForm = reactive({ name: '', description: '', is_active: true, project: null })

// 模块
const moduleDialogVisible = ref(false)
const moduleFormRef = ref(null)
const editingModule = ref(null)
const currentProductId = ref(null)
const currentProductName = ref('')
const moduleForm = reactive({ name: '', description: '', is_active: true, product: null })

const getNodeType = (data) => {
  if (data.type === 'project') return 'primary'
  if (data.type === 'product') return 'success'
  return 'warning'
}

const getNodeTag = (data) => {
  if (data.type === 'project') return '项目'
  if (data.type === 'product') return '产品'
  return '模块'
}

const getAddText = (data) => {
  if (data.type === 'project') return '添加产品'
  if (data.type === 'product') return '添加模块'
  return ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const projects = await getProjectList()
    const products = await getProductList()
    const modules = await getModuleList()

    // 构建树形结构
    const tree = (projects.results || projects).map(project => ({
      ...project,
      type: 'project',
      children: (products.results || products)
        .filter(p => p.project === project.id)
        .map(product => ({
          ...product,
          type: 'product',
          projectName: project.name,
          children: (modules.results || modules)
            .filter(m => m.product === product.id)
            .map(module => ({
              ...module,
              type: 'module',
              productName: product.name
            }))
        }))
    }))
    treeData.value = tree
  } finally {
    loading.value = false
  }
}

// 项目操作
const openProjectDialog = (project = null) => {
  editingProject.value = project
  if (project) {
    Object.assign(projectForm, { name: project.name, description: project.description || '', is_active: project.is_active })
  } else {
    Object.assign(projectForm, { name: '', description: '', is_active: true })
  }
  projectDialogVisible.value = true
}

const submitProject = async () => {
  const valid = await projectFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, projectForm)
      ElMessage.success('更新成功')
    } else {
      await createProject(projectForm)
      ElMessage.success('创建成功')
    }
    projectDialogVisible.value = false
    fetchData()
  } finally {
    submitting.value = false
  }
}

// 产品操作
const openProductDialog = (projectId, projectName, product = null) => {
  currentProjectId.value = projectId
  currentProjectName.value = projectName
  editingProduct.value = product
  if (product) {
    Object.assign(productForm, { name: product.name, description: product.description || '', is_active: product.is_active, project: projectId })
  } else {
    Object.assign(productForm, { name: '', description: '', is_active: true, project: projectId })
  }
  productDialogVisible.value = true
}

const submitProduct = async () => {
  const valid = await productFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingProduct.value) {
      await updateProduct(editingProduct.value.id, productForm)
      ElMessage.success('更新成功')
    } else {
      await createProduct(productForm)
      ElMessage.success('创建成功')
    }
    productDialogVisible.value = false
    fetchData()
  } finally {
    submitting.value = false
  }
}

// 模块操作
const openModuleDialog = (productId, productName, module = null) => {
  currentProductId.value = productId
  currentProductName.value = productName
  editingModule.value = module
  if (module) {
    Object.assign(moduleForm, { name: module.name, description: module.description || '', is_active: module.is_active, product: productId })
  } else {
    Object.assign(moduleForm, { name: '', description: '', is_active: true, product: productId })
  }
  moduleDialogVisible.value = true
}

const submitModule = async () => {
  const valid = await moduleFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingModule.value) {
      await updateModule(editingModule.value.id, moduleForm)
      ElMessage.success('更新成功')
    } else {
      await createModule(moduleForm)
      ElMessage.success('创建成功')
    }
    moduleDialogVisible.value = false
    fetchData()
  } finally {
    submitting.value = false
  }
}

// 通用操作
const handleAdd = (data) => {
  if (data.type === 'project') {
    openProductDialog(data.id, data.name)
  } else if (data.type === 'product') {
    openModuleDialog(data.id, data.name)
  }
}

const handleEdit = (data) => {
  if (data.type === 'project') {
    openProjectDialog(data)
  } else if (data.type === 'product') {
    openProductDialog(data.project, data.projectName, data)
  } else {
    openModuleDialog(data.product, data.productName, data)
  }
}

const handleDelete = async (data) => {
  const typeText = getNodeTag(data)
  await ElMessageBox.confirm(`确定要删除${typeText} "${data.name}" 吗？`, '警告', { type: 'error' })
  
  if (data.type === 'project') {
    await deleteProject(data.id)
  } else if (data.type === 'product') {
    await deleteProduct(data.id)
  } else {
    await deleteModule(data.id)
  }
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 10px;
}

.node-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-actions {
  display: none;
}

.tree-node:hover .node-actions {
  display: inline-flex;
}
</style>
