<!-- 注册账号 -->

<template>
  <!-- 移动端容器 -->
  <div class="register-container">
    <div class="mobile-frame">
      <!-- 返回栏 -->
      <header class="header-bar">
        <button class="back-button" @click="goBack">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1 class="header-title">注册账号</h1>
      </header>

      <!-- 主要内容区域 -->
      <main class="main-content">
        <div class="content-wrapper">
          <!-- 标题区 -->
          <div class="welcome-section">
            <h2 class="welcome-title">加入 U-Linker</h2>
            <p class="welcome-subtitle">完成学生身份认证，开启校园互助</p>
          </div>

          <!-- 表单区域 -->
          <form class="form-section" @submit.prevent="handleRegister">
            <!-- 学院下拉选择 -->
            <div class="input-container">
              <div class="input-label">学院</div>
              <select 
                class="form-select"
                v-model="formData.college"
                @change="clearError('college')"
              >
                <option value="" disabled selected>请选择您的学院</option>
                <option value="maynooth">梅努斯国际工程学院</option>
              </select>
              <div v-if="errors.college" class="error-message">{{ errors.college }}</div>
            </div>

            <!-- 真实姓名和学号（并列） -->
            <div class="form-row">
              <div class="input-container" style="flex: 1">
                <div class="input-label">真实姓名</div>
                <input 
                  type="text" 
                  class="form-input"
                  placeholder="您的姓名"
                  v-model="formData.realName"
                  @input="clearError('realName')"
                >
                <div v-if="errors.realName" class="error-message">{{ errors.realName }}</div>
              </div>
              <div class="input-container" style="flex: 1; margin-left: 12px">
                <div class="input-label">学号</div>
                <input 
                  type="text" 
                  class="form-input"
                  placeholder="9位学号"
                  v-model="formData.studentId"
                  maxlength="9"
                  @input="validateStudentId"
                >
                <div v-if="errors.studentId" class="error-message">{{ errors.studentId }}</div>
              </div>
            </div>

            <!-- 设置密码 -->
            <div class="input-container">
              <div class="input-label">设置密码</div>
              <div class="password-input-wrapper">
                <input 
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input password-input"
                  placeholder="密码必须同时包含数字和字母"
                  v-model="formData.password"
                  @input="validatePassword"
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
              <!-- 密码强度指示器 -->
              <div class="password-strength">
                <div class="strength-bar" :class="strengthClass"></div>
                <div class="strength-text">{{ strengthText }}</div>
              </div>
              <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
            </div>

            <!-- 确认密码 -->
            <div class="input-container">
              <div class="input-label">确认密码</div>
              <div class="password-input-wrapper">
                <input 
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="再次输入密码"
                  v-model="formData.confirmPassword"
                  @input="validateConfirmPassword"
                >
                <button 
                  type="button" 
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <svg class="eye-icon" viewBox="0 0 24 24" fill="none" v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg class="eye-icon" viewBox="0 0 24 24" fill="none" v-else xmlns="http://www.w3.org/2000/svg">
                    <path d="M14.12 14.12C13.8454 14.4148 13.5141 14.6512 13.1462 14.8151C12.7782 14.9791 12.3809 15.0673 11.9781 15.0744C11.5753 15.0815 11.1752 15.0074 10.8016 14.8565C10.4281 14.7056 10.0887 14.481 9.80385 14.1962C9.51897 13.9113 9.29439 13.5719 9.14351 13.1984C8.99262 12.8248 8.91853 12.4247 8.92563 12.0219C8.93274 11.6191 9.02091 11.2218 9.18488 10.8538C9.34884 10.4859 9.58525 10.1546 9.88 9.88M17.94 17.94C16.2306 19.243 14.1491 19.9649 12 20C5 20 1 12 1 12C2.80448 10.2466 3.9999 8.68329 5.5 7.5M9.9 4.24C10.5883 4.07888 11.2931 3.99834 12 4C19 4 23 12 23 12C21.393 13.1356 20.6691 14.2048 19.84 15.19M1 1L23 23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
              <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
            </div>

            <!-- 注册按钮 -->
            <button 
              type="submit" 
              class="register-button"
              :disabled="!isFormValid"
            >
              立即注册 (+100积分)
            </button>

            <!-- 协议提示 -->
            <div class="agreement">
              点击注册即代表同意《用户协议》与《隐私政策》
            </div>
          </form>
        </div>
      </main>
    </div>

    <!-- 成功浮窗 -->
    <div v-if="showSuccessModal" class="success-modal">
      <div class="modal-overlay"></div>
      <div class="modal-container">
        <div class="modal-content">
          
          <!-- 顶部绿色圆形 + 对勾图标 -->
          <div class="success-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM9.29 16.29L5.7 12.7C5.31 12.31 5.31 11.68 5.7 11.29C6.09 10.9 6.72 10.9 7.11 11.29L10 14.17L16.88 7.29C17.27 6.9 17.9 6.9 18.29 7.29C18.68 7.68 18.68 8.31 18.29 8.7L10.7 16.29C10.32 16.68 9.68 16.68 9.29 16.29Z" fill="#52C41A"/>
            </svg>
          </div>

          <!-- 标题 -->
          <h3 class="modal-title">注册成功</h3>

          <!-- 欢迎文字 -->
          <p class="modal-subtitle">欢迎加入 U-Linker 校园互助！</p>

          <!-- 积分奖励 -->
          <div class="points-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="#E6A23C"/>
            </svg>
            已获赠 100 积分
          </div>

          <!-- 登录按钮 -->
          <button class="modal-login-button" @click="goToLogin">
            立即登录
          </button>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'

const router = useRouter()

// 学院列表数据
const colleges = ref([
  { value: 'maynooth', label: '梅努斯国际工程学院' }
])

// 表单数据
const formData = reactive({
  username: '', // 这一项如果页面没输入框，下面会自动用学号填充
  college: '',
  password: '',
  confirmPassword: '',
  studentId: '',
  realName: ''
  // 注意：你之前这里多写了一个 college: ''，我删掉了重复的
})

const isLoading = ref(false)

// 状态管理
const showPassword = ref(false)
const showConfirmPassword = ref(false) // 控制确认密码显示/隐藏
const showSuccessModal = ref(false)    // 控制成功弹窗显示
const errors = reactive({
  college: '',
  realName: '',
  studentId: '',
  password: '',
  confirmPassword: ''
})

// --- 密码强度逻辑 (保持不变) ---
const passwordStrength = computed(() => {
  const password = formData.password
  if (!password) return 0
  let score = 0
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  if (/\d/.test(password)) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  return Math.min(Math.floor(score / 2), 3)
})

const strengthText = computed(() => {
  const strength = passwordStrength.value
  switch(strength) {
    case 0: return '请设置密码'
    case 1: return '弱'
    case 2: return '中'
    case 3: return '强'
    default: return ''
  }
})

const strengthClass = computed(() => `strength-${passwordStrength.value}`)

// --- 交互方法 (保持不变) ---
const togglePasswordVisibility = () => { showPassword.value = !showPassword.value }
const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}
const clearError = (field) => { errors[field] = '' }
const goBack = () => { router.back() }
const goToLogin = () => { router.push('/login') }

// --- 验证逻辑 (保持不变) ---
const validateStudentId = () => {
  clearError('studentId')
  if (!formData.studentId) return
  if (!/^\d{9}$/.test(formData.studentId.trim())) {
    errors.studentId = '学号必须是9位数字'
  }
}

const validatePassword = () => {
  clearError('password')
  if (!formData.password) return
  if (formData.password.length < 8) {
    errors.password = '密码长度至少8位'
  } else if (!/\d/.test(formData.password) || !/[a-zA-Z]/.test(formData.password)) {
    errors.password = '密码必须同时包含数字和字母'
  }
}

const validateConfirmPassword = () => {
  clearError('confirmPassword')
  if (!formData.confirmPassword) return
  if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
  }
}

// 表单验证计算属性
const isFormValid = computed(() => {
  return (
    formData.college &&
    formData.realName &&
    formData.studentId &&
    formData.password &&
    formData.confirmPassword &&
    formData.password === formData.confirmPassword &&
    !errors.college && !errors.realName && !errors.studentId &&
    !errors.password && !errors.confirmPassword
  )
})

// --- 🚀 核心修改：处理注册 ---
// 1. 加上 async 关键字
const handleRegister = async () => {
  // 触发所有验证
  if (!formData.college) errors.college = '请选择学院'
  if (!formData.realName) errors.realName = '请输入真实姓名'
  if (!formData.studentId) errors.studentId = '请输入学号'
  else validateStudentId()
  if (!formData.password) errors.password = '请设置密码'
  else validatePassword()
  if (!formData.confirmPassword) errors.confirmPassword = '请确认密码'
  else validateConfirmPassword()

  // 如果验证不通过，直接返回
  if (!isFormValid.value) return
  
  isLoading.value = true
  
  try {
    // 2. 构造 Payload (注意：这里用 formData，不是 form)
    const payload = {
      // 如果没有专门的用户名输入框，默认把学号当作用户名传给后端
      // 这样后端 auth.py 里的 if not username 就不会报错了
      username: formData.username || formData.studentId, 
      password: formData.password,
      confirmPassword: formData.confirmPassword,
      studentId: formData.studentId,
      name: formData.realName, // 映射：前端 realName -> 后端 name
      college: formData.college
    }

    console.log('正在发送注册请求:', payload)

    // 3. 调用真接口
    const res = await register(payload)
    
    // 4. 成功处理
    console.log('注册成功:', res)
    alert('注册成功！赠送 100 积分，请登录。')
    router.push('/login')

  } catch (error) {
    console.error('注册失败:', error)
    // 错误会自动弹窗，这里不需要额外 alert
  } finally {
    isLoading.value = false
  }
}

// 监听密码变化
watch(() => formData.password, () => {
  validatePassword()
})
</script>

<style scoped>
/* 基础样式 - 与loginPage完全一致 */
.register-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

/* 移动端容器 - 与loginPage完全一致 */
.mobile-frame {
  width: 375px;
  height: 812px;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 1. 顶部标题栏 - 类似loginPage但带返回按钮 */
.header-bar {
  height: 4rem;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  position: relative;
}

.back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  position: absolute;
  left: 8px;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #333;
  text-align: center;
  flex: 1;
  margin: 0;
}

/* 2. 主内容区域 - 与loginPage完全一致 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem;
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
  max-width: 28rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 欢迎区域 - 类似loginPage */
.welcome-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
  line-height: 1.25;
  margin: 0;
}

.welcome-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
}

/* 表单区域 - 与loginPage完全一致 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 输入框容器 - 与loginPage完全一致 */
.input-container {
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  position: relative;
  transition: border-color 0.15s ease-in-out;
}

.input-container:focus-within {
  border-color: #2563eb;
  outline: none;
}

.input-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  font-weight: 400;
  line-height: 1;
}

/* 下拉选择框样式 */
.form-select {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
  padding: 0;
  margin: 0;
  appearance: none;
  cursor: pointer;
}

.form-select:invalid {
  color: #9ca3af;
}

.form-input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
  padding: 0;
  margin: 0;
}

.form-input::placeholder {
  color: #9ca3af;
  font-size: 0.875rem;
}

/* 表单行布局 */
.form-row {
  display: flex;
  gap: 0;
}

/* 密码输入框特殊样式 */
.password-input-wrapper {
  position: relative;
}

.password-input {
  padding-right: 2rem;
}

.password-toggle {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
}

.eye-icon {
  width: 1rem;
  height: 1rem;
}

.password-toggle:hover {
  color: #374151;
}

/* 密码强度指示器 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: #e5e7eb;
  overflow: hidden;
  position: relative;
}

.strength-bar::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 0;
  transition: width 0.3s ease;
}

.strength-0::after { width: 0%; background: #e5e7eb; }
.strength-1::after { width: 33%; background: #ef4444; }
.strength-2::after { width: 66%; background: #f59e0b; }
.strength-3::after { width: 100%; background: #10b981; }

.strength-text {
  font-size: 0.75rem;
  min-width: 40px;
  text-align: right;
}

.strength-0 { color: #9ca3af; }
.strength-1 { color: #ef4444; }
.strength-2 { color: #f59e0b; }
.strength-3 { color: #10b981; }

/* 错误消息 */
.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.25rem;
  font-weight: 400;
}

/* 注册按钮 - 类似loginPage按钮 */
.register-button {
  width: 100%;
  background-color: #2563eb;
  color: white;
  font-weight: 500;
  border: none;
  border-radius: 9999px;
  padding: 0.75rem 0;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  margin-top: 0.5rem;
}

.register-button:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.register-button:active:not(:disabled) {
  background-color: #1e40af;
}

.register-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 协议提示 */
.agreement {
  text-align: center;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 1rem;
  line-height: 1.5;
}

/* 成功浮窗样式 */
.success-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
}

.modal-container {
  position: relative;
  z-index: 1001;
  width: 300px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 40px 24px 32px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* 成功图标 */
.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #f6ffed;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

/* 标题 */
.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #333333;
  margin: 0 0 10px;
  line-height: 1.4;
}

/* 副标题 */
.modal-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0 0 15px;
  line-height: 1.5;
}

/* 积分奖励徽章 */
.points-badge {
  background: #fffbeb;
  color: #e6a23c;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 20px;
}

/* 登录按钮 */
.modal-login-button {
  width: 100%;
  height: 44px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 0;
}

.modal-login-button:hover {
  background: #1d4ed8;
}

/* 动画效果 */
.modal-container {
  animation: modalIn 0.3s ease-out forwards;
}

@keyframes modalIn {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 400px) {
  .register-container {
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