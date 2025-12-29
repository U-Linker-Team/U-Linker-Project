<template>
  <div v-if="user" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">用户详情</h3>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>

      <div class="modal-body">
        <!-- 用户基本信息 -->
        <div class="info-section">
          <div class="info-item">
            <label>用户名</label>
            <div>{{ user.username }}</div>
          </div>
          <div class="info-item">
            <label>姓名</label>
            <div>{{ user.name || '未设置' }}</div>
          </div>
          <div class="info-item">
            <label>学院</label>
            <div>{{ user.college || '未设置' }}</div>
          </div>
          <div class="info-item">
            <label>当前积分</label>
            <div class="points-value">{{ user.points }}</div>
          </div>
          <div class="info-item">
            <label>封禁状态</label>
            <div v-if="user.is_banned" class="text-red-600">
              已封禁至 {{ user.ban_until }}
            </div>
            <div v-else class="text-green-600">正常</div>
          </div>
          <div class="info-item" v-if="user.ban_count > 0">
            <label>封禁次数</label>
            <div>{{ user.ban_count }} 次</div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions-section">
          <!-- 积分管理 -->
          <div class="action-group">
            <label>调整积分</label>
            <div class="action-input-group">
              <input 
                v-model.number="pointsChange" 
                type="number" 
                placeholder="输入积分变化量（正数增加，负数减少）"
                class="action-input"
              />
              <input 
                v-model="pointsReason" 
                type="text" 
                placeholder="调整原因"
                class="action-input"
              />
              <button @click="handlePointsChange" class="btn-action">调整</button>
            </div>
          </div>

          <!-- 封禁操作 -->
          <div class="action-group" v-if="!user.is_admin">
            <label>封禁操作</label>
            <div class="action-input-group">
              <input 
                v-model="banReason" 
                type="text" 
                placeholder="封禁原因（如：恶意逃单）"
                class="action-input"
              />
              <button 
                @click="handleBan" 
                class="btn-action btn-danger"
                :disabled="user.is_banned"
              >
                {{ user.is_banned ? '已封禁' : '封禁用户' }}
              </button>
              <button 
                v-if="user.is_banned"
                @click="handleUnban" 
                class="btn-action btn-success"
              >
                解封
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { manageUserPoints, banUser, unbanUser } from '@/api/admin'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

const pointsChange = ref(null)
const pointsReason = ref('管理员调整')
const banReason = ref('恶意行为')

// 调整积分
const handlePointsChange = async () => {
  if (pointsChange.value === null || pointsChange.value === 0) {
    alert('请输入有效的积分变化量')
    return
  }

  try {
    const res = await manageUserPoints(props.user.id, {
      points_change: pointsChange.value,
      reason: pointsReason.value || '管理员调整'
    })
    
    if (res.status === 'success') {
      alert(`积分调整成功：${res.data.old_points} → ${res.data.new_points}`)
      pointsChange.value = null
      pointsReason.value = '管理员调整'
      emit('updated')
    }
  } catch (e) {
    console.error('调整积分失败', e)
  }
}

// 封禁用户
const handleBan = async () => {
  if (!banReason.value.trim()) {
    alert('请输入封禁原因')
    return
  }

  if (!confirm(`确定要封禁用户 "${props.user.name || props.user.username}" 吗？\n原因：${banReason.value}`)) {
    return
  }

  try {
    const res = await banUser(props.user.id, {
      reason: banReason.value,
      ban_days: 3  // 默认3天，会根据封禁次数自动计算
    })
    
    if (res.status === 'success') {
      // 处理返回数据，兼容 data 为 null 的情况
      if (res.data && res.data.ban_duration_days) {
        const banInfo = res.data
        alert(`用户已被封禁 ${banInfo.ban_duration_days} 天\n封禁至：${banInfo.ban_until || '未知'}\n封禁次数：${banInfo.ban_count || 1}`)
      } else {
        // 如果 data 为空，从 message 中提取信息
        alert(res.message || '封禁成功')
      }
      banReason.value = '恶意行为'
      // 触发更新，刷新用户列表
      emit('updated')
      // 关闭弹窗
      emit('close')
    } else {
      alert(res.message || '封禁失败')
    }
  } catch (e) {
    console.error('封禁失败', e)
    alert('封禁失败：' + (e.response?.data?.message || e.message || '未知错误'))
  }
}

// 解封用户
const handleUnban = async () => {
  if (!confirm(`确定要解封用户 "${props.user.name || props.user.username}" 吗？`)) {
    return
  }

  try {
    const res = await unbanUser(props.user.id)
    
    if (res.status === 'success') {
      alert(res.message || '用户已解封')
      // 触发更新，刷新用户列表
      emit('updated')
      // 关闭弹窗
      emit('close')
    } else {
      alert(res.message || '解封失败')
    }
  } catch (e) {
    console.error('解封失败', e)
    alert('解封失败：' + (e.response?.data?.message || e.message || '未知错误'))
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 1rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
}

.info-section {
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item div {
  color: #1f2937;
  font-weight: 500;
}

.points-value {
  color: #3b82f6;
  font-size: 1.25rem;
  font-weight: 700;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.action-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-group label {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.action-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-input {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
}

.btn-action {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: #3b82f6;
  color: white;
}

.btn-action:hover:not(:disabled) {
  background: #2563eb;
}

.btn-action:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-danger {
  background: #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-success {
  background: #10b981;
}

.btn-success:hover {
  background: #059669;
}
</style>

