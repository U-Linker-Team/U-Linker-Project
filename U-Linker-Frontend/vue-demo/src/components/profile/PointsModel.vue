<!-- 我的-积分规则弹窗 -->

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title">
          <div class="title-icon">
            <span class="iconify" data-icon="mdi:information-circle-outline"></span>
          </div>
          <h3>积分规则</h3>
        </div>
        <button class="close-btn" @click="closeModal">
          <span class="iconify" data-icon="mdi:close"></span>
        </button>
      </div>

      <div class="modal-body" @scroll="handleScroll">
        <!-- 规则说明区域 -->
        <div class="rules-section">
          <div class="rule-item">
            <div class="rule-icon-bg bg-red-50">
              <span class="iconify text-red-500" data-icon="mdi:lock-outline"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">积分冻结规则</h4>
              <p class="rule-desc">发布悬赏任务时，积分会被<span class="text-red-600 font-bold">冻结</span>，任务完成后转给帮助者。</p>
            </div>
          </div>

          <div class="rule-item">
            <div class="rule-icon-bg bg-green-50">
              <span class="iconify text-green-500" data-icon="mdi:refresh-circle-outline"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">积分退还规则</h4>
              <p class="rule-desc">任务取消后，冻结的积分将<span class="text-green-600 font-bold">退还</span>到您的账户。</p>
            </div>
          </div>

          <div class="rule-item">
            <div class="rule-icon-bg bg-blue-50">
              <span class="iconify text-blue-500" data-icon="mdi:currency-usd"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">服务交易规则</h4>
              <p class="rule-desc">购买服务时，积分会被冻结，服务完成确认后转给卖家。</p>
            </div>
          </div>

          <div class="rule-item">
            <div class="rule-icon-bg bg-purple-50">
              <span class="iconify text-purple-500" data-icon="mdi:bank-outline"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">积分使用范围</h4>
              <p class="rule-desc">积分不可提现，仅限平台内使用，可用于发布悬赏、购买服务等。</p>
            </div>
          </div>

          <div class="rule-item">
            <div class="rule-icon-bg bg-orange-50">
              <span class="iconify text-orange-500" data-icon="mdi:alert-circle-outline"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">违规处理规则</h4>
              <p class="rule-desc">如有违规行为，平台有权扣除相应积分，严重者可能封禁账号。</p>
            </div>
          </div>

          <div class="rule-item">
            <div class="rule-icon-bg bg-yellow-50">
              <span class="iconify text-yellow-500" data-icon="mdi:star-circle-outline"></span>
            </div>
            <div class="rule-text">
              <h4 class="rule-title">积分有效期</h4>
              <p class="rule-desc">积分有效期为一年，每年12月31日清零，请及时使用。</p>
            </div>
          </div>
        </div>

        <!-- 分割线 -->
        <div class="divider"></div>

        <!-- 积分记录列表 -->
        <div class="record-section">
          <h4 class="section-title">最近积分记录</h4>
          <div v-if="list.length === 0 && !loading" class="empty-state">
            <div class="empty-icon">
              <span class="iconify" data-icon="mdi:receipt-text-outline"></span>
            </div>
            <p>暂无记录</p>
          </div>
          
          <div v-for="item in list" :key="item.id" class="record-item">
            <div class="record-info">
              <div class="record-type">
                <div :class="getRecordTypeIconBg(item.type)" class="type-icon">
                  <span class="iconify" :class="getRecordTypeIconColor(item.type)" :data-icon="getRecordTypeIcon(item.type)"></span>
                </div>
                <div>
                  <span class="record-title">{{ item.title }}</span>
                  <span class="record-date">{{ item.date }}</span>
                </div>
              </div>
              <div class="record-amount" :class="item.amount > 0 ? 'text-green-600' : 'text-red-500'">
                {{ item.amount > 0 ? '+' : '' }}{{ item.amount }} 积分
              </div>
            </div>
          </div>

          <div v-if="loading" class="loading-state">
            <span class="loading-icon"></span>
            <p>加载中...</p>
          </div>
          <div v-if="finished" class="finished-state">
            <p>没有更多记录了</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="closeModal" class="confirm-btn">
          <span class="iconify" data-icon="mdi:check-circle-outline"></span>
          我知道了
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)

const closeModal = () => {
  emit('close')
}

// 生成模拟数据（汉化版）
const mockFetchData = (pageNum) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newData = []
      // 生成10条模拟数据
      const recordTypes = [
        { type: 'task_complete', title: '完成任务：数据标注', icon: 'mdi:check-circle-outline' },
        { type: 'publish_need', title: '发布悬赏：Logo设计', icon: 'mdi:tag-outline' },
        { type: 'reward', title: '新用户注册奖励', icon: 'mdi:gift-outline' },
        { type: 'purchase', title: '购买服务：PPT美化', icon: 'mdi:cart-outline' },
        { type: 'service_income', title: '服务收入：编程辅导', icon: 'mdi:briefcase-check-outline' },
        { type: 'refund', title: '悬赏退还：取快递', icon: 'mdi:arrow-u-left-top' }
      ]
      
      const startId = (pageNum - 1) * 10
      for (let i = 0; i < 10; i++) {
        const recordType = recordTypes[Math.floor(Math.random() * recordTypes.length)]
        const isIncome = recordType.type === 'task_complete' || 
                        recordType.type === 'reward' || 
                        recordType.type === 'service_income' ||
                        recordType.type === 'refund'
        
        const now = new Date()
        const randomDate = new Date(now.getTime() - Math.random() * 30 * 24 * 60 * 60 * 1000)
        
        newData.push({
          id: startId + i,
          type: recordType.type,
          title: recordType.title,
          date: randomDate.toLocaleDateString('zh-CN') + ' ' + 
                randomDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
          amount: isIncome ? Math.floor(Math.random() * 100) + 20 : -(Math.floor(Math.random() * 50) + 10)
        })
      }
      resolve(newData)
    }, 800)
  })
}

// 加载数据逻辑
const loadData = async () => {
  if (loading.value || finished.value) return
  
  loading.value = true
  const data = await mockFetchData(page.value)
  
  if (data.length === 0) {
    finished.value = true
  } else {
    list.value.push(...data)
    page.value++
    // 模拟3页数据后停止
    if (page.value > 3) finished.value = true
  }
  loading.value = false
}

// 无限滚动处理
const handleScroll = (e) => {
  const { scrollTop, clientHeight, scrollHeight } = e.target
  // 距离底部50px时加载更多
  if (scrollHeight - scrollTop - clientHeight < 50) {
    loadData()
  }
}

// 获取记录类型图标
const getRecordTypeIcon = (type) => {
  const iconMap = {
    task_complete: 'mdi:check-circle-outline',
    publish_need: 'mdi:tag-outline',
    reward: 'mdi:gift-outline',
    purchase: 'mdi:cart-outline',
    service_income: 'mdi:briefcase-check-outline',
    refund: 'mdi:arrow-u-left-top'
  }
  return iconMap[type] || 'mdi:currency-usd'
}

const getRecordTypeIconBg = (type) => {
  const classMap = {
    task_complete: 'bg-green-100',
    publish_need: 'bg-red-100',
    reward: 'bg-yellow-100',
    purchase: 'bg-red-100',
    service_income: 'bg-green-100',
    refund: 'bg-blue-100'
  }
  return classMap[type] || 'bg-gray-100'
}

const getRecordTypeIconColor = (type) => {
  const classMap = {
    task_complete: 'text-green-600',
    publish_need: 'text-red-500',
    reward: 'text-yellow-500',
    purchase: 'text-red-500',
    service_income: 'text-green-600',
    refund: 'text-blue-500'
  }
  return classMap[type] || 'text-gray-500'
}

// 当弹窗打开时重置并加载数据
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    list.value = []
    page.value = 1
    finished.value = false
    loadData()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalIn 0.3s ease;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon .iconify {
  width: 20px;
  height: 20px;
}

.modal-title h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.close-btn .iconify {
  width: 20px;
  height: 20px;
  color: white;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-height: calc(85vh - 120px);
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 规则部分 */
.rules-section {
  margin-bottom: 24px;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.rule-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.rule-icon-bg {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rule-icon-bg .iconify {
  width: 24px;
  height: 24px;
}

.rule-text {
  flex: 1;
}

.rule-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.rule-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

/* 分割线 */
.divider {
  height: 1px;
  background: #f1f5f9;
  margin: 24px 0;
}

/* 记录部分 */
.record-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #3b82f6;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}

.empty-icon {
  width: 60px;
  height: 60px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-icon .iconify {
  width: 30px;
  height: 30px;
  color: #cbd5e1;
}

.record-item {
  padding: 16px;
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.record-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.record-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-type {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.type-icon .iconify {
  width: 20px;
  height: 20px;
}

.record-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.record-date {
  display: block;
  font-size: 12px;
  color: #94a3b8;
}

.record-amount {
  font-size: 16px;
  font-weight: 700;
}

.loading-state {
  text-align: center;
  padding: 20px;
  color: #64748b;
}

.loading-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #3b82f6;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.finished-state {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 14px;
}

/* 底部按钮 */
.modal-footer {
  padding: 20px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}

.confirm-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.confirm-btn:active {
  transform: translateY(0);
}

.confirm-btn .iconify {
  width: 20px;
  height: 20px;
}
</style>