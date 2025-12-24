<template>
  <div 
    @click="handleClick"
    class="card-animate bg-white p-4 rounded-2xl mb-3 border border-gray-100 shadow-sm cursor-pointer hover:shadow-md hover:border-blue-100 transition-all"
    :class="{ 'opacity-60': displayItem.isCompleted }"
    :style="{ animationDelay: `${delay}s`, opacity: 0 }"
  >
    <!-- 头部：用户信息 + 积分/价格 -->
    <div class="flex justify-between items-start mb-3">
      <div class="flex items-center gap-2.5">
        <!-- 头像区域 -->
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 overflow-hidden flex-shrink-0 flex items-center justify-center text-sm font-bold text-blue-600 shadow-inner">
          <img 
            v-if="displayItem.avatar" 
            :src="displayItem.avatar" 
            class="w-full h-full object-cover"
            @error="(e) => e.target.style.display = 'none'"
          >
          <!-- 没有头像显示首字 -->
          <span v-else>{{ displayItem.name[0] }}</span>
        </div>
        
        <!-- 用户名与时间 -->
        <div>
          <div class="text-sm font-bold text-gray-800">{{ displayItem.name }}</div>
          <div class="text-[11px] text-gray-400 flex items-center gap-1">
            <span>{{ displayItem.time }}</span>
            <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
            <!-- 学院字段后端暂时没有，先写死或隐藏 -->
            <span>{{ displayItem.college || '未知学院' }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧积分展示 (区分悬赏和服务) -->
      <div class="text-right">
        <div 
          class="font-bold text-xl"
          :class="[
            displayItem.isCompleted ? 'text-gray-400' : '',
            displayItem.type === 'bounty' ? 'text-blue-600' : 'text-orange-500'
          ]"
        >
          {{ displayItem.priceDisplay }}
        </div>
        <div class="text-[10px] text-gray-400">
          {{ displayItem.type === 'bounty' ? '积分悬赏' : '服务价格' }}
        </div>
      </div>
    </div>
    
    <!-- 标题 -->
    <h3 
      class="font-bold text-[15px] mb-2.5 leading-snug line-clamp-2"
      :class="displayItem.isCompleted ? 'text-gray-400' : 'text-gray-900'"
    >
      {{ displayItem.title }}
    </h3>
    
    <!-- 底部：标签 + 状态 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-1.5 flex-wrap">
        <!-- 类型标签 -->
        <span 
          class="px-2 py-0.5 text-[10px] rounded-md border font-medium"
          :class="displayItem.type === 'bounty' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-orange-50 text-orange-600 border-orange-100'"
        >
          {{ displayItem.type === 'bounty' ? '求助' : '服务' }}
        </span>
        
        <!-- 状态标签 -->
        <span 
          class="px-2 py-0.5 text-[10px] rounded-md border font-medium"
          :class="statusStyles[displayItem.statusKey]"
        >
          {{ displayItem.statusText }}
        </span>
      </div>

      <!-- 数据统计 (后端暂无，显示模拟数据或静态图标) -->
      <div class="flex items-center gap-3 text-[11px] text-gray-400">
        <span class="flex items-center gap-0.5">
          <Icon icon="mdi:eye-outline" class="w-3.5 h-3.5" />
          {{ displayItem.views || 0 }}
        </span>
        <span class="flex items-center gap-0.5">
          <Icon icon="mdi:account-multiple-outline" class="w-3.5 h-3.5" />
          申请
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

// 1. 接收父组件传来的 data (对应后端的一条 Post 数据)
const props = defineProps({
  data: { 
    type: Object,
    required: true
  },
  delay: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['click'])
const handleClick = () => {
  console.log('[TaskCard] 卡片被点击了！数据ID:', props.data?.id)
  emit('click')
}

// 2. 数据适配层 (核心修改！！！)
// 将后端复杂的结构，转换成模板需要的简单结构
const displayItem = computed(() => {
  const raw = props.data || {}
  
  // 状态映射：后端状态 -> 前端样式Key
  let statusKey = 'recruiting'
  let statusText = '进行中'
  let isCompleted = false

  if (raw.status === 'active') {
    statusKey = 'recruiting'
    statusText = '招募中'
  } else if (raw.status === 'trading') {
    statusKey = 'ongoing'
    statusText = '交易中'
  } else if (raw.status === 'completed' || raw.status === 'sold') {
    statusKey = 'completed'
    statusText = '已完成'
    isCompleted = true
  }

  // 价格展示
  const priceDisplay = raw.post_type === 'bounty' 
    ? `+${raw.price}` 
    : `${raw.price}`

  return {
    id: raw.id,
    title: raw.title,
    // 防止 author 为空导致报错
    name: raw.author ? raw.author.name : '未知用户',
    avatar: raw.author ? raw.author.avatar : '',
    college: raw.author ? raw.author.college : '', 
    time: raw.created_at ? raw.created_at.split(' ')[0] : '刚刚', // 只显示日期
    priceDisplay,
    type: raw.post_type, // 'bounty' 或 'service'
    statusKey,
    statusText,
    isCompleted,
    views: Math.floor(Math.random() * 100) + 1 // 模拟浏览量
  }
})

// 3. 样式映射表 (保留朋友的配色)
const statusStyles = {
  recruiting: 'bg-blue-50 text-blue-600 border-blue-200', // 招募中
  ongoing: 'bg-yellow-50 text-yellow-600 border-yellow-200', // 进行中
  completed: 'bg-gray-100 text-gray-500 border-gray-200' // 已完成
}
</script>

<style scoped>
@keyframes cardSlideIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.card-animate { animation: cardSlideIn 0.35s ease-out forwards; }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
