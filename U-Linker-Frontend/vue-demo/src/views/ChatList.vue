<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部标题 -->
    <header class="bg-white border-b border-gray-200 h-14 flex items-center justify-center sticky top-0 z-10 px-4">
      <span class="text-lg font-bold text-gray-800">消息中心</span>
    </header>

    <!-- 列表内容 -->
    <div class="p-0">
      <!-- 加载中 -->
      <div v-if="loading" class="p-4 text-center text-gray-400 text-sm">
        加载会话中...
      </div>

      <!-- 空状态 -->
      <div v-else-if="list.length === 0" class="flex flex-col items-center justify-center mt-20 text-gray-400">
        <span class="iconify text-6xl mb-2" data-icon="mdi:message-off-outline"></span>
        <p>暂无消息记录</p>
      </div>

      <!-- 会话列表 -->
      <div v-else>
        <div 
          v-for="item in list" 
          :key="item.session_id"
          @click="goToChat(item.session_id)"
          class="bg-white p-4 border-b border-gray-100 flex items-center gap-3 active:bg-gray-50 transition-colors cursor-pointer"
        >
          <!-- 头像 -->
          <div class="relative w-12 h-12 flex-shrink-0">
            <img 
              :src="item.target_user.avatar || 'https://via.placeholder.com/100'" 
              class="w-full h-full rounded-full object-cover border border-gray-100"
              @error="(e) => e.target.src = 'https://via.placeholder.com/100'"
            />
            <!-- 未读红点 -->
            <span v-if="item.unread_count > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] min-w-[1.2rem] h-[1.2rem] flex items-center justify-center rounded-full px-1 border-2 border-white">
              {{ item.unread_count }}
            </span>
          </div>

          <!-- 信息区域 -->
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-center mb-1">
              <h3 class="font-bold text-gray-800 text-base truncate">{{ item.target_user.name || item.target_user.username }}</h3>
              <span class="text-xs text-gray-400 flex-shrink-0">{{ formatTime(item.updated_at) }}</span>
            </div>
            <p class="text-sm text-gray-500 truncate">{{ item.last_message || '暂无消息' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 (复用组件) -->
    <BottomNav active-tab="message" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getChatList } from '@/api/chat'
import BottomNav from '@/components/common/BottomNav.vue'

const router = useRouter()
const userStore = useUserStore()
const list = ref([])
const loading = ref(false)

const fetchData = async () => {
  if (!userStore.userInfo) return router.push('/login')
  
  try {
    loading.value = true
    const res = await getChatList(userStore.userInfo.id)
    list.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goToChat = (sessionId) => {
  router.push(`/chat/${sessionId}`)
}

// 简单的时间格式化
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  // 如果是今天的消息，只显示时间
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  // 否则显示日期
  return date.toLocaleDateString()
}

onMounted(() => {
  fetchData()
})
</script>