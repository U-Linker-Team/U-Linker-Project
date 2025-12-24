<template>
  <div class="provide-service-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>

      <!-- 顶部导航 -->
      <header class="header-bar">
        <div class="back-button" @click="goBack">
          <span class="iconify" data-icon="mdi:close"></span>
        </div>
        <h1 class="app-title">发布</h1>
        <div class="reset-button" @click="handleReset">重置</div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        
        <!-- 切换发布类型 -->
        <div class="type-toggle">
          <!-- 按钮 1: 我需要 (悬赏) -->
          <button 
            class="type-button"
            :class="{ 
              'active': formData.post_type === 'bounty', 
              'text-blue-600': formData.post_type === 'bounty',
              'text-gray-500': formData.post_type !== 'bounty'
            }"
            @click="formData.post_type = 'bounty'"
          >
            <span class="iconify" data-icon="mdi:hand-extended-outline"></span>
            我需要 (悬赏)
          </button>

          <!-- 按钮 2: 我能提供 (服务) -->
          <button 
            class="type-button"
            :class="{ 
              'active': formData.post_type === 'service',
              'text-orange-500': formData.post_type === 'service',
              'text-gray-500': formData.post_type !== 'service'
            }"
            @click="formData.post_type = 'service'"
          >
            <span class="iconify" data-icon="mdi:briefcase-outline"></span>
            我能提供 (服务)
          </button>
        </div>

        <!-- 表单区域 -->
        <div class="form-section">
          <!-- 服务/任务标题 -->
          <div class="form-group">
            <label class="form-label">
              {{ formData.post_type === 'bounty' ? '任务标题' : '服务标题' }} <span class="required">*</span>
            </label>
            <input
              type="text"
              v-model="formData.title"
              :placeholder="formData.post_type === 'bounty' ? '例如：急求帮取东门快递' : '例如：提供英语口语陪练，雅思8.0'"
              class="form-input"
              :class="{ 'error': titleError }"
              @input="validateTitle"
            />
            <p class="error-message" v-if="titleError">{{ titleError }}</p>
          </div>

          <!-- 详情描述 -->
          <div class="form-group">
            <label class="form-label">
              详情描述 <span class="required">*</span>
            </label>
            <textarea
              v-model="formData.description"
              :placeholder="formData.post_type === 'bounty' ? '请详细描述任务要求、时间地点等...' : '请描述您的技能优势、服务时间、服务方式等...'"
              class="form-textarea"
              :class="{ 'error': descriptionError }"
              @input="validateDescription"
              rows="6"
            ></textarea>
            <p class="error-message" v-if="descriptionError">{{ descriptionError }}</p>
          </div>

          <!-- 价格/积分 -->
          <div class="form-group">
            <label class="form-label">
              {{ formData.post_type === 'bounty' ? '悬赏积分' : '服务价格' }}
            </label>
            <div class="price-container">
              <div class="price-input-wrapper">
                <input
                  type="number"
                  v-model.number="formData.price"
                  @input="validatePrice"
                  class="price-input"
                  :class="{ 
                    'error': priceError, 
                    'text-blue-600': formData.post_type === 'bounty',
                    'text-orange-500': formData.post_type === 'service'
                  }"
                  min="1"
                />
                <span class="price-unit">分</span>
              </div>
              <div class="price-controls">
                <button 
                  class="price-btn minus text-gray-500"
                  @click="decreasePrice"
                  :disabled="formData.price <= 1"
                >
                  -
                </button>
                <button 
                  class="price-btn plus text-gray-500"
                  @click="increasePrice"
                >
                  +
                </button>
              </div>
            </div>
            <!-- 动态提示文案 -->
            <p class="price-hint" :class="{ 
              'error-text': priceError,
              'text-blue-600': formData.post_type === 'bounty',
              'text-orange-500': formData.post_type === 'service'
            }">
              <span class="iconify" :data-icon="formData.post_type === 'bounty' ? 'mdi:information-outline' : 'mdi:cash-multiple'"></span>
              {{ priceError || (formData.post_type === 'bounty' ? '发布后将冻结相应积分，任务完成后转给对方。' : '买家确认服务完成后，积分将直接转入您的账户。') }}
            </p>
          </div>

          <!-- 作品/证明展示 -->
          <div class="form-group">
            <div class="form-label">
              图片展示 <span class="optional">(可选)</span>
            </div>
            <div class="image-upload-section">
              <!-- 上传按钮 -->
              <div 
                class="upload-area"
                @click="triggerImageUpload"
                @dragover.prevent="handleDragOver"
                @drop.prevent="handleDrop"
              >
                <span class="iconify" data-icon="mdi:camera-plus-outline"></span>
                <input
                  type="file"
                  ref="imageInput"
                  @change="handleImageUpload"
                  accept="image/*"
                  multiple
                  class="file-input"
                  style="display: none" 
                />
              </div>
              
              <!-- 已上传图片预览 -->
              <div 
                v-for="(image, index) in uploadedImages" 
                :key="index"
                class="image-preview"
              >
                <img :src="image.url" :alt="image.name" class="preview-image" />
                <div class="remove-btn" @click="removeImage(index)">
                  <span class="iconify" data-icon="mdi:close"></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部发布按钮 -->
      <footer class="footer-bar">
        <button
          class="publish-button"
          :class="{ 
            'disabled': !isFormValid, 
            'publishing': isPublishing,
            'bg-blue-600': formData.post_type === 'bounty',
            'bg-orange-500': formData.post_type === 'service'
          }"
          @click="handlePublish"
          :disabled="!isFormValid || isPublishing"
        >
          <span v-if="!isPublishing">
            立即发布{{ formData.post_type === 'bounty' ? '悬赏' : '服务' }}
          </span>
          <span v-else class="publishing-text">
            <span class="iconify" data-icon="mdi:loading" style="animation: spin 1s linear infinite;"></span>
            发布中...
          </span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 1. 引入 API
import { addPost } from '@/api/market'
import { getUserProfile } from '@/api/auth'

const router = useRouter()
const route = useRoute() 
const userStore = useUserStore()

// 表单数据
const formData = reactive({
  title: '',
  description: '',
  price: 10,
  post_type: 'bounty', // 默认悬赏
  images: []
})

// 响应式数据
const titleError = ref('')
const descriptionError = ref('')
const priceError = ref('')
const uploadedImages = ref([])
const isPublishing = ref(false)
const imageInput = ref(null)

// 计算属性：表单是否有效
const isFormValid = computed(() => {
  return !titleError.value && 
         !descriptionError.value && 
         !priceError.value &&
         formData.title.trim().length >= 5 &&
         formData.description.trim().length >= 10 &&
         formData.price > 0
})

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 重置表单
const handleReset = () => {
  if (confirm('确定要重置所有内容吗？')) {
    formData.title = ''
    formData.description = ''
    formData.price = 10
    uploadedImages.value = []
    titleError.value = ''
    descriptionError.value = ''
    priceError.value = ''
  }
}

// 验证逻辑
const validateTitle = () => {
  const title = formData.title.trim()
  if (title.length === 0) {
    titleError.value = '标题不能为空'
  } else if (title.length < 5) {
    titleError.value = '标题至少需要5个字符'
  } else if (title.length > 50) {
    titleError.value = '标题不能超过50个字符'
  } else {
    titleError.value = ''
  }
}

const validateDescription = () => {
  const description = formData.description.trim()
  if (description.length === 0) {
    descriptionError.value = '详情不能为空'
  } else if (description.length < 10) {
    descriptionError.value = '详情至少需要10个字符'
  } else {
    descriptionError.value = ''
  }
}

const validatePrice = () => {
  const price = formData.price
  if (isNaN(price) || price <= 0) {
    priceError.value = '价格必须是正整数'
  } else if (!Number.isInteger(price)) {
    priceError.value = '价格必须是整数'
  } else {
    priceError.value = ''
  }
}

// 价格调节
const decreasePrice = () => {
  if (formData.price > 1) {
    formData.price--
    validatePrice()
  }
}

const increasePrice = () => {
  formData.price++
  validatePrice()
}

// 图片上传相关逻辑 (前端预览用，目前后端接口暂不支持存图)
const triggerImageUpload = () => imageInput.value.click()

const handleImageUpload = (event) => {
  const files = event.target.files
  handleFiles(files)
}

const handleDragOver = (e) => e.preventDefault()
const handleDrop = (e) => {
  e.preventDefault()
  handleFiles(e.dataTransfer.files)
}

const handleFiles = (files) => {
  if (uploadedImages.value.length + files.length > 5) {
    alert('最多只能上传5张图片')
    return
  }
  Array.from(files).forEach(file => {
    if (!file.type.match('image.*')) return
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedImages.value.push({ url: e.target.result, file: file })
    }
    reader.readAsDataURL(file)
  })
}

const removeImage = (index) => uploadedImages.value.splice(index, 1)

// ==========================================
// 🔥 核心修改：处理发布 (对接后端)
// ==========================================
const handlePublish = async () => {
  // 1. 最后校验
  validateTitle()
  validateDescription()
  validatePrice()

  if (!isFormValid.value || isPublishing.value) return

  // 2. 积分检查 (仅针对悬赏)
  if (formData.post_type === 'bounty') {
    if ((userStore.userInfo?.points || 0) < formData.price) {
      alert(`积分不足！当前余额: ${userStore.userInfo?.points}，需要: ${formData.price}`)
      return
    }
  }

  isPublishing.value = true

  try {
    // 3. 构造数据包
    const postData = {
      title: formData.title.trim(),
      content: formData.description.trim(), // 对应后端 content
      price: Number(formData.price),
      post_type: formData.post_type // 'service' 或 'bounty'
    }
    
    // 4. 调用后端 API
    await addPost(postData)

    // 5. 成功后：刷新用户积分 (因为发布悬赏扣分了)
    try {
      const userRes = await getUserProfile(userStore.userInfo.id)
      userStore.login(userRes.data) // 更新 Pinia
    } catch (err) {
      console.warn('积分刷新失败，但不影响发布', err)
    }

    // 6. 提示并跳转
    alert(`${formData.post_type === 'bounty' ? '悬赏' : '服务'}发布成功！`)
    router.push('/home') // 回到首页
    
  } catch (error) {
    console.error('发布失败:', error)
    // 显示后端返回的具体错误信息
    const msg = error.response?.data?.message || '发布失败，请重试'
    alert(msg)
  } finally {
    isPublishing.value = false
  }
}

// 初始化
onMounted(() => {
  // 检查登录
  if (!userStore.userInfo) {
    alert('请先登录')
    router.push('/login')
    return
  }

  // 接收路由参数 (例如从首页点击"我需要"进来，自动切到 bounty)
  if (route.query.type) {
    formData.post_type = route.query.type
  }
})
</script>

<style scoped>
/* 基础容器 */
.provide-service-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

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
}

.reset-button {
  font-size: 0.875rem;
  color: #9ca3af;
  cursor: pointer;
  transition: color 0.2s ease;
  width: 2.5rem;
  text-align: right;
}

.reset-button:hover {
  color: #4b5563;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
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

/* 发布类型切换 */
.type-toggle {
  background-color: #f3f4f6;
  padding: 0.25rem;
  border-radius: 0.75rem;
  display: flex;
  margin-bottom: 1.5rem;
}

.type-button {
  flex: 1;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: none;
  background: transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.type-button .iconify {
  width: 1.25rem;
  height: 1.25rem;
}

.type-button.active {
  background-color: white;
  color: #f97316;
  font-weight: 700;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 表单区域 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
}

.required {
  color: #ef4444;
  margin-left: 0.25rem;
}

.optional {
  font-size: 0.75rem;
  font-weight: 400;
  color: #9ca3af;
  margin-left: 0.25rem;
}

/* 输入框样式 */
.form-input,
.form-textarea {
  width: 100%;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  font-size: 0.875rem;
  color: #111827;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.form-input.error,
.form-textarea.error {
  border-color: #ef4444;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #9ca3af;
}

.form-textarea {
  resize: none;
  font-family: inherit;
  line-height: 1.5;
}

.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.25rem;
  min-height: 1rem;
}

/* 价格容器 */
.price-container {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s ease;
}

.price-container:focus-within {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.price-container .error {
  border-color: #ef4444;
}

.price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-input {
  width: 6rem;
  background: transparent;
  border: none;
  outline: none;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f97316;
  text-align: right;
}

.price-input.error {
  color: #ef4444;
}

.price-unit {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  white-space: nowrap;
}

.price-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.price-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
  background-color: white;
  color: #6b7280;
  font-size: 1.125rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.price-btn:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

.price-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.price-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.price-btn.minus {
  color: #6b7280;
}

.price-btn.plus {
  color: #f97316;
}

.price-hint {
  font-size: 0.625rem;
  color: #f97316;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.price-hint .iconify {
  width: 0.75rem;
  height: 0.75rem;
}

.price-hint.error-text {
  color: #ef4444;
}

/* 图片上传区域 */
.image-upload-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.upload-area {
  width: 5rem;
  height: 5rem;
  border: 2px dashed #d1d5db;
  border-radius: 1rem;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-area:hover {
  background-color: #f3f4f6;
  border-color: #f97316;
}

.upload-area .iconify {
  width: 1.5rem;
  height: 1.5rem;
  color: #9ca3af;
}

.upload-area:hover .iconify {
  color: #f97316;
}

.file-input {
  display: none;
}

.image-preview {
  width: 5rem;
  height: 5rem;
  border-radius: 1rem;
  background-color: #f3f4f6;
  overflow: hidden;
  position: relative;
  border: 1px solid #e5e7eb;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  width: 1.25rem;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.remove-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.remove-btn .iconify {
  width: 0.75rem;
  height: 0.75rem;
  color: white;
}

/* 底部发布按钮 */
.footer-bar {
  background-color: white;
  border-top: 1px solid #f3f4f6;
  padding: 1rem 1.5rem;
  z-index: 30;
  flex-shrink: 0;
}

.publish-button {
  width: 100%;
  padding: 1rem;
  background-color: #f97316;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.publish-button:hover:not(.disabled) {
  background-color: #ea580c;
  box-shadow: 0 15px 20px -3px rgba(249, 115, 22, 0.25);
}

.publish-button:active:not(.disabled) {
  transform: scale(0.99);
  box-shadow: 0 5px 10px -3px rgba(249, 115, 22, 0.2);
}

.publish-button.publishing {
  background-color: #f97316;
  opacity: 0.8;
}

.publish-button.disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
}

.publishing-text {
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
  .provide-service-container {
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