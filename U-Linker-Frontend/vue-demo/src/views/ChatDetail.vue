<template>
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
          class="max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm break-words"
          :class="isMe(msg.sender_id) 
            ? 'bg-blue-600 text-white rounded-tr-none' 
            : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'"
        >
          {{ msg.content }}
        </div>
        
        <!-- 时间戳 -->
        <span class="text-[10px] text-gray-400 px-1">
          {{ formatTime(msg.created_at) }}
        </span>
      </div>
    </div>

    <!-- 底部输入框 (固定) -->
    <div class="bg-white border-t border-gray-200 p-3 pb-safe flex items-end gap-2">
      <textarea 
        v-model="inputContent"
        rows="1"
        class="flex-1 bg-gray-100 border-0 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all resize-none max-h-24 outline-none"
        placeholder="发送消息..."
        @keyup.enter.prevent="handleSend"
      ></textarea>
      
      <button 
        @click="handleSend"
        :disabled="!inputContent.trim()"
        class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-md active:scale-95 transition-all disabled:opacity-50 disabled:shadow-none"
      >
        发送
      </button>
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

const sessionId = route.params.session_id
const messages = ref([])
const inputContent = ref('')
const scrollContainer = ref(null)
const loading = ref(false)
const targetName = ref('聊天') // 暂时用默认值，后端可以在 getHistory 里返回对方名字优化体验
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

// 发送消息
const handleSend = async () => {
  const content = inputContent.value.trim()
  if (!content) return

  // 乐观UI：先清空输入框，防止重复点击
  inputContent.value = '' 

  try {
    await sendMessage({
      session_id: sessionId,
      sender_id: userStore.userInfo.id,
      content: content
    })
    // 发送成功后立即刷新一次
    await fetchMessages()
  } catch (e) {
    alert('发送失败')
    inputContent.value = content // 失败了把字填回去
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
/* 适配 iPhone 底部安全区 */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 20px);
}
</style>