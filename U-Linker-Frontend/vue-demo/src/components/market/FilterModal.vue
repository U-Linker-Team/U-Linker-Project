<template>
  <div 
    class="filter-modal absolute inset-0 bg-black/40 z-50"
    :class="{ show: true }"
    @click.self="$emit('close')"
  >
    <div class="filter-panel absolute top-36 left-4 right-4 bg-white rounded-2xl shadow-2xl p-5 max-h-[60%] overflow-y-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-gray-900">筛选条件</h3>
        <span @click="handleReset" class="text-sm text-blue-600 cursor-pointer">重置</span>
      </div>
      
      <!-- 状态筛选 -->
      <div class="mb-5">
        <div class="text-sm font-medium text-gray-700 mb-2">任务状态</div>
        <div class="flex flex-wrap gap-2">
          <span 
            v-for="option in statusOptions" 
            :key="option.value"
            @click="localFilterStatus = option.value"
            :class="[
              'px-3 py-1.5 text-xs rounded-full cursor-pointer transition-all',
              localFilterStatus === option.value 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ option.label }}
          </span>
        </div>
      </div>
      
      <!-- 积分范围 -->
      <div class="mb-5">
        <div class="text-sm font-medium text-gray-700 mb-2">积分范围</div>
        <div class="flex items-center gap-3">
          <input 
            v-model.number="localPointsMin" 
            type="number" 
            placeholder="最低" 
            class="flex-1 px-3 py-2 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
          >
          <span class="text-gray-400">—</span>
          <input 
            v-model.number="localPointsMax" 
            type="number" 
            placeholder="最高" 
            class="flex-1 px-3 py-2 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
          >
        </div>
      </div>
      
      <!-- 学院筛选 -->
      <div class="mb-5">
        <div class="text-sm font-medium text-gray-700 mb-2">发布学院</div>
        <div class="flex flex-wrap gap-2">
          <span 
            v-for="option in collegeOptions" 
            :key="option.value"
            @click="localFilterCollege = option.value"
            :class="[
              'px-3 py-1.5 text-xs rounded-full cursor-pointer transition-all',
              localFilterCollege === option.value 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ option.label }}
          </span>
        </div>
      </div>
      
      <!-- 确认按钮 -->
      <button 
        @click="handleApply"
        class="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-200/50 active:scale-[0.98] transition-transform"
      >
        确认筛选
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  filterStatus: {
    type: String,
    default: 'all'
  },
  filterCollege: {
    type: String,
    default: 'all'
  },
  pointsMin: {
    type: Number,
    default: null
  },
  pointsMax: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['close', 'apply', 'reset'])

// 本地状态
const localFilterStatus = ref(props.filterStatus)
const localFilterCollege = ref(props.filterCollege)
const localPointsMin = ref(props.pointsMin)
const localPointsMax = ref(props.pointsMax)

// 监听 props 变化
watch(() => props.filterStatus, (val) => localFilterStatus.value = val)
watch(() => props.filterCollege, (val) => localFilterCollege.value = val)
watch(() => props.pointsMin, (val) => localPointsMin.value = val)
watch(() => props.pointsMax, (val) => localPointsMax.value = val)

const statusOptions = [
  { value: 'all', label: '全部' },
  { value: 'recruiting', label: '招募中' },
  { value: 'ongoing', label: '进行中' },
  { value: 'completed', label: '已完成' }
]

const collegeOptions = [
  { value: 'all', label: '全部' },
  { value: 'cs', label: '计算机' },
  { value: 'math', label: '数学系' },
  { value: 'foreign', label: '外国语' },
  { value: 'art', label: '艺术' },
  { value: 'econ', label: '经济' }
]

const handleApply = () => {
  emit('apply', {
    status: localFilterStatus.value,
    college: localFilterCollege.value,
    pointsMin: localPointsMin.value || null,
    pointsMax: localPointsMax.value || null
  })
}

const handleReset = () => {
  localFilterStatus.value = 'all'
  localFilterCollege.value = 'all'
  localPointsMin.value = null
  localPointsMax.value = null
  emit('reset')
}
</script>

<style scoped>
.filter-modal { opacity: 0; pointer-events: none; transition: opacity 0.25s; }
.filter-modal.show { opacity: 1; pointer-events: auto; }
.filter-panel { transform: translateY(-10px); opacity: 0; transition: all 0.25s ease-out; }
.filter-modal.show .filter-panel { transform: translateY(0); opacity: 1; }
</style>
