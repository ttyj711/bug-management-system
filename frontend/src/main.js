import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'  // 注意这里路径可能略有不同，也可以用下面那行
// import zhCn from 'element-plus/lib/locale/lang/zh-cn' 

import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

import './style.css'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// ✅ 正确配置 Element Plus 中文语言包
app.use(ElementPlus, { 
  locale: zhCn  // 使用 Element Plus 的中文语言包
})

app.use(createPinia())
app.use(router)
app.mount('#app')