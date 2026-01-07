<template>
  <div class="home-container">
   <div class="mobile-frame">
    <!-- 状态栏占位 -->
    <div class="status-bar"></div>
    <div class="flex flex-col h-screen bg-gray-50">
    <!-- 顶部导航 (复用 BackHeader) -->
    <BackHeader :title="targetName || '聊天'" />

    <!-- 消息列表区域 (自适应高度，可滚动) -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="scrollContainer">
      <div v-if="loading" class="text-center text-xs text-gray-400 py-2">加载历史记录...</div>
      
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        class="flex flex-col gap-1"
        :class="isMe(msg.sender_id) ? 'items-end' : 'items-start'"
      >
        <!-- 消息气泡 -->
        <div 
          class="max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-md break-words transition-all duration-200"
          :class="isMe(msg.sender_id) 
            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-none hover:shadow-lg' 
            : 'bg-white text-gray-800 border border-gray-200 rounded-tl-none hover:shadow-lg hover:border-gray-300'"
        >
          <!-- 图片消息 -->
          <div v-if="msg.message_type === 'image' && msg.file_url" class="mb-2">
            <img 
              :src="getFileUrl(msg.file_url)" 
              :alt="msg.file_name || '图片'"
              class="max-w-full rounded-lg cursor-pointer"
              @click="previewImage(getFileUrl(msg.file_url))"
            />
          </div>
          <!-- 视频消息 -->
          <div v-if="msg.message_type === 'video' && msg.file_url" class="mb-2">
            <video 
              :src="getFileUrl(msg.file_url)" 
              controls
              class="max-w-full rounded-lg"
              :poster="msg.thumbnail_url"
            >
              您的浏览器不支持视频播放
            </video>
          </div>
          <!-- 文本内容 -->
          <div v-if="msg.content">{{ msg.content }}</div>
          <div v-if="!msg.content && msg.message_type === 'image'" class="text-xs opacity-75">[图片]</div>
          <div v-if="!msg.content && msg.message_type === 'video'" class="text-xs opacity-75">[视频]</div>
        </div>
        
        <!-- 时间戳 -->
        <span class="text-[10px] text-gray-400 px-1">
          {{ formatTime(msg.created_at) }}
        </span>
      </div>
    </div>

    <!-- 底部输入框 (固定) -->
    <div class="bg-white/95 backdrop-blur-lg border-t border-gray-200 p-3 pb-safe shadow-lg">
      <!-- 图片/视频预览 -->
      <div v-if="previewFile" class="mb-2 relative">
        <div class="relative inline-block">
          <img v-if="previewFile.type.startsWith('image/')" :src="previewFile.url" class="max-w-[200px] max-h-[200px] rounded-lg" />
          <video v-else-if="previewFile.type.startsWith('video/')" :src="previewFile.url" class="max-w-[200px] max-h-[200px] rounded-lg" controls />
          <button 
            @click="clearPreview"
            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
          >
            ×
          </button>
        </div>
      </div>
      
      <div class="flex items-end gap-2">
        <!-- 文件选择按钮 -->
        <label class="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 cursor-pointer transition-colors">
          <input 
            type="file" 
            accept="image/*,video/*,.mp4,.mov,.avi,.webm,.mkv" 
            class="hidden" 
            @change="handleFileSelect"
            ref="fileInput"
          />
          <span class="iconify w-5 h-5 text-gray-600" data-icon="mdi:image-outline"></span>
        </label>
        
        <textarea 
          v-model="inputContent"
          rows="1"
          class="flex-1 bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-transparent rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white focus:border-blue-300 transition-all resize-none max-h-24 outline-none shadow-sm"
          placeholder="发送消息..."
          @keyup.enter.exact="handleSend"
        ></textarea>
        
        <button 
          @click="handleSend"
          :disabled="!inputContent.trim() && !previewFile"
          class="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded-full text-sm font-bold shadow-md active:scale-95 transition-all duration-200 disabled:opacity-50 disabled:shadow-none hover:bg-blue-700 hover:shadow-lg"
        >
          <span class="iconify w-5 h-5" data-icon="mdi:send"></span>
        </button>
      </div>
     </div>
     </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getHistory, sendMessage } from '@/api/chat'
import BackHeader from '@/components/common/BackHeader.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 同时支持路径参数和查询参数（向后兼容）
const sessionId = route.params.session_id || route.query.session_id
const messages = ref([])
const inputContent = ref('')
const scrollContainer = ref(null)
const loading = ref(false)
const targetName = ref('聊天') // 暂时用默认值，后端可以在 getHistory 里返回对方名字优化体验
const previewFile = ref(null)
const fileInput = ref(null)
let pollingTimer = null

// 判断消息是不是我发的
const isMe = (senderId) => {
  return senderId === userStore.userInfo?.id
}

// 获取历史消息
const fetchMessages = async (isFirstLoad = false) => {
  if (isFirstLoad) loading.value = true
  try {
    const res = await getHistory(sessionId)
    // 假设后端返回的数据格式: { data: [ {id, content, sender_id...} ] }
    // 如果列表长度变了，说明有新消息
    if (res.data.length !== messages.value.length) {
      messages.value = res.data
      scrollToBottom()
    }
  } catch (e) {
    console.error(e)
  } finally {
    if (isFirstLoad) loading.value = false
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 验证文件类型：同时检查 MIME 类型和文件扩展名
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.webm', '.mkv']
  const fileName = file.name.toLowerCase()
  const fileExtension = fileName.substring(fileName.lastIndexOf('.'))
  const isValidExtension = allowedExtensions.includes(fileExtension)
  const isValidMimeType = file.type.startsWith('image/') || file.type.startsWith('video/') || file.type === ''
  
  // 如果 MIME 类型为空或无效，但扩展名有效，也允许（浏览器兼容性）
  if (!isValidMimeType && !isValidExtension) {
    alert('不支持的文件类型，仅支持图片和视频')
    return
  }
  
  // 如果扩展名不在允许列表中，即使 MIME 类型有效也拒绝（更严格的安全检查）
  if (!isValidExtension) {
    alert('不支持的文件类型，仅支持图片和视频')
    return
  }
  
  // 验证文件大小（20MB）
  if (file.size > 20 * 1024 * 1024) {
    alert('文件大小不能超过20MB')
    return
  }
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    previewFile.value = {
      file: file,
      url: e.target.result,
      type: file.type,
      name: file.name
    }
  }
  reader.readAsDataURL(file)
}

// 清除预览
const clearPreview = () => {
  previewFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 获取文件URL
const getFileUrl = (url) => {
  if (!url) return ''
  // 如果是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  // /uploads/ 和 /static/ 路径前端nginx已经有代理，直接返回即可
  if (url.startsWith('/uploads/') || url.startsWith('/static/')) {
    return url
  }
  // 其他API路径使用/api代理访问
  return `/api${url}`
}

// 预览图片
const previewImage = (url) => {
  // 可以在这里实现图片预览功能
  window.open(url, '_blank')
}

// 发送消息
const handleSend = async () => {
  const content = inputContent.value.trim()
  const file = previewFile.value?.file
  
  if (!content && !file) return

  // 保存原始内容，用于失败时恢复
  const originalContent = content
  const originalFile = file

  // 乐观UI：先清空输入框和预览
  inputContent.value = ''
  clearPreview()

  try {
    await sendMessage({
      session_id: sessionId,
      sender_id: userStore.userInfo.id,
      content: content || '',
      file: file
    })
    // 发送成功后立即刷新一次
    await fetchMessages()
  } catch (e) {
    // 尽量展示后端真实报错，便于定位（如 413、"消息不能为空"、"不支持的文件类型" 等）
    const msg =
      e?.response?.data?.message ||
      e?.message ||
      '发送失败'
    alert(msg)
    // 失败了恢复内容
    inputContent.value = originalContent
    if (originalFile) {
      const reader = new FileReader()
      reader.onload = (event) => {
        previewFile.value = {
          file: originalFile,
          url: event.target.result,
          type: originalFile.type,
          name: originalFile.name
        }
      }
      reader.readAsDataURL(originalFile)
    }
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  if (!userStore.userInfo) {
    router.push('/login')
    return
  }
  
  // 检查 session_id 是否存在
  if (!sessionId) {
    alert('会话不存在')
    router.push('/chat')
    return
  }
  
  fetchMessages(true)
  
  // 简单的轮询：每3秒去后端查一次有没有新消息
  pollingTimer = setInterval(() => {
    fetchMessages()
  }, 3000)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
</script>

<style scoped>

/* === 添加这两个样式 === */
.home-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.mobile-frame {
  width: 375px;
  height: 812px;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}
/* 适配 iPhone 底部安全区 */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 20px);
}

/* 响应式 */
@media (min-width: 768px) {
  .home-container {
    padding: 0;
    align-items: stretch;
  }
  .mobile-frame {
    width: 100%;
    height: 100vh;
    max-width: 100%;
    border-radius: 0;
    box-shadow: none;
  }
  .status-bar {
    display: none;
  }
}

@media (max-width: 400px) {
  .home-container { padding: 0.5rem; }
  .mobile-frame { width: 100%; height: 100vh; border-radius: 0; }
}
</style>
