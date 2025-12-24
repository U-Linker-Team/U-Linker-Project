import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/css/tailwind.css'

// 注意：不再在这里全局配置 axios
// 所有 API 请求应该使用封装的 request.js

const app = createApp(App)

//先创建并安装Pinia
const pinia = createPinia()
app.use(pinia)

//然后再安装router
app.use(router)
app.mount('#app')

console.log('✅ Tailwind CSS已导入')
console.log('✅ 应用初始化完成')