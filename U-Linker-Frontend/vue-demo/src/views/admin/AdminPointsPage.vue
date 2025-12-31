<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="header-back" @click="router.push('/admin')">
        <span class="iconify" data-icon="mdi:arrow-left"></span>
      </div>
      <span class="page-title">积分流动</span>
      <div style="width: 2rem;"></div>
    </header>

    <main class="page-content">
      <div class="table-container">
        <div v-if="pointsLoading" class="loading">加载中...</div>
        <div v-else-if="pointsList.length === 0" class="empty">暂无记录</div>
        <div v-else class="points-list">
          <div 
            v-for="record in pointsList" 
            :key="record.id"
            class="points-item"
          >
            <div class="points-user">{{ record.user_info?.name || '未知用户' }}</div>
            <div class="points-action">{{ record.action }}</div>
            <div :class="['points-change', record.points_change > 0 ? 'text-green-600' : 'text-red-600']">
              {{ record.points_change > 0 ? '+' : '' }}{{ record.points_change }}
            </div>
            <div class="points-time">{{ record.created_at }}</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getAllPointsHistory } from '@/api/admin'

const router = useRouter()
const userStore = useUserStore()

// 检查管理员权限
if (!userStore.userInfo || !userStore.userInfo.is_admin) {
  alert('权限不足：需要管理员权限')
  router.push('/home')
}

const pointsList = ref([])
const pointsLoading = ref(false)

const fetchPointsHistory = async () => {
  pointsLoading.value = true
  try {
    const res = await getAllPointsHistory({
      page: 1,
      page_size: 100
    })
    if (res.status === 'success') {
      pointsList.value = res.data.items
    }
  } catch (e) {
    console.error('获取积分流动记录失败', e)
  } finally {
    pointsLoading.value = false
  }
}

onMounted(() => {
  fetchPointsHistory()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.page-header {
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-back {
  cursor: pointer;
  padding: 0.5rem;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.points-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.points-item {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr 1fr;
  gap: 0.5rem;
  align-items: center;
}

.points-user {
  font-weight: 500;
}

.points-action {
  font-size: 0.875rem;
  color: #6b7280;
}

.points-change {
  font-weight: 600;
  text-align: right;
}

.points-time {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: right;
}

.text-green-600 {
  color: #16a34a;
}

.text-red-600 {
  color: #dc2626;
}
</style>

