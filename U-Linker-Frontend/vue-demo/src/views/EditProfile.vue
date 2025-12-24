<template>
  <div class="edit-profile-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>

      <!-- 顶部导航 -->
      <header class="header-bar">
        <div class="back-button" @click="goBack">
          <span class="iconify" data-icon="mdi:arrow-left"></span>
        </div>
        <h1 class="app-title">编辑资料</h1>
        <div class="placeholder"></div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 头像上传区域 -->
        <div class="avatar-section">
          <div class="avatar-upload" @click="triggerFileInput">
            <div class="avatar-preview">
              <!-- [修改] 绑定真实头像 -->
              <img 
                :src="avatarPreview || formData.avatar || 'https://via.placeholder.com/100'" 
                alt="用户头像" 
                class="avatar-image" 
                @error="(e) => e.target.src = 'https://via.placeholder.com/100'"
              />
            </div>
            <div class="camera-icon">
              <span class="iconify" data-icon="mdi:camera-outline"></span>
            </div>
            <input
              type="file"
              ref="fileInput"
              @change="handleAvatarUpload"
              accept="image/jpeg,image/png"
              class="file-input"
            />
          </div>
          <p class="upload-hint">点击修改头像 (支持JPG/PNG, Max 2MB)</p>
        </div>

        <!-- 表单区域 -->
        <div class="form-section">
          <!-- 用户名 -->
          <div class="form-group">
            <label class="form-label">昵称 / 姓名</label>
            <div class="input-container" :class="{ 'input-error': usernameError }">
              <input
                type="text"
                v-model="formData.name" 
                placeholder="请输入你的昵称"
                class="form-input"
              />
            </div>
            <!-- [修改] 错误提示逻辑简化 -->
            <p class="form-hint" v-if="usernameError" :class="{ 'error-text': usernameError }">
              {{ usernameError }}
            </p>
          </div>

          <!-- 学号/工号 -->
          <div class="form-group disabled">
            <label class="form-label">学号 / 工号</label>
            <div class="input-container disabled">
              <span class="disabled-text">{{ formData.studentId }}</span>
              <span class="iconify lock-icon" data-icon="mdi:lock-outline"></span>
            </div>
          </div>

          <!-- 所属学院 -->
          <div class="form-group disabled">
            <label class="form-label">所属学院</label>
            <div class="input-container disabled">
              <span class="disabled-text">{{ formData.college }}</span>
              <span class="iconify lock-icon" data-icon="mdi:lock-outline"></span>
            </div>
          </div>

          <!-- 个人简介 -->
          <div class="form-group">
            <label class="form-label">个人简介</label>
            <div class="textarea-container">
              <textarea
                v-model="formData.bio"
                placeholder="介绍一下自己，让大家更信任你..."
                class="form-textarea"
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部保存按钮 -->
      <footer class="footer-bar">
        <button
          class="save-button"
          :class="{ 'saving': isSaving, 'disabled': !isFormValid }"
          @click="handleSave"
          :disabled="!isFormValid || isSaving"
        >
          <span v-if="!isSaving">保存修改</span>
          <span v-else class="saving-text">
            <span class="iconify" data-icon="mdi:loading" style="animation: spin 1s linear infinite;"></span>
            保存中...
          </span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { updateProfile } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const fileInput = ref(null)
const selectedFile = ref(null) // 存真实文件对象

// 表单数据 (初始化为空，等 onMounted 回填)
const formData = reactive({
  name: '', // 对应后端 name
  studentId: '',
  college: '',
  bio: '',
  avatar: ''
})

const avatarPreview = ref(null) // 仅用于预览新选的图
const usernameError = ref('')
const isSaving = ref(false)

// 简单的表单校验
const isFormValid = computed(() => {
  return formData.name && formData.name.trim().length > 0
})

// --- 核心修改 1: 数据回显 ---
onMounted(() => {
  const info = userStore.userInfo || {}
  
  // 从 Pinia 填充数据，替换原来的假数据
  formData.name = info.name || info.username || ''
  formData.studentId = info.student_id || '未设置'
  formData.college = info.college || '未设置'
  formData.avatar = info.avatar || ''
  // formData.bio = info.bio || '' // 如果后端没这个字段就先不用
})

const goBack = () => router.back()
const triggerFileInput = () => fileInput.value.click()

// --- 核心修改 2: 真实头像处理 ---
const handleAvatarUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.match('image.*')) {
    alert('只支持图片格式')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    alert('图片大小不能超过 2MB')
    return
  }

  // 1. 存文件对象
  selectedFile.value = file
  
  // 2. 本地预览
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// --- 核心修改 3: 发送真实请求 ---
const handleSave = async () => {
  if (!isFormValid.value || isSaving.value) return

  isSaving.value = true

  try {
    // 构造 FormData
    const payload = new FormData()
    payload.append('user_id', userStore.userInfo.id)
    payload.append('name', formData.name)
    
    // 只有选了新图才传 avatar
    if (selectedFile.value) {
      payload.append('avatar', selectedFile.value)
    }

    // 发请求
    const res = await updateProfile(payload)
    
    // 更新本地 Store
    userStore.login(res.data)

    console.log('保存成功:', res)
    alert('资料修改成功！')
    
    router.back() // 返回上一页
    
  } catch (error) {
    console.error('保存失败:', error)
    // 错误处理交给拦截器
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
/* 
   此处完全保留了你队友原来的所有 CSS 样式 
   一行都没动，保证界面长得一模一样！
*/
.edit-profile-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

/* ... (后面的 CSS 请保留原文件里的，不要删) ... */
/* 为了节省篇幅，这里省略了 CSS 部分，请确保你复制的时候保留了原来的 <style scoped> 内容 */
/* 如果你原来的文件里 CSS 很长，记得别把它覆盖没了 */

/* 移动端框架 */
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

/* 状态栏 */
.status-bar {
  height: 2rem;
  background-color: white;
  width: 100%;
  flex-shrink: 0;
}

/* 顶部导航 */
.header-bar {
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  background-color: white;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.back-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  cursor: pointer;
}

.back-button .iconify {
  width: 1.5rem;
  height: 1.5rem;
  color: #4b5563;
}

.app-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
  text-align: center;
  flex: 1;
}

.placeholder {
  width: 2.5rem;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 1.5rem 1rem;
  background-color: white;
}

/* 隐藏滚动条 */
.main-content::-webkit-scrollbar {
  display: none;
}

.main-content {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 头像上传区域 */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.avatar-upload {
  position: relative;
  cursor: pointer;
  margin-bottom: 0.5rem;
  width: 6rem;
  height: 6rem;
}

.avatar-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 4px solid white;
  background-color: #e5e7eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 1;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-icon {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 2rem;
  height: 2rem;
  background-color: #2563eb;
  border-radius: 50%;
  border: 2px solid white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  z-index: 2; /* 确保相机图标在最上层 */
}

.camera-icon .iconify {
  width: 1rem;
  height: 1rem;
  color: white;
}

.avatar-upload:active .camera-icon {
  transform: scale(0.95);
}

.file-input {
  display: none;
}

.upload-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
  margin-top: 0.5rem;
}

/* 表单区域 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.disabled {
  opacity: 0.7;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: #374151;
  margin-left: 0.25rem;
}

.form-group.disabled .form-label {
  color: #6b7280;
}

.input-container {
  background-color: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.input-container:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-container.disabled {
  background-color: #f3f4f6;
  border-color: transparent;
}

.input-container.input-error {
  border-color: #ef4444;
}

.form-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

.form-input::placeholder {
  color: #9ca3af;
}

.disabled-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.lock-icon {
  width: 1rem;
  height: 1rem;
  color: #9ca3af;
}

.textarea-container {
  background-color: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.textarea-container:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  resize: none;
  font-family: inherit;
  line-height: 1.5;
}

.form-textarea::placeholder {
  color: #9ca3af;
}

.form-hint {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-left: 0.25rem;
  margin-top: 0.125rem;
  min-height: 0.875rem;
}

.error-text {
  color: #ef4444;
}

/* 底部保存按钮 */
.footer-bar {
  background-color: white;
  border-top: 1px solid #f3f4f6;
  padding: 1rem 1.5rem;
  z-index: 30;
  flex-shrink: 0;
}

.save-button {
  width: 100%;
  padding: 0.875rem;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.save-button:hover:not(.disabled) {
  background-color: #1d4ed8;
  box-shadow: 0 15px 20px -3px rgba(37, 99, 235, 0.25);
}

.save-button:active:not(.disabled) {
  transform: scale(0.98);
  box-shadow: 0 5px 10px -3px rgba(37, 99, 235, 0.2);
}

.save-button.saving {
  background-color: #2563eb;
  opacity: 0.8;
}

.save-button.disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
}

.saving-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 400px) {
  .edit-profile-container {
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