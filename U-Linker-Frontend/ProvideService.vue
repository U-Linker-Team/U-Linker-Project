<!-- 任务-发布任务-我能提供 -->

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
          <!-- 服务标题 -->
          <div class="form-group">
            <label class="form-label">
              服务标题 <span class="required">*</span>
            </label>
            <input
              type="text"
              v-model="formData.title"
              placeholder="例如：提供英语口语陪练，雅思8.0"
              class="form-input"
              :class="{ 'error': titleError }"
              @input="validateTitle"
            />
            <p class="error-message" v-if="titleError">{{ titleError }}</p>
          </div>

          <!-- 服务详情 -->
          <div class="form-group">
            <label class="form-label">
              服务详情 <span class="required">*</span>
            </label>
            <textarea
              v-model="formData.description"
              placeholder="请描述您的技能优势、服务时间、服务方式等..."
              class="form-textarea"
              :class="{ 'error': descriptionError }"
              @input="validateDescription"
              rows="6"
            ></textarea>
            <p class="error-message" v-if="descriptionError">{{ descriptionError }}</p>
          </div>

          <!-- 服务价格 -->
          <div class="form-group">
            <label class="form-label">
              服务价格 (积分)
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
                <span class="price-unit">分 / 次</span>
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
              作品/证明展示 <span class="optional">(可选)</span>
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
          :class="{ 'disabled': !isFormValid, 'publishing': isPublishing }"
          @click="handlePublish"
          :disabled="!isFormValid || isPublishing"
        >
          <span v-if="!isPublishing">立即发布服务</span>
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
import { useRouter,useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

//1.引入api
import {addPost} from '@/api/market'
import { getUserProfile } from '@/api/auth'

const router = useRouter()
const route = useRoute() 
const userStore = useUserStore()

// 表单数据
const formData = reactive({
  title: '',
  description: '',
  price: 10,
  post_type: 'bounty',
  images: []
})

// 响应式数据
const titleError = ref('')
const descriptionError = ref('')
const priceError = ref('')
const uploadedImages = ref([])
const isPublishing = ref(false)
const imageInput = ref(null)

// 计算属性
const isFormValid = computed(() => {
  return !titleError.value && 
         !descriptionError.value && 
         !priceError.value &&
         formData.title.trim().length > 0 &&
         formData.description.trim().length > 0 &&
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
    formData.price = 50
    uploadedImages.value = []
    titleError.value = ''
    descriptionError.value = ''
    priceError.value = ''
  }
}

// 跳转到"我需要"页面
const goToNeedTask = () => {
  // 这里可以添加跳转到"我需要"页面的逻辑
  console.log('跳转到"我需要"页面')
}

// 验证服务标题
const validateTitle = () => {
  const title = formData.title.trim()
  
  if (title.length === 0) {
    titleError.value = '服务标题不能为空'
    return
  }

  if (title.length < 5) {
    titleError.value = '服务标题至少需要5个字符'
    return
  }

  if (title.length > 50) {
    titleError.value = '服务标题不能超过50个字符'
    return
  }

  titleError.value = ''
}

// 验证服务详情
const validateDescription = () => {
  const description = formData.description.trim()
  
  if (description.length === 0) {
    descriptionError.value = '服务详情不能为空'
    return
  }

  if (description.length < 10) {
    descriptionError.value = '服务详情至少需要10个字符'
    return
  }

  if (description.length > 500) {
    descriptionError.value = '服务详情不能超过500个字符'
    return
  }

  descriptionError.value = ''
}

// 验证服务价格
const validatePrice = () => {
  const price = formData.price
  
  if (isNaN(price)) {
    priceError.value = '价格必须是数字'
    return
  }

  if (price <= 0) {
    priceError.value = '价格必须是正整数'
    return
  }

  if (!Number.isInteger(price)) {
    priceError.value = '价格必须是整数'
    return
  }

  if (price > 10000) {
    priceError.value = '价格不能超过10000积分'
    return
  }

  priceError.value = ''
}

// 减少价格
const decreasePrice = () => {
  if (formData.price > 1) {
    formData.price--
    validatePrice()
  }
}

// 增加价格
const increasePrice = () => {
  formData.price++
  validatePrice()
}

// 触发图片上传
const triggerImageUpload = () => {
  imageInput.value.click()
}

// 处理拖拽事件
const handleDragOver = (event) => {
  event.preventDefault()
  event.currentTarget.style.backgroundColor = '#f3f4f6'
}

const handleDrop = (event) => {
  event.preventDefault()
  event.currentTarget.style.backgroundColor = '#f9fafb'
  
  const files = event.dataTransfer.files
  handleFiles(files)
}

// 处理图片上传
const handleImageUpload = (event) => {
  const files = event.target.files
  handleFiles(files)
}

// 处理文件
const handleFiles = (files) => {
  if (uploadedImages.value.length + files.length > 5) {
    alert('最多只能上传5张图片')
    return
  }

  Array.from(files).forEach(file => {
    if (!file.type.match('image.*')) {
      alert('只能上传图片文件')
      return
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB
      alert('图片大小不能超过5MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedImages.value.push({
        url: e.target.result,
        name: file.name,
        file: file
      })
    }
    reader.readAsDataURL(file)
  })
}

// 移除图片
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}


// 核心修改: 处理发布
const handlePublish = async () => {
  
  // 触发一次全部验证
  validateTitle()
  validateDescription()
  validatePrice()

  if (!isFormValid.value || isPublishing.value) return

  isPublishing.value = true

  try {
    
    // 2. 构造发送给后端的数据包 (按照后端 routes/market.py 的要求)
    const postData = {
      author_id: userStore.userInfo.id, // 从 Pinia 仓库拿当前登录用户的 ID
      title: formData.title.trim(),
      content: formData.description.trim(), // 注意：后端数据库字段叫 content
      price: Number(formData.price),
      post_type: formData.post_type // 'service' 或 'bounty'
    }
    
    const res = await addPost(postData)

    try {
      const userRes = await getUserProfile(userStore.userInfo.id)
      // 更新本地仓库 (Pinia)，这样页面上的 100 就会自动变成 90 (假设扣了10分)
      userStore.login(userRes.data) 
    } catch (err) {
      console.error('刷新积分失败', err)
    }
    console.log('后端响应:', res)
    // 显示成功提示
    alert('服务发布成功！')
    
    // 返回首页或任务列表页
    router.push('/home')
    
  } catch (error) {
    console.error('发布失败:', error)
    alert('发布失败，请重试')
  } finally {
    isPublishing.value = false
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 可以添加一些初始化逻辑
  // 检查是否登录，没登录不让发
  if (!userStore.userInfo) {
    alert('请先登录')
    router.push('/login')
  }

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

/* 添加颜色类 */
.text-blue-600 {
  color: #2563eb; /* 蓝色 */
}

.text-orange-500 {
  color: #f97316; /* 橙色 */
}

.text-gray-500 {
  color: #6b7280;
}
</style>