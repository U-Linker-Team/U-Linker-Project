<template>
  <!-- 这里的 UI 完全保留成员 A 的设计 -->
  <div 
    class="modal-bg fixed inset-0 bg-black/50 z-50 flex items-end"
    :class="{ show: show }"
    @click.self="handleClose"
  >
    <div class="modal-panel w-full h-[90%] bg-white rounded-t-3xl flex flex-col overflow-hidden relative">
      <!-- 拖动条 -->
      <div class="flex justify-center py-3 bg-white flex-shrink-0">
        <div class="w-10 h-1 bg-gray-300 rounded-full"></div>
      </div>
      
      <!-- 头部 -->
      <div class="flex items-center justify-between px-5 pb-3 border-b border-gray-100 bg-white flex-shrink-0">
        <span @click="handleClose" class="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center cursor-pointer hover:bg-gray-200">
          <Icon icon="mdi:close" class="w-5 h-5 text-gray-500" />
        </span>
        <h2 class="text-base font-bold text-gray-900">任务详情</h2>
        <!-- 收藏按钮放在这里或者底部都可以 -->
        <span class="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center">
             <Icon icon="mdi:dots-horizontal" class="w-5 h-5 text-gray-500" />
        </span>
      </div>
      
      <!-- 内容滚动区 -->
      <div class="flex-1 overflow-y-auto hide-scrollbar bg-white" v-if="taskData">
        <!-- 发布者信息 -->
        <div class="px-5 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="w-12 h-12 rounded-full bg-blue-50 overflow-hidden flex-shrink-0 flex items-center justify-center text-lg font-bold text-blue-600">
             <!-- 后端数据映射 -->
            <img v-if="taskData.author_info?.avatar" :src="taskData.author_info.avatar" class="w-full h-full object-cover">
            <span v-else>{{ taskData.author_info?.name?.charAt(0) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-gray-800">{{ taskData.author_info?.name }}</div>
            <div class="text-xs text-gray-500">{{ taskData.author_info?.college }} · {{ taskData.created_at }}</div>
          </div>
          <div class="flex flex-col items-end gap-1">
             <span class="bg-blue-50 text-blue-600 px-2.5 py-1 rounded-full text-[10px] font-bold">信用良好</span>
          </div>
        </div>
        
        <!-- 任务详情 -->
        <div class="px-5 py-5">
          <h1 class="text-xl font-bold text-gray-900 leading-snug mb-4">{{ taskData.title }}</h1>
                    <!-- 图片展示区域 -->
          <div v-if="taskData.images" class="mb-5">
            <div class="grid grid-cols-3 gap-2">
              <div 
                v-for="(img, index) in taskData.images.split(',').filter(img => img.trim() !== '')" 
                :key="index" 
                class="aspect-square rounded-xl overflow-hidden bg-gray-100"
              >
                <img 
                  :src="img" 
                  :alt="`任务图片 ${index + 1}`"
                  class="w-full h-full object-cover"
                  @error="(e) => e.target.src = 'https://via.placeholder.com/150'"
                >
              </div>
            </div>
          </div>
     
          <!-- 积分卡片 -->
          <div class="flex items-center justify-between mb-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-4">
            <div>
              <div class="text-xs text-gray-500 mb-1">
                 {{ taskData.post_type === 'bounty' ? '悬赏积分' : '服务价格' }}
              </div>
              <div class="flex items-baseline gap-1">
                <span class="text-3xl font-bold text-blue-600">{{ taskData.price }}</span>
                <span class="text-sm text-gray-500">分</span>
              </div>
            </div>
            <span class="px-4 py-2 text-sm font-bold rounded-xl border bg-white text-blue-600 border-blue-200">
              {{ statusText }}
            </span>
          </div>
          
          <!-- 描述 -->
          <div class="mb-5">
            <h3 class="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <Icon icon="mdi:text-box-outline" class="w-4 h-4 text-blue-500" />
              任务详情
            </h3>
            <div class="text-gray-700 leading-relaxed text-sm bg-gray-50 rounded-xl p-4 whitespace-pre-line">
              {{ taskData.content }}
            </div>
          </div>
          
          <!-- ⬇️⬇️⬇️ 这里的申请记录改成真实渲染 ⬇️⬇️⬇️ -->
          <div v-if="isOwner && taskData.applications?.length > 0" class="mb-5">
            <h3 class="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <Icon icon="mdi:account-group-outline" class="w-4 h-4 text-blue-500" />
              申请记录 <span class="text-gray-400 font-normal">({{ taskData.applications.length }}人)</span>
            </h3>
            <div class="space-y-2">
              <!-- 循环渲染后端返回的 applications -->
              <div 
                v-for="app in taskData.applications" 
                :key="app.application_id || app.id"
                class="bg-gray-50 rounded-xl p-3 flex items-center gap-3"
              >
                <div class="w-9 h-9 rounded-full bg-orange-100 overflow-hidden flex items-center justify-center text-sm font-bold text-orange-600 flex-shrink-0">
                  <img v-if="app.applicant_avatar || app.applicant_info?.avatar" 
                       :src="app.applicant_avatar || app.applicant_info.avatar" 
                       class="w-full h-full object-cover">
                  <span v-else>{{ (app.applicant_name || app.applicant_info?.name || '?').charAt(0) }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-800">{{ app.applicant_name || app.applicant_info?.name }}</div>
                  <p class="text-xs text-gray-500 truncate">{{ app.message || '无留言' }}</p>
                </div>
                
                <!-- 选人按钮 -->
                <button 
                    v-if="app.status === 'pending'"
                    @click="handleSelect(app)"
                    class="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700"
                >
                    选择TA
                </button>
                <span v-else class="text-xs text-gray-400">
                    {{ app.status === 'selected' ? '已选中' : '未选中' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 安全提示 -->
          <div class="bg-orange-50 p-4 rounded-xl flex gap-3 items-start border border-orange-100">
            <Icon icon="mdi:shield-check-outline" class="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
            <p class="text-xs text-orange-600 leading-relaxed">交易过程中请勿脱离平台私下支付。</p>
          </div>
        </div>
      </div>
      
      <!-- 底部操作栏 -->
      <div class="border-t border-gray-100 px-5 py-3 flex gap-3 items-center bg-white flex-shrink-0">
        <button 
          @click="handleChat"
          class="flex-1 h-11 border-2 border-blue-600 text-blue-600 font-bold rounded-2xl flex items-center justify-center gap-2 hover:bg-blue-50"
        >
          <Icon icon="mdi:message-text-outline" class="w-5 h-5" />
          私聊
        </button>

        <!-- 根据身份显示不同按钮 -->
        <template v-if="isOwner">
            <button class="flex-1 h-11 bg-gray-200 text-gray-500 font-bold rounded-2xl flex items-center justify-center">
                {{ taskData?.applications?.length > 0 ? '请在上方选人' : '等待申请...' }}
            </button>
        </template>
        <template v-else>
            <!-- 如果我是路人 (isOwner 为 false) -->
            <!-- 情况 A: 已经申请过了 -->
          <button 
            v-if="hasApplied"
            class="flex-1 h-11 bg-gray-200 text-gray-500 font-bold rounded-2xl flex items-center justify-center cursor-not-allowed"
            disabled
          >
            已申请
          </button>

          <!-- 情况 B: 还没申请，且任务在招募中 -->
          <button 
            v-else-if="taskData?.status === 'active'" 
            @click="showApplyModal = true"
            class="flex-1 h-11 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-bold rounded-2xl flex items-center justify-center shadow-lg active:scale-[0.98] transition-transform"
          >
            我能帮助
          </button>
          
          <!-- 情况 C: 任务已经结束或进行中 -->
          <button 
            v-else
            class="flex-1 h-11 bg-gray-100 text-gray-400 font-bold rounded-2xl flex items-center justify-center cursor-not-allowed"
            disabled
          >
            {{ taskData?.status === 'trading' ? '进行中' : taskData?.status === 'sold' ? '已完成' : '已结束' }}
          </button>
        </template>
      </div>
    </div>

    <!-- 引入申请弹窗 -->
    <ApplyModal 
      :show="showApplyModal" 
      :taskTitle="taskData?.title"
      @close="showApplyModal = false"
      @submit="submitApply"
    />

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getPostDetail } from '@/api/market'
import { applyTask, selectHelper } from '@/api/transaction'
import { createSession } from '@/api/chat'
import ApplyModal from './ApplyModal.vue'

const props = defineProps({
  show: Boolean,
  taskId: [String, Number] // 接收父组件传来的 ID
})

const emit = defineEmits(['close'])
const router = useRouter()
const userStore = useUserStore()

const taskData = ref(null)
const showApplyModal = ref(false)

// 监听 show 变化，一旦打开弹窗，就去后端加载数据
watch(() => props.show, (newVal) => {
  if (newVal && props.taskId) {
    fetchDetail()
  }
})

// 获取当前用户ID（从 userStore）
const currentUserId = computed(() => userStore.userInfo?.id || null)

// 核心：请求后端详情
const fetchDetail = async () => {
  try {
    const res = await getPostDetail(props.taskId)
    if (res.status === 'success') {
      taskData.value = res.data
    }
  } catch (error) {
    console.error("加载详情失败", error)
  }
}

// 计算属性：我是不是雇主
const isOwner = computed(() => {
    return taskData.value?.author_info?.id === currentUserId.value
})

const hasApplied = computed(() => {
    // 如果没有申请列表，肯定没申请过
    if (!taskData.value?.applications) return false
    
    // 遍历申请列表，看看有没有我的 ID
    // 注意：后端返回的字段是 applicant_id
    return taskData.value.applications.some(app => app.applicant_id === currentUserId.value)
})

const statusText = computed(() => {
    const map = { active: '招募中', trading: '进行中', sold: '已完成' }
    return map[taskData.value?.status] || taskData.value?.status
})

// 关闭弹窗
const handleClose = () => {
  emit('close')
}

// 私聊逻辑
const handleChat = async () => {
    try {
        const res = await createSession({
            target_id: taskData.value.author_info.id
        })
        if(res.status === 'success') {
            router.push(`/chat/${res.data.session_id}`)
        }
    } catch(e) {
        console.error('私聊发起失败', e)
    }
}

// 提交申请逻辑
// 注意：ApplyModal 会通过 @submit 事件传递 message 参数
const submitApply = async (message) => {
  // 检查登录状态
  if (!currentUserId.value) {
    alert('请先登录后再申请')
    showApplyModal.value = false
    return
  }
  
  try {
    const res = await applyTask({
      post_id: taskData.value.id,
      message: message || ''
    })
    
    if(res.status === 'success') {
      // 关闭申请弹窗
      showApplyModal.value = false
      // 刷新数据以更新按钮状态（"我能帮助" -> "已申请"）
      await fetchDetail()
    }
  } catch(e) {
    console.error("申请失败", e)
    // request.js 的拦截器已经处理了错误提示
    // 如果是"已经申请过"的错误，关闭弹窗并刷新数据
    if (e.message && e.message.includes('已经申请')) {
      showApplyModal.value = false
      await fetchDetail()
    }
  }
}


// 选人逻辑
const handleSelect = async (app) => {
    if(!confirm(`确定选择 ${app.applicant_name || app.applicant_info?.name} 吗？积分将冻结`)) return;
    
    try {
        const res = await selectHelper({
            post_id: taskData.value.id,
            helper_id: app.applicant_id,
            owner_id: currentUserId.value
        })
        if(res.status === 'success') {
            // 刷新数据以更新状态
            await fetchDetail()
        }
    } catch(e) {
        console.error('选人失败', e)
        // request.js 的拦截器已经处理了错误提示
    }
}
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.modal-bg { opacity: 0; pointer-events: none; transition: opacity 0.3s; }
.modal-bg.show { opacity: 1; pointer-events: auto; }
.modal-panel { transform: translateY(100%); transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1); }
.modal-bg.show .modal-panel { transform: translateY(0); }
</style>