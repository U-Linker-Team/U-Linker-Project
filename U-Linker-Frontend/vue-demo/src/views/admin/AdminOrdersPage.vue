<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="header-back" @click="router.push('/admin')">
        <span class="iconify" data-icon="mdi:arrow-left"></span>
      </div>
      <span class="page-title">订单管理</span>
      <div style="width: 2rem;"></div>
    </header>

    <main class="page-content">
      <div class="table-container">
        <div v-if="ordersLoading" class="loading">加载中...</div>
        <div v-else-if="ordersList.length === 0" class="empty">暂无订单</div>
        <div v-else class="order-list">
          <div 
            v-for="order in ordersList" 
            :key="order.id"
            class="order-item"
          >
            <div class="order-title">{{ order.post_title }}</div>
            <div class="order-meta">
              买家：{{ order.buyer_info?.name || '未知' }} · 
              卖家：{{ order.seller_info?.name || '未知' }} · 
              {{ order.status === 'pending' ? '待处理' : order.status === 'trading' ? '进行中' : '已完成' }}
            </div>
            <div class="order-price">{{ order.price }} 积分</div>
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
import { getAllOrders } from '@/api/admin'

const router = useRouter()
const userStore = useUserStore()

if (!userStore.userInfo || !userStore.userInfo.is_admin) {
  alert('权限不足：需要管理员权限')
  router.push('/home')
}

const ordersList = ref([])
const ordersLoading = ref(false)

const fetchOrders = async () => {
  ordersLoading.value = true
  try {
    const res = await getAllOrders({
      page: 1,
      page_size: 100
    })
    if (res.status === 'success') {
      ordersList.value = res.data.items
    }
  } catch (e) {
    console.error('获取订单列表失败', e)
  } finally {
    ordersLoading.value = false
  }
}

onMounted(() => {
  fetchOrders()
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

.order-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.order-item {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.order-title {
  font-weight: 600;
  color: #1f2937;
}

.order-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.order-price {
  font-weight: 600;
  color: #3b82f6;
}
</style>

