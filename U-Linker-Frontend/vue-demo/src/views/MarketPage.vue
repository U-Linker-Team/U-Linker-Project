<template>
  <div class="w-full h-full bg-white flex flex-col overflow-hidden relative">
    <!-- 顶部占位 -->
    <div class="h-8 bg-white w-full flex-shrink-0"></div>
    
    <!-- 头部区域 -->
    <header class="bg-white z-20 flex-shrink-0 px-4 pb-2 border-b border-gray-50">
      <div class="h-10 flex items-center justify-center relative mb-2">
        <h1 class="text-lg font-bold text-gray-900">任务市场</h1>
      </div>
      
      <!-- 搜索栏 -->
      <div class="flex items-center gap-2 mb-4">
        <div class="flex-1 bg-gray-100 rounded-full flex items-center px-4 py-2">
          <span class="text-gray-400 mr-2">
            <!-- 搜索图标 -->
            <svg class="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5l-1.5 1.5l-5-5v-.79l-.27-.27A6.516 6.516 0 0 1 9.5 16A6.5 6.5 0 0 1 3 9.5A6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14S14 12 14 9.5S12 5 9.5 5Z"/></svg>
          </span>
          <!-- 绑定 v-model 和 键盘事件 -->
          <input 
            v-model="searchKeyword"
            @keyup.enter="fetchTasks"
            type="text" 
            class="bg-transparent w-full text-sm focus:outline-none text-gray-800" 
            placeholder="搜索任务或服务... (回车搜索)" 
          />
        </div>
      </div>
      
      <!-- Tab切换 (悬赏 vs 服务) -->
      <div class="flex gap-4 mb-3">
        <button @click="switchTab('bounty')" 
          :class="['flex-1 py-2 rounded-lg font-bold text-sm border flex items-center justify-center gap-1 active:scale-95 transition-transform',
            currentType === 'bounty' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-gray-50 text-gray-500 border-gray-100 hover:bg-blue-50 hover:text-blue-500 hover:border-blue-100']">
          我需要 (悬赏)
        </button>
        <button @click="switchTab('service')" 
          :class="['flex-1 py-2 rounded-lg font-medium text-sm border flex items-center justify-center gap-1 active:scale-95 transition-transform',
            currentType === 'service' ? 'bg-orange-50 text-orange-500 border-orange-100' : 'bg-gray-50 text-gray-500 border-gray-100 hover:bg-orange-50 hover:text-orange-500 hover:border-orange-100']">
          我能提供 (服务)
        </button>
      </div>
      
      <!-- 排序筛选栏 -->
      <div class="flex items-center gap-2 overflow-x-auto hide-scrollbar pb-1">
        <span 
          @click="switchSort('time')"
          :class="['px-3 py-1 rounded-full text-xs flex-shrink-0 font-medium cursor-pointer', 
            currentSort === 'time' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
          按时间
        </span>
        <span 
          @click="switchSort('price')"
          :class="['px-3 py-1 rounded-full text-xs flex-shrink-0 font-medium cursor-pointer', 
            currentSort === 'price' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
          按积分
        </span>
      </div>
    </header>

    <!-- 列表主内容 -->
    <main class="flex-1 overflow-y-auto hide-scrollbar bg-gray-50 px-4 py-4 space-y-3 pb-20">
      
      <!-- 加载中状态 -->
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">
        加载数据中...
      </div>

      <!-- 空状态 -->
      <div v-else-if="tasks.length === 0" class="text-center py-10 text-gray-400 text-sm flex flex-col items-center">
        <span>暂无相关帖子</span>
        <button @click="fetchTasks" class="mt-2 text-blue-500 text-xs">点击刷新</button>
      </div>

      <!-- 任务卡片列表 -->
      <div v-else v-for="task in tasks" :key="task.id" 
        @click="openDetail(task.id)"
        class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-3 relative overflow-hidden cursor-pointer hover:bg-gray-50 transition-colors">
        
        <!-- 卡片头部：头像与价格 -->
        <div class="flex justify-between items-start">
          <div class="flex items-center gap-2">
            <!-- 头像 -->
            <div class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center text-gray-500 font-bold text-sm">
              <img v-if="task.author?.avatar" :src="task.author.avatar" class="w-full h-full object-cover">
              <span v-else>{{ task.author?.name?.charAt(0) || 'U' }}</span>
            </div>
            <!-- 用户名与学院 -->
            <div>
              <div class="text-sm font-bold text-gray-800">{{ task.author?.name || '未知用户' }}</div>
              <div class="text-xs text-gray-400">{{ task.created_at }} · {{ task.author?.college || '未知学院' }}</div>
            </div>
          </div>
          <!-- 价格/积分 -->
          <div class="text-blue-600 font-bold text-lg flex items-baseline">
            {{ task.price }} <span class="text-xs ml-0.5 font-normal">积分</span>
          </div>
        </div>
               <!-- 如果有图片，显示图片缩略图 -->
        <div v-if="task.images" class="relative">
          <div class="grid grid-cols-3 gap-1">
            <div 
              v-for="(img, index) in task.images.split(',').filter(img => img.trim() !== '').slice(0, 3)" 
              :key="index" 
              class="aspect-square rounded-lg overflow-hidden bg-gray-100"
            >
              <img 
                :src="img" 
                :alt="`任务图片 ${index + 1}`"
                class="w-full h-full object-cover"
                @error="(e) => e.target.src = 'https://via.placeholder.com/100'"
              >
            </div>
            <!-- 如果有超过3张图片，显示更多指示 -->
            <div v-if="task.images.split(',').filter(img => img.trim() !== '').length > 3" 
                 class="aspect-square rounded-lg bg-gray-200 flex items-center justify-center text-xs text-gray-500">
              +{{ task.images.split(',').filter(img => img.trim() !== '').length - 3 }}
            </div>
          </div>
        </div>
        
        <!-- 卡片内容：标题与标签 -->
        <div>
          <h3 class="font-bold text-gray-900 text-base mb-2 text-left line-clamp-2">{{ task.title }}</h3>
          <div class="flex gap-2">
            <span :class="['px-2 py-0.5 text-[10px] rounded border', 
              task.post_type === 'bounty' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-orange-50 text-orange-600 border-orange-100']">
              {{ task.post_type === 'bounty' ? '悬赏' : '服务' }}
            </span>
            <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded">
              {{ formatStatus(task.status) }}
            </span>
          </div>
        </div>
      </div>
    </main>

    <!-- 浮动发布按钮 (跳转发布页) -->
    <button 
      @click="goToPublish"
      class="absolute bottom-20 right-6 w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center shadow-lg shadow-blue-300 z-30 active:scale-95 transition-transform hover:bg-blue-700"
    >
      <span class="text-white">
        <svg class="w-8 h-8" viewBox="0 0 24 24"><path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2Z"/></svg>
      </span>
    </button>

    <!-- 底部导航 (复用组件) -->
    <BottomNav active-tab="market" />

    <!-- 任务详情弹窗 (复用组件) -->
    <TaskDetailModal 
      :show="showDetail" 
      :taskId="currentTaskId"
      @close="showDetail = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPostList } from '@/api/market'
import BottomNav from '@/components/common/BottomNav.vue'
import TaskDetailModal from '@/components/market/TaskDetailModal.vue'

const router = useRouter()

// ================= 状态管理 =================
const tasks = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const currentType = ref('bounty') // 默认为悬赏 (bounty)
const currentSort = ref('time')   // 默认为时间 (time)

const showDetail = ref(false)
const currentTaskId = ref(null)

// ================= API 请求 =================
const fetchTasks = async () => {
  loading.value = true
  tasks.value = [] // 清空旧数据防止闪烁
  try {
    const res = await getPostList({
      type: currentType.value,
      keyword: searchKeyword.value,
      sort: currentSort.value,
      page: 1, // 暂时不处理分页，先拉第一页
      page_size: 50
    })
    
    if (res.status === 'success') {
      tasks.value = res.data.items
    }
  } catch (error) {
    console.error("获取列表失败:", error)
    // alert("网络错误，无法加载列表") // 调试时可以打开，上线建议用 Toast
  } finally {
    loading.value = false
  }
}

// ================= 交互逻辑 =================

// 切换 Tab (悬赏/服务)
const switchTab = (type) => {
  if (currentType.value === type) return
  currentType.value = type
  fetchTasks() // 重新请求
}

// 切换排序
const switchSort = (sort) => {
  if (currentSort.value === sort) return
  currentSort.value = sort
  fetchTasks() // 重新请求
}

// 跳转发布页
const goToPublish = () => {
  router.push(`/publish?type=${currentType.value}`) // 带上当前类型参数
}

// 打开详情弹窗
const openDetail = (id) => {
  currentTaskId.value = id
  showDetail.value = true
}

// 格式化状态显示
const formatStatus = (status) => {
  const map = {
    'active': '招募中',
    'trading': '进行中',
    'sold': '已完成',
    'deleted': '已下架'
  }
  return map[status] || status
}

// 页面加载时请求数据
onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
/* 隐藏滚动条但保留功能 */
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
