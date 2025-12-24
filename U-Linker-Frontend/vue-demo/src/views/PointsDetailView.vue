<template>
  <PointsModel 
    :isOpen="showPointsModal" 
    @close="showPointsModal = false"
  />

  <div 
    v-if="showHowToGetModal"
    class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center"
    @click.self="showHowToGetModal = false"
  >
    <div class="modal-content bg-white rounded-2xl p-6 mx-4 max-w-sm w-full shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-800">如何获取积分？</h3>
        <button @click="showHowToGetModal = false" class="btn-press">
          <span class="iconify w-6 h-6 text-gray-400" data-icon="mdi:close"></span>
        </button>
      </div>
      <div class="space-y-4">
        <div class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0">
            <span class="iconify w-5 h-5 text-green-500" data-icon="mdi:check-circle-outline"></span>
          </div>
          <div>
            <h4 class="font-bold text-gray-800 text-sm">完成悬赏任务</h4>
            <p class="text-xs text-gray-500 mt-0.5">帮助他人完成任务获得奖励</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-orange-50 flex items-center justify-center flex-shrink-0">
            <span class="iconify w-5 h-5 text-orange-500" data-icon="mdi:briefcase-outline"></span>
          </div>
          <div>
            <h4 class="font-bold text-gray-800 text-sm">提供专业服务</h4>
            <p class="text-xs text-gray-500 mt-0.5">出售技能获得积分收入</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div 
    v-if="showMonthPicker"
    class="fixed inset-0 bg-black/50 z-[60] flex items-end sm:items-center justify-center"
    @click.self="showMonthPicker = false"
  >
    <div class="modal-content bg-white rounded-t-2xl sm:rounded-2xl w-full sm:max-w-sm sm:mx-4 shadow-2xl">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-bold text-gray-800">选择时间范围</h3>
        <button @click="showMonthPicker = false" class="btn-press">
          <span class="iconify w-6 h-6 text-gray-400" data-icon="mdi:close"></span>
        </button>
      </div>
      <div class="p-4 grid grid-cols-2 gap-2">
        <button 
          v-for="month in monthOptions"
          :key="month.value"
          @click="selectMonth(month)"
          :class="[
            'btn-press py-3 rounded-xl text-sm font-medium transition-all',
            selectedMonth === month.value ? 'bg-blue-600 text-white' : 'bg-gray-50 text-gray-600'
          ]"
        >
          {{ month.label }}
        </button>
      </div>
    </div>
  </div>

  <div class="w-full sm:w-[375px] h-[100vh] sm:h-[812px] bg-gray-50 sm:rounded-xl shadow-lg flex flex-col overflow-hidden relative mx-auto">
    <div class="absolute top-0 left-0 w-full h-40 bg-gray-900 z-0"></div>
    <div class="h-8 w-full z-10"></div>

    <header class="h-12 flex items-center justify-between px-4 z-10 relative">
      <button @click="goBack" class="btn-press">
        <span class="iconify w-6 h-6 text-white" data-icon="mdi:arrow-left"></span>
      </button>
      <h1 class="text-lg font-bold text-white">积分明细</h1>
      <button @click="showPointsModal = true" class="btn-press">
        <span class="iconify w-6 h-6 text-white" data-icon="mdi:help-circle-outline"></span>
      </button>
    </header>

    <main class="flex-1 overflow-y-auto hide-scrollbar px-4 pt-4 pb-4 relative z-10">
      <div class="bg-white rounded-2xl p-6 shadow-lg mb-6 text-center relative overflow-hidden">
        <div class="absolute top-0 right-0 w-20 h-20 bg-yellow-50 rounded-bl-full -mr-4 -mt-4 z-0"></div>
        <div class="relative z-10">
          <div class="text-sm text-gray-500 mb-2 flex items-center justify-center gap-1">
            <span class="iconify text-yellow-500" data-icon="mdi:star-four-points"></span>
            当前可用积分
          </div>
          <div class="text-4xl font-bold text-gray-900 font-mono tracking-tight points-animate">
            {{ currentPoints }}
          </div>
          <div class="mt-4 flex justify-center gap-3">
            <button 
              @click="showHowToGetModal = true"
              class="btn-press px-4 py-1.5 bg-blue-50 text-blue-600 text-xs font-bold rounded-full border border-blue-100"
            >
              如何获取?
            </button>
            <button 
              @click="showPointsModal = true"
              class="btn-press px-4 py-1.5 bg-gray-50 text-gray-500 text-xs font-bold rounded-full border border-gray-200"
            >
              积分规则
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between mb-4 px-1">
        <h3 class="font-bold text-gray-800">最近记录</h3>
        <button 
          @click="showMonthPicker = true"
          class="btn-press flex items-center gap-1 text-xs text-gray-500 bg-white px-3 py-1.5 rounded-lg border border-gray-200 shadow-sm"
        >
          {{ currentMonthLabel }}
          <span class="iconify" data-icon="mdi:chevron-down"></span>
        </button>
      </div>

      <div v-if="loading" class="flex flex-col items-center py-10 gap-2">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-xs text-gray-400">加载数据中...</p>
      </div>

      <div v-else class="space-y-3">
        <div 
          v-for="item in transactions"
          :key="item.id"
          class="record-item bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center"
        >
          <div class="flex items-center gap-3">
            <div 
              :class="['w-10 h-10 rounded-full flex items-center justify-center', 
                item.points_change > 0 ? 'bg-green-50' : 'bg-red-50']"
            >
              <span 
                class="iconify w-6 h-6" 
                :class="item.points_change > 0 ? 'text-green-600' : 'text-red-500'"
                :data-icon="item.points_change > 0 ? 'mdi:arrow-down-left' : 'mdi:arrow-top-right'"
              ></span>
            </div>
            <div>
              <div class="text-sm font-bold text-gray-800">{{ item.action }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5 line-clamp-1">{{ item.description }}</div>
              <div class="text-[10px] text-gray-300 mt-0.5">{{ item.created_at }}</div>
            </div>
          </div>
          <div class="text-right">
            <div 
              :class="['text-lg font-bold', item.points_change > 0 ? 'text-green-600' : 'text-red-500']"
            >
              {{ item.points_change > 0 ? '+' : '' }}{{ item.points_change }}
            </div>
          </div>
        </div>

        <div v-if="transactions.length === 0" class="text-center py-12">
          <div class="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <span class="iconify w-8 h-8 text-gray-300" data-icon="mdi:receipt-text-outline"></span>
          </div>
          <p class="text-gray-400 text-sm">暂无记录</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
// 接入你的 API
import { getPointsHistory } from '@/api/transaction'
import { getUserProfile } from '@/api/auth'
// 队友的组件
import PointsModel from '@/components/profile/PointsModel.vue'

const router = useRouter()
const userStore = useUserStore()

// 状态管理
const loading = ref(false)
const showHowToGetModal = ref(false)
const showPointsModal = ref(false)
const showMonthPicker = ref(false)
const selectedMonth = ref('all')
const transactions = ref([])

// 队友的配置项
const monthOptions = [
  { label: '全部记录', value: 'all' },
  { label: '本月', value: 'current' },
  { label: '上月', value: 'last' },
  { label: '近3月', value: '3months' },
]

// 计算当前余额 (来自 Store)
const currentPoints = computed(() => userStore.userInfo?.points || 0)

const currentMonthLabel = computed(() => {
  return monthOptions.find(m => m.value === selectedMonth.value)?.label || '筛选'
})

// 核心逻辑：获取后端数据
const fetchData = async () => {
  if (!userStore.userInfo?.id) return
  
  loading.value = true
  try {
    // 1. 获取流水列表 (这里可以根据 selectedMonth.value 传参给后端进行筛选)
    const res = await getPointsHistory({ 
      user_id: userStore.userInfo.id,
      page: 1, 
      page_size: 10,
      period: selectedMonth.value // 假设后端支持按周期筛选
    })
    transactions.value = res.data.items

    // 2. 刷新用户个人资料以同步余额
    const userRes = await getUserProfile(userStore.userInfo.id)
    userStore.login(userRes.data) // 更新全局 Store
    
  } catch (e) {
    console.error('获取数据失败:', e)
  } finally {
    loading.value = false
  }
}

const selectMonth = (month) => {
  selectedMonth.value = month.value
  showMonthPicker.value = false
  fetchData() // 切换月份时重新加载
}

const goBack = () => router.back()

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 融合队友的精美 CSS */
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.btn-press { transition: transform 0.1s ease; }
.btn-press:active { transform: scale(0.95); }

.points-animate { animation: pointsIn 0.5s cubic-bezier(0.17, 0.67, 0.83, 0.67); }
@keyframes pointsIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-content { animation: modalIn 0.2s ease-out; }
@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.record-item { transition: all 0.2s ease; }
.record-item:active { background-color: #f9fafb; transform: scale(0.98); }
</style>