<!-- 登录 -->

<template>
  <div class="login-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      
      <!-- 顶部标题栏 -->
      <header class="header-bar">
        <span class="app-title">U-Linker</span>
        <button class="help-btn">
          <!-- 修改为更精确的问号图标 -->
        <span class="iconify help-icon" data-icon="mdi:help-circle-outline"></span>
        </button>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <div class="content-wrapper">
          
          <!-- 图标和欢迎语 -->
          <div class="welcome-section">
            <div class="avatar-container">
              <!-- 使用与HTML中mdi:account-group完全相同的图标 -->
              <svg class="avatar-icon" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12,5.5A3.5,3.5 0 0,1 15.5,9A3.5,3.5 0 0,1 12,12.5A3.5,3.5 0 0,1 8.5,9A3.5,3.5 0 0,1 12,5.5M5,8C5.56,8 6.08,8.15 6.53,8.42C6.38,9.85 6.8,11.27 7.66,12.38C7.16,13.34 6.16,14 5,14A3,3 0 0,1 2,11A3,3 0 0,1 5,8M19,8A3,3 0 0,1 22,11A3,3 0 0,1 19,14C17.84,14 16.84,13.34 16.34,12.38C17.2,11.27 17.62,9.85 17.47,8.42C17.92,8.15 18.44,8 19,8M5.5,18.25C5.5,16.18 8.41,14.5 12,14.5C15.59,14.5 18.5,16.18 18.5,18.25V20H5.5V18.25M0,20V18.5C0,17.11 1.89,15.94 4.45,15.6C3.86,16.28 3.5,17.22 3.5,18.25V20H0M24,20H20.5V18.25C20.5,17.22 20.14,16.28 19.55,15.6C22.11,15.94 24,17.11 24,18.5V20Z"/>
              </svg>
            </div>
            <h2 class="welcome-title">欢迎使用U-Linker</h2>
            <p class="welcome-subtitle">校园互助平台，连接你的校园生活</p>
          </div>

          <!-- 登录表单 -->
          <div class="form-section">
            
            <!-- 学工号/手机号输入 -->
            <div class="input-container">
              <div class="input-label">学号</div>
              <input 
                v-model="form.username"
                type="text" 
                class="form-input"
                placeholder="请输入学号"
              >
            </div>

            <!-- 密码输入 -->
            <div class="input-container">
              <div class="input-label">密码</div>
              <input 
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="请输入密码"
              >
              <button 
                type="button"
                class="password-toggle"
                @click="togglePasswordVisibility"
              >
                <svg class="eye-icon" viewBox="0 0 24 24" fill="none" v-if="!showPassword" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg class="eye-icon" viewBox="0 0 24 24" fill="none" v-else xmlns="http://www.w3.org/2000/svg">
                  <path d="M14.12 14.12C13.8454 14.4148 13.5141 14.6512 13.1462 14.8151C12.7782 14.9791 12.3809 15.0673 11.9781 15.0744C11.5753 15.0815 11.1752 15.0074 10.8016 14.8565C10.4281 14.7056 10.0887 14.481 9.80385 14.1962C9.51897 13.9113 9.29439 13.5719 9.14351 13.1984C8.99262 12.8248 8.91853 12.4247 8.92563 12.0219C8.93274 11.6191 9.02091 11.2218 9.18488 10.8538C9.34884 10.4859 9.58525 10.1546 9.88 9.88M17.94 17.94C16.2306 19.243 14.1491 19.9649 12 20C5 20 1 12 1 12C2.80448 10.2466 3.9999 8.68329 5.5 7.5M9.9 4.24C10.5883 4.07888 11.2931 3.99834 12 4C19 4 23 12 23 12C21.393 13.1356 20.6691 14.2048 19.84 15.19M1 1L23 23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>

            <!-- 登录按钮 -->
            <button 
              @click="handleLogin"
              class="login-button"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">登录</span>
              <span v-else class="loading">
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
              </span>
            </button>

            <!-- 注册和忘记密码 -->
            <div class="action-links">
              <button @click="goToRegister" class="link-button register-link">
                注册账号
              </button>
              <button @click="forgotPassword" class="link-button forgot-link">
                忘记密码？
              </button>
            </div>
          </div>

        </div>
      </main>

      <!-- 移除了底部导航栏 -->
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// --- 1. 数据定义 (完全保留) ---
const form = reactive({
  username: '',
  password: ''
})

const showPassword = ref(false)
const isLoading = ref(false) // 控制按钮转圈圈，必须保留

// --- 2. 纯 UI 方法 (完全保留) ---
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// --- 3. 登录逻辑 (深度修改：保留校验，替换请求) ---
const handleLogin = async () => {
  // [保留] 基础非空校验
  if (!form.username || !form.password) {
    alert('请填写完整的登录信息')
    return
  }

  // [保留] 学号格式校验 (虽然后端也会验，但前端先验可以省流量)
  if (!/^\d{9}$/.test(form.username)) {
    alert('学号必须是9位数字')
    return
  }
  
  // [保留] 密码长度校验
  if (form.password.length < 8) {
    alert('密码长度至少8位')
    return
  }
  
  // [保留] 开启加载动画 (让按钮变灰，显示转圈)
  isLoading.value = true
  
  try {
    // -----------------------------------------------------------
    // [删除] 原来的 setTimeout 和 localStorage 逻辑
    // [新增] 调用真实的 Python 后端接口
    // -----------------------------------------------------------
    const res = await login({
      username: form.username,
      password: form.password
    })
    
    // 登录成功！
    console.log('登录成功:', res)
    
    // [新增] 把用户信息存入 Pinia (状态管理)，供个人中心使用
    // 注意：假设后端返回格式是 { data: { user: {...} } }
    if (res.data && res.data.user) {
      userStore.login(res.data.user)
    }
    
    // [修改] 跳转到我们在 router 里配置好的首页路径 '/home'
    router.push('/home')

  } catch (error) {
    // 登录失败 (密码错误等)
    // request.js 拦截器通常会弹窗提示，这里我们只需要处理 UI
    console.error('登录请求失败', error)
  } finally {
    // [保留] 无论成功失败，都要关闭加载动画，让按钮恢复可点状态
    isLoading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

const forgotPassword = () => {
  alert('忘记密码功能开发中...')
}
</script>

<style scoped>
/* 基础样式 - 与HTML完全一致 */
.login-container {
  min-height: 100vh;
  background-color: #f3f4f6; /* bg-gray-100 */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem; /* p-4 */
}

/* 移动端容器 - 与HTML完全一致 */
.mobile-frame {
  width: 375px;
  height: 812px;
  background-color: white;
  border-radius: 0.75rem; /* rounded-xl */
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); /* shadow-lg */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 1. 顶部标题栏 - 与HTML完全一致 */
.header-bar {
  height: 4rem; /* h-16 */
  padding: 0 1rem; /* px-4 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb; /* border-gray-200 */
  background: white;
}

.app-title {
  font-size: 1.125rem; /* text-lg */
  font-weight: 700; /* font-bold */
  color: #2563eb; /* text-blue-600 */
  letter-spacing: -0.025em;
}

.help-btn {
  width: 1.5rem; /* w-6 */
  height: 1.5rem; /* h-6 */
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.help-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #2563eb; /* text-blue-600 */
}

/* 2. 主内容区域 - 与HTML完全一致 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem; /* px-6 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 隐藏滚动条 */
.main-content::-webkit-scrollbar {
  display: none;
}

.main-content {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.content-wrapper {
  width: 100%;
  max-width: 28rem; /* max-w-md */
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* space-y-6 */
}

/* 欢迎区域 - 与HTML完全一致 */
.welcome-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* space-y-2 */
}

.avatar-container {
  width: 5rem; /* w-20 */
  height: 5rem; /* h-20 */
  margin: 0 auto;
  background-color: #dbeafe; /* bg-blue-100 */
  border-radius: 9999px; /* rounded-full */
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  width: 3rem; /* w-12 */
  height: 3rem; /* h-12 */
  color: #2563eb; /* text-blue-600 */
}

.welcome-title {
  font-size: 1.5rem; /* text-2xl */
  font-weight: 700; /* font-bold */
  color: #1f2937; /* text-gray-800 */
  line-height: 1.25;
  margin: 0;
}

.welcome-subtitle {
  font-size: 0.875rem; /* text-base -> 实际是text-gray-500 */
  color: #6b7280; /* text-gray-500 */
  line-height: 1.5;
  margin: 0;
}

/* 表单区域 - 与HTML完全一致 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* space-y-4 */
}

/* 输入框容器 - 与HTML完全一致 */
.input-container {
  border: 1px solid #d1d5db; /* border */
  border-radius: 0.75rem; /* rounded-xl */
  padding: 0.75rem; /* p-3 */
  background-color: #f9fafb; /* bg-gray-50 */
  position: relative;
  transition: border-color 0.15s ease-in-out;
}

.input-container:focus-within {
  border-color: #2563eb; /* focus:border-blue-500 */
  outline: none;
}

.input-label {
  font-size: 0.75rem; /* text-xs */
  color: #6b7280; /* text-gray-500 */
  margin-bottom: 0.25rem; /* mb-1 */
  font-weight: 400;
  line-height: 1;
}

.form-input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 0.875rem; /* text-sm */
  color: #1f2937; /* text-gray-800 */
  outline: none;
  padding: 0;
  margin: 0;
}

.form-input::placeholder {
  color: #9ca3af; /* placeholder-gray-400 */
  font-size: 0.875rem;
}

/* 密码显示切换按钮 */
.password-toggle {
  position: absolute;
  right: 0.75rem; /* 对齐padding */
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #6b7280; /* text-gray-500 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.eye-icon {
  width: 1rem; /* w-4 */
  height: 1rem; /* h-4 */
}

.password-toggle:hover {
  color: #374151; /* text-gray-700 */
}

/* 登录按钮 - 与HTML完全一致 */
.login-button {
  width: 100%;
  background-color: #2563eb; /* bg-blue-600 */
  color: white;
  font-weight: 500; /* font-medium */
  border: none;
  border-radius: 9999px; /* rounded-full */
  padding: 0.75rem 0; /* py-3 */
  font-size: 0.875rem; /* text-sm */
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  margin-top: 0.5rem;
}

.login-button:hover:not(:disabled) {
  background-color: #1d4ed8; /* hover:bg-blue-700 */
}

.login-button:active:not(:disabled) {
  background-color: #1e40af; /* active:bg-blue-800 */
}

.login-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载动画 */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.loading-dot {
  width: 0.375rem;
  height: 0.375rem;
  background: white;
  border-radius: 50%;
  animation: loading 1.4s infinite ease-in-out;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%, 80%, 100% { 
    transform: scale(0);
    opacity: 0; 
  }
  40% { 
    transform: scale(1);
    opacity: 1; 
  }
}

/* 操作链接 - 与HTML完全一致 */
.action-links {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem; /* text-sm */
}

.link-button {
  background: transparent;
  border: none;
  font-size: 0.875rem; /* text-sm */
  font-weight: 400;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem; /* rounded */
  transition: background-color 0.15s ease-in-out;
}

.register-link {
  color: #2563eb; /* text-blue-600 */
}

.forgot-link {
  color: #6b7280; /* text-gray-500 */
}

.link-button:hover {
  background-color: #f3f4f6; /* hover:bg-gray-100 */
}

/* 响应式设计 */
@media (max-width: 400px) {
  .login-container {
    padding: 0.5rem;
  }
  
  .mobile-frame {
    width: 100%;
    height: 100vh;
    border-radius: 0;
  }
}

@media (max-height: 850px) {
  .mobile-frame {
    height: auto;
    min-height: 100vh;
    max-height: 812px;
  }
}
</style>