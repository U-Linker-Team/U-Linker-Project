<template>
  <div class="home-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>

      <!-- 顶部导航 -->
      <header class="header-bar">
        <div class="header-back" @click="router.push('/home')">
          <span class="iconify" data-icon="mdi:arrow-left"></span>
        </div>
        <span class="app-title">订单中心</span>
        <div class="header-icons">
          <span class="iconify header-icon" data-icon="mdi:refresh" @click="refreshData"></span>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 选项卡 -->
        <div class="order-tabs">
          <div 
            @click="switchTab('published')"
            :class="['tab-item', { 'active': activeTab === 'published' }]"
          >
            <span class="tab-text">我发布的</span>
            <!-- 如果数据加载完了，显示数量 -->
            <span class="tab-badge" v-if="publishedList.length">{{ publishedList.length }}</span>
          </div>
          <div 
            @click="switchTab('accepted')"
            :class="['tab-item', { 'active': activeTab === 'accepted' }]"
          >
            <span class="tab-text">我接受的</span>
            <span class="tab-badge" v-if="acceptedList.length">{{ acceptedList.length }}</span>
          </div>
        </div>

        <!-- 列表展示区域 -->
        <div class="order-list">
          
          <!-- 加载中 -->
          <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">加载中...</div>
          
          <!-- 空状态 -->
          <div v-else-if="currentList.length === 0" class="text-center py-10 text-gray-400 text-sm flex flex-col items-center">
            <span class="iconify w-10 h-10 mb-2 text-gray-300" data-icon="mdi:file-document-outline"></span>
            <span>暂无订单数据</span>
          </div>

          <!-- 订单卡片 -->
          <div 
            v-else
            v-for="order in currentList" 
            :key="order.id"
            class="order-item"
          >
            <!-- 左侧颜色条 (区分悬赏和服务) -->
            <div :class="['order-status-bar', order.post?.post_type === 'bounty' ? 'bg-blue-500' : 'bg-orange-400']"></div>
            
            <!-- 订单内容 -->
            <div class="order-content">
              <div class="order-header">
                <div class="order-tags">
                  <!-- 类型标签 -->
                  <span :class="['tag', order.post?.post_type === 'bounty' ? 'tag-bounty' : 'tag-service']">
                    {{ order.post?.post_type === 'bounty' ? '悬赏' : '服务' }}
                  </span>
                  <!-- 时间 -->
                  <span class="order-time">{{ order.created_at }}</span>
                </div>
                <!-- 状态标签 -->
                <span :class="getStatusClass(order.status)">{{ formatStatus(order.status) }}</span>
              </div>
              
              <!-- 标题 -->
              <h3 class="order-title">{{ order.post?.title }}</h3>
              
              <!-- 对方信息 -->
              <!-- 逻辑：如果是我发布的，显示帮手/卖家信息；如果是我接受的，显示雇主/买家信息 -->
              <div class="order-helper">
                <span class="helper-label">{{ activeTab === 'published' ? '合作方:' : '雇主:' }}</span>
                <div class="helper-info" v-if="getCounterpart(order)">
                  <!-- 头像 -->
                  <div class="w-6 h-6 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center text-[10px]">
                    <img v-if="getCounterpart(order).avatar" :src="getCounterpart(order).avatar" class="w-full h-full object-cover">
                    <span v-else>{{ getCounterpart(order).name?.charAt(0) }}</span>
                  </div>
                  <span class="helper-name">{{ getCounterpart(order).name }}</span>
                </div>
                <div v-else class="helper-info text-gray-400 text-xs">
                   (等待接单中...)
                </div>
              </div>
              
              <!-- 价格信息 -->
              <div class="order-price">
                <template v-if="order.post?.post_type === 'service'">
                  服务价格: <span class="price-value text-orange-500">{{ order.post?.price }} 积分</span>
                </template>
                <template v-else>
                  涉及积分: <span class="price-value text-blue-600">{{ order.post?.price }} 积分</span>
                </template>
              </div>
              
              <!-- 操作按钮 -->
              <div class="order-actions">
                
                <!-- 1. 私聊按钮 (只要对方存在就能聊) -->
                <button v-if="getCounterpart(order)" @click="handleChat(order)" class="action-btn chat-btn">
                  <span class="iconify" data-icon="mdi:message-outline"></span>
                  私聊
                </button>

                <!-- 2. 确认完成按钮 -->
                <!-- 逻辑：只有 pending 状态且符合身份才能操作 -->
                <template v-if="order.status === 'pending'">
                  <!-- 判断是否显示确认按钮 -->
                  <button 
                    v-if="canConfirm(order)"
                    @click="handleConfirm(order)" 
                    class="action-btn complete-btn"
                  >
                    确认完成
                  </button>

                  <!-- 取消按钮 (简化处理，双方在 pending 状态都可以尝试取消) -->
                  <button @click="handleCancel(order)" class="action-btn cancel-btn">取消</button>
                </template>

              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部导航 -->
      <BottomNav active-tab="order" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getMyInvolved, confirmComplete, cancelOrder } from '@/api/transaction'
import { createSession } from '@/api/chat'
import BottomNav from '@/components/common/BottomNav.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 状态变量
const activeTab = ref('published')
const loading = ref(false)
const publishedList = ref([])
const acceptedList = ref([])

// 计算属性：当前显示的列表
const currentList = computed(() => {
  return activeTab.value === 'published' ? publishedList.value : acceptedList.value
})

// 获取当前用户ID（从 userStore）
const currentUserId = computed(() => userStore.userInfo?.id || null)

// 初始化
onMounted(() => {
  // 支持从其他页面带参数跳转过来 (?tab=accepted)
  if (route.query.tab === 'accepted') {
    activeTab.value = 'accepted'
  }
  refreshData()
})

// 2. 刷新数据
const refreshData = async () => {
  await fetchOrders('published')
  await fetchOrders('accepted')
}

// 3. 核心：从后端拉取数据
const fetchOrders = async (role) => {
  //后面几行是到try前面是cursor改的

  //检查登陆状态
  if (!currentUserId.value) {
    console.warn(`[${role}] 用户未登录，跳过加载`)
    return
  }
  
  // 设置 loading 状态（只在第一次调用时设置）
  if (role === 'published') {
    loading.value = true
  }

  try {
    const res = await getMyInvolved({
      role: role,
      page_size: 50
    })
    if (res.status === 'success') {
      if (role === 'published') {
        publishedList.value = res.data.items
      } else {
        acceptedList.value = res.data.items
      }
    }
  } catch (error) {
    console.error(`[${role}] 加载订单失败:`, error)
  } finally {
    // 两个请求都完成后才取消 loading
    if (role === 'accepted') {
      loading.value = false
    }
  }
}

// 切换 Tab
const switchTab = (tab) => {
  activeTab.value = tab
}

// --- 辅助逻辑 ---

// 获取对方信息对象
const getCounterpart = (order) => {
  if (activeTab.value === 'published') {
    // 我发布的 -> 对方是卖家/帮手 (seller_info)
    // 后端返回的字段是 seller_info
    return order.seller_info
  } else {
    // 我接受的 -> 对方是买家/雇主 (buyer_info)
    // 后端返回的字段是 buyer_info
    return order.buyer_info
  }
}

// 状态文案
const formatStatus = (status) => {
  const map = {
    'pending': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return map[status] || status
}

// 状态样式
const getStatusClass = (status) => {
  const base = 'status-tag'
  if (status === 'pending') return `${base} text-blue-600 bg-blue-50`
  if (status === 'completed') return `${base} text-green-600 bg-green-50`
  return `${base} text-gray-500 bg-gray-50`
}

// 判断是否有权确认完成
const canConfirm = (order) => {
  const myId = currentUserId.value
  const isService = order.post?.post_type === 'service'
  
  // 规则：服务由卖家(我)确认，悬赏由买家(我)确认
  if (isService && order.seller_id === myId) return true
  if (!isService && order.buyer_id === myId) return true
  
  return false
}

// --- 交互动作 ---

// 私聊
const handleChat = async (order) => {
  const target = getCounterpart(order)
  if (!target) return
  
  try {
    const res = await createSession({ target_id: target.id })
    if (res.status === 'success') {
      router.push(`/chat/${res.data.session_id}`)
    }
  } catch(e) {
    console.error('发起私聊失败', e)
  }
}

// 确认完成
const handleConfirm = async (order) => {
  if (!confirm('确认任务已完成且资金结算吗？')) return
  try {
    const res = await confirmComplete({ order_id: order.id })
    if (res.status === 'success') {
      // 刷新列表状态
      await refreshData()
    }
  } catch(e) {
    console.error('确认完成失败', e)
    // request.js 的拦截器已经处理了错误提示
  }
}

// 取消订单
const handleCancel = async (order) => {
  if (!confirm('确定要取消订单吗？')) return
  try {
    const res = await cancelOrder({ order_id: order.id })
    if (res.status === 'success') {
      // 刷新列表状态
      await refreshData()
    }
  } catch(e) {
    console.error('取消失败', e)
    // request.js 的拦截器已经处理了错误提示
  }
}
</script>

<style scoped>
/* 样式部分直接复用你之前的，稍微整理一下 */
.home-container { min-height: 100vh; background-color: #f3f4f6; display: flex; justify-content: center; padding: 0; }
.mobile-frame { width: 100%; max-width: 480px; background: white; min-height: 100vh; display: flex; flex-direction: column; position: relative; }
.status-bar { height: 2rem; background: white; flex-shrink: 0; }

.header-bar { height: 3rem; display: flex; justify-content: space-between; align-items: center; padding: 0 1rem; border-bottom: 1px solid #eee; background: white; }
.app-title { font-size: 1.1rem; font-weight: bold; }
.header-icons { display: flex; gap: 1rem; }

.main-content { flex: 1; overflow-y: auto; background: #f9fafb; padding-bottom: 60px; }

/* 选项卡 */
.order-tabs { display: flex; background: white; border-bottom: 1px solid #eee; position: sticky; top: 0; z-index: 10; }
.tab-item { flex: 1; text-align: center; padding: 0.8rem 0; cursor: pointer; font-size: 0.9rem; color: #666; position: relative; display: flex; justify-content: center; align-items: center; gap: 4px; }
.tab-item.active { color: #2563eb; font-weight: bold; }
.tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 20%; height: 3px; background: #2563eb; border-radius: 3px; }
.tab-badge { background: #ef4444; color: white; font-size: 0.6rem; padding: 0.1rem 0.3rem; border-radius: 10px; }

/* 订单列表 */
.order-list { padding: 1rem; display: flex; flex-direction: column; gap: 1rem; }
.order-item { background: white; border-radius: 0.75rem; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); position: relative; overflow: hidden; display: flex; }
.order-status-bar { width: 4px; position: absolute; left: 0; top: 0; bottom: 0; }
.order-content { flex: 1; margin-left: 0.5rem; }

.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.order-tags { display: flex; align-items: center; gap: 0.5rem; }
.tag { font-size: 0.65rem; padding: 1px 4px; border-radius: 4px; border: 1px solid; }
.tag-bounty { color: #2563eb; background: #eff6ff; border-color: #bfdbfe; }
.tag-service { color: #ea580c; background: #fff7ed; border-color: #fed7aa; }
.order-time { font-size: 0.7rem; color: #9ca3af; }
.status-tag { font-size: 0.75rem; padding: 2px 8px; border-radius: 99px; font-weight: bold; }

.order-title { font-size: 0.95rem; font-weight: bold; color: #1f2937; margin-bottom: 0.5rem; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }

.order-helper { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: #6b7280; background: #f9fafb; padding: 0.4rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
.helper-info { display: flex; align-items: center; gap: 0.4rem; font-weight: bold; color: #374151; }

.order-price { font-size: 0.8rem; font-weight: 500; display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; border-top: 1px solid #f3f4f6; padding-top: 0.5rem; }
.price-value { font-weight: bold; font-size: 0.9rem; margin-left: 4px; }

.order-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.action-btn { font-size: 0.75rem; padding: 0.3rem 0.8rem; border-radius: 99px; border: 1px solid #e5e7eb; background: white; color: #4b5563; display: flex; align-items: center; gap: 2px; }
.chat-btn { color: #2563eb; border-color: #bfdbfe; background: #eff6ff; }
.complete-btn { color: white; background: #10b981; border: none; font-weight: bold; }
.cancel-btn { color: #ef4444; border-color: #fecaca; }
</style>