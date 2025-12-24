<!-- 我的-收藏 -->

<template>
  <!-- 外部居中容器 -->
  <div class="w-full min-h-screen bg-gray-100 flex justify-center items-center p-4">
    <!-- 手机容器 -->
    <div class="w-full sm:w-[375px] h-[100vh] sm:h-[812px] bg-white sm:rounded-xl shadow-lg flex flex-col overflow-hidden relative">
      <!-- 状态栏占位 -->
      <div class="h-8 bg-white w-full flex-shrink-0"></div>

      <!-- 头部 -->
      <header class="h-14 flex items-center justify-between px-4 border-b border-gray-100 bg-white z-20 sticky top-0">
        <!-- 直接使用 a 标签跳转 -->
        <a :href="profileUrl" class="flex items-center" @click.prevent="goToProfile">
          <span 
            class="iconify w-6 h-6 text-gray-600" 
            data-icon="mdi:arrow-left"
          ></span>
        </a>
        <h1 class="text-lg font-bold text-gray-900">我的收藏</h1>
        <span 
          class="text-sm text-gray-400 cursor-pointer hover:text-gray-600 transition-colors"
          @click="toggleManageMode"
        >
          {{ isManaging ? '完成' : '管理' }}
        </span>
      </header>

      <!-- 主要内容区域 -->
      <main class="flex-1 overflow-y-auto hide-scrollbar bg-gray-50 px-4 py-4 space-y-3">
        <!-- 空状态提示 -->
        <div v-if="collectItems.length === 0" class="flex flex-col items-center justify-center h-64">
          <span class="iconify text-6xl text-gray-300 mb-4" data-icon="mdi:heart-outline"></span>
          <p class="text-gray-500 mb-2">暂无收藏</p>
          <p class="text-sm text-gray-400">快去发现你感兴趣的任务吧</p>
        </div>

        <!-- 收藏项目列表 -->
        <div 
          v-for="item in collectItems" 
          :key="item.id"
          class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 relative overflow-hidden transition-all duration-300"
          :class="{ 'opacity-60': item.status === '已结束' }"
        >
          <!-- 左侧颜色条 -->
          <div 
            class="absolute left-0 top-0 bottom-0 w-1"
            :class="{
              'bg-blue-500': item.type === '悬赏',
              'bg-orange-500': item.type === '服务',
              'bg-gray-300': item.status === '已结束'
            }"
          ></div>

          <!-- 顶部信息 -->
          <div class="flex justify-between items-start mb-2 pl-2">
            <div class="flex items-center gap-2">
              <!-- 类型标签 -->
              <span 
                class="text-[10px] font-bold px-1.5 py-0.5 rounded border"
                :class="getTypeClass(item.type, item.status)"
              >
                {{ item.type }}
              </span>
              
              <!-- 发布者/时间 -->
              <div class="flex items-center gap-1 text-xs" :class="item.status === '已结束' ? 'text-gray-400' : 'text-gray-400'">
                <span 
                  class="iconify"
                  :data-icon="item.type === '悬赏' ? 'mdi:account' : 'mdi:briefcase-account'"
                ></span>
                {{ item.publisher }}
              </div>
            </div>
            
            <!-- 状态标签 -->
            <span 
              class="text-xs font-medium px-2 py-0.5 rounded"
              :class="getStatusClass(item.status)"
            >
              {{ item.status }}
            </span>
          </div>

          <!-- 主要内容 -->
          <div class="pl-2 mb-3">
            <h3 
              class="font-bold text-sm mb-1"
              :class="item.status === '已结束' ? 'text-gray-600 line-through' : 'text-gray-800'"
            >
              {{ item.title }}
            </h3>
            <div 
              class="font-bold text-sm"
              :class="item.status === '已结束' ? 'text-gray-400' : (item.type === '悬赏' ? 'text-blue-600' : 'text-orange-500')"
            >
              {{ item.price }} <span class="text-xs font-normal text-gray-400">{{ item.unit }}</span>
            </div>
          </div>

          <!-- 底部操作按钮 -->
          <div class="flex justify-end gap-3 border-t border-gray-50 pt-3 pl-2">
            <!-- 失效提示 -->
            <span 
              v-if="item.status === '已结束'"
              class="text-xs text-red-400 flex items-center mr-auto"
            >
              <span class="iconify w-3 h-3 mr-1" data-icon="mdi:alert-circle-outline"></span>
              帖子已失效
            </span>
            
            <!-- 取消收藏/移除按钮 -->
            <button 
              v-if="!isManaging && item.status !== '已结束'"
              class="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
              @click="cancelCollect(item.id)"
            >
              <span class="iconify" data-icon="mdi:heart-off-outline"></span>
              取消收藏
            </button>
            
            <button 
              v-if="isManaging && item.status === '已结束'"
              class="flex items-center gap-1 text-xs text-gray-500 border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors"
              @click="removeItem(item.id)"
            >
              移除
            </button>
            
            <!-- 查看详情/购买按钮 -->
            <button 
              v-if="item.status !== '已结束'"
              class="flex items-center gap-1 text-xs font-bold px-3 py-1.5 rounded-lg"
              :class="getActionButtonClass(item.type)"
              @click="handleAction(item)"
            >
              {{ item.type === '悬赏' ? '查看详情' : '立即购买' }}
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态
const isManaging = ref(false)
const collectItems = ref([
  {
    id: 1,
    type: '悬赏',
    publisher: '王同学',
    title: '求高等数学(下)期末复习辅导',
    price: 25,
    unit: '积分/小时',
    status: '招募中'
  },
  {
    id: 2,
    type: '服务',
    publisher: '李设计',
    title: '专业PPT美化与定制设计',
    price: 50,
    unit: '积分/次',
    status: '上架中'
  },
  {
    id: 3,
    type: '悬赏',
    publisher: '张同学',
    title: '代拿东门圆通快递',
    price: 10,
    unit: '积分',
    status: '已结束'
  }
])

// 计算属性
const profileUrl = computed(() => {
  // 根据当前环境生成正确的URL
  const baseUrl = window.location.origin
  return `${baseUrl}/profile`
})

// 方法
const getTypeClass = (type, status) => {
  if (status === '已结束') {
    return 'bg-gray-100 text-gray-500 border-gray-100'
  }
  return type === '悬赏' 
    ? 'bg-blue-50 text-blue-600 border-blue-100' 
    : 'bg-orange-50 text-orange-500 border-orange-100'
}

const getStatusClass = (status) => {
  switch(status) {
    case '招募中': return 'text-gray-500 bg-gray-100'
    case '上架中': return 'text-green-600 bg-green-50'
    case '已结束': return 'text-white bg-gray-400'
    default: return 'text-gray-500 bg-gray-100'
  }
}

const getActionButtonClass = (type) => {
  return type === '悬赏' 
    ? 'text-blue-600 bg-blue-50 hover:bg-blue-100' 
    : 'text-orange-500 bg-orange-50 hover:bg-orange-100'
}

const goToProfile = () => {
  console.log('跳转到个人中心')
  console.log('router对象:', router)
  
  // 方法1：优先使用 Vue Router
  try {
    router.push('/profile')
  } catch (error) {
    console.log('Router跳转失败:', error)
    
    // 方法2：使用浏览器跳转
    setTimeout(() => {
      window.location.href = '/profile'
    }, 0)
  }
}

const toggleManageMode = () => {
  isManaging.value = !isManaging.value
  console.log(isManaging.value ? '进入管理模式' : '退出管理模式')
}

const cancelCollect = (id) => {
  if (confirm('确定要取消收藏吗？')) {
    collectItems.value = collectItems.value.filter(item => item.id !== id)
    console.log('已取消收藏', id)
  }
}

const removeItem = (id) => {
  collectItems.value = collectItems.value.filter(item => item.id !== id)
  console.log('已移除项目', id)
}

const handleAction = (item) => {
  if (item.type === '悬赏') {
    console.log('查看详情:', item.id)
  } else {
    console.log('立即购买:', item.id)
    if (confirm(`确定要购买【${item.title}】吗？`)) {
      console.log('购买成功')
    }
  }
}
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar { 
  display: none; 
}
.hide-scrollbar { 
  -ms-overflow-style: none; 
  scrollbar-width: none; 
}

/* 确保链接样式正确 */
a {
  text-decoration: none;
  color: inherit;
}

.iconify {
  transition: transform 0.1s ease;
}

.iconify:active {
  transform: scale(0.9);
}
</style>