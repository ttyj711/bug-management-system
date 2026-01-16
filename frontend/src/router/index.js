import { createRouter, createWebHistory } from 'vue-router'
import Cookies from 'js-cookie'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/bugs'
      },
      {
        path: 'bugs',
        name: 'BugList',
        component: () => import('../views/BugList.vue'),
        meta: { title: 'BUG列表' }
      },

      {
        path: 'bugs/:id',
        name: 'BugDetail',
        component: () => import('../views/BugDetail.vue'),
        meta: { title: 'BUG详情' }
      },

      {
        path: 'users',
        name: 'UserList',
        component: () => import('../views/UserList.vue'),
        meta: { title: '账号管理', requiresAdmin: true }
      },
      {
        path: 'modules',
        name: 'ModuleManage',
        component: () => import('../views/ModuleManage.vue'),
        meta: { title: '模块管理' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人信息' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = Cookies.get('access_token')
  
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
