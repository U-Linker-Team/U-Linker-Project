<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="header-back" @click="router.push('/admin')">
        <span class="iconify" data-icon="mdi:arrow-left"></span>
      </div>
      <span class="page-title">用户管理</span>
      <div style="width: 2rem;"></div>
    </header>

    <main class="page-content">
      <!-- 统一搜索框（支持切换模式） -->
      <div class="search-bar">
        <div class="search-mode-tabs">
          <button 
            @click="searchMode = 'list'"
            :class="['mode-tab', { active: searchMode === 'list' }]"
          >
            <span class="iconify" data-icon="mdi:account-search"></span>
            用户列表
          </button>
          <button 
            @click="searchMode = 'studentId'"
            :class="['mode-tab', { active: searchMode === 'studentId' }]"
          >
            <span class="iconify" data-icon="mdi:card-account-details"></span>
            学号查询
          </button>
        </div>
        
        <div class="search-input-wrapper">
          <input 
            v-if="searchMode === 'studentId'"
            v-model="studentIdSearch"
            @keyup.enter="searchByStudentId"
            type="text" 
            placeholder="输入学号查询用户所有帖子（如：222222222）"
            class="search-input"
          />
          <input 
            v-else
            v-model="userSearchKeyword"
            @input="searchUsers"
            type="text" 
            placeholder="搜索用户列表（用户名、姓名、学号、学院）"
            class="search-input"
          />
          <button 
            v-if="searchMode === 'studentId'"
            @click="searchByStudentId" 
            class="search-btn-inline"
          >
            <span class="iconify" data-icon="mdi:magnify"></span>
          </button>
        </div>
      </div>
      
      <!-- 学号查询结果 -->
      <div v-if="studentIdResult" class="student-id-result">
        <div class="result-header">
          <h4>学号 {{ studentIdSearch }} 的用户信息</h4>
          <button @click="studentIdResult = null" class="close-result-btn">×</button>
        </div>
        
        <div class="result-user-info">
          <div class="info-row">
            <span class="info-label">用户名：</span>
            <span>{{ studentIdResult.user_info?.username }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">姓名：</span>
            <span>{{ studentIdResult.user_info?.name || '未设置' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">学院：</span>
            <span>{{ studentIdResult.user_info?.college || '未设置' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">积分：</span>
            <span class="points-highlight">{{ studentIdResult.user_info?.points || 0 }}</span>
          </div>
        </div>
        
        <!-- 帖子列表 -->
        <div class="result-posts">
          <div class="posts-tabs">
            <button 
              @click="postsTab = 'i_need'" 
              :class="['tab-btn', { active: postsTab === 'i_need' }]"
            >
              我需要 ({{ studentIdResult.posts?.i_need?.length || 0 }})
            </button>
            <button 
              @click="postsTab = 'i_provide'" 
              :class="['tab-btn', { active: postsTab === 'i_provide' }]"
            >
              我能提供 ({{ studentIdResult.posts?.i_provide?.length || 0 }})
            </button>
          </div>
          
          <div class="posts-list">
            <div v-if="postsTab === 'i_need'">
              <div v-if="!studentIdResult.posts?.i_need || studentIdResult.posts.i_need.length === 0" class="empty-posts">
                暂无"我需要"帖子
              </div>
              <div v-else v-for="post in studentIdResult.posts.i_need" :key="post.id" class="post-item-result post-item-i-need">
                <div class="post-header-result">
                  <div class="post-title-result">{{ post.title }}</div>
                  <div class="post-price-badge">{{ post.price }} 积分</div>
                </div>
                <div class="post-badges-result">
                  <span :class="['badge-type', post.post_type === 'bounty' ? 'badge-bounty' : 'badge-service']">
                    <span class="iconify" :data-icon="post.post_type === 'bounty' ? 'mdi:currency-usd' : 'mdi:handshake'"></span>
                    {{ post.post_type === 'bounty' ? '悬赏' : '服务' }}
                  </span>
                  <span :class="['badge-status', getStatusClass(post.status)]">
                    {{ getStatusText(post.status) }}
                  </span>
                </div>
                <div class="post-content-result">{{ post.content }}</div>
              </div>
            </div>
            
            <div v-if="postsTab === 'i_provide'">
              <div v-if="!studentIdResult.posts?.i_provide || studentIdResult.posts.i_provide.length === 0" class="empty-posts">
                暂无"我能提供"帖子
              </div>
              <div v-else v-for="post in studentIdResult.posts.i_provide" :key="post.id" class="post-item-result post-item-i-provide">
                <div class="post-header-result">
                  <div class="post-title-result">{{ post.title }}</div>
                  <div class="post-price-badge">{{ post.price }} 积分</div>
                </div>
                <div class="post-badges-result">
                  <span :class="['badge-type', post.post_type === 'bounty' ? 'badge-bounty' : 'badge-service']">
                    <span class="iconify" :data-icon="post.post_type === 'bounty' ? 'mdi:currency-usd' : 'mdi:handshake'"></span>
                    {{ post.post_type === 'bounty' ? '悬赏' : '服务' }}
                  </span>
                  <span :class="['badge-status', getStatusClass(post.status)]">
                    {{ getStatusText(post.status) }}
                  </span>
                </div>
                <div class="post-content-result">{{ post.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 用户列表（仅在列表模式下显示） -->
      <div v-if="searchMode === 'list' || !studentIdResult" class="table-container">
        <div v-if="usersLoading" class="loading">加载中...</div>
        <div v-else-if="usersList.length === 0" class="empty">暂无用户</div>
        <div v-else class="user-list">
          <div 
            v-for="user in usersList" 
            :key="user.id"
            class="user-item"
            @click="openUserDetail(user)"
          >
            <div class="user-avatar">
              <img v-if="user.avatar" :src="getImageUrl(user.avatar)" />
              <span v-else>{{ user.name?.charAt(0) || 'U' }}</span>
            </div>
            <div class="user-info">
              <div class="user-name">
                {{ user.name || user.username }}
                <span v-if="user.is_admin" class="badge-admin">管理员</span>
                <span v-if="user.is_banned" class="badge-banned">已封禁</span>
              </div>
              <div class="user-meta">
                {{ user.college || '未知学院' }} · {{ user.points }} 积分
              </div>
            </div>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
        </div>
      </div>
    </main>

    <!-- 用户详情弹窗 -->
    <UserDetailModal 
      v-if="selectedUser"
      :user="selectedUser"
      @close="selectedUser = null"
      @updated="refreshUsers"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getAllUsers, getUserByStudentId } from '@/api/admin'
import { getImageUrl } from '@/utils/imageHelper'
import UserDetailModal from '@/components/admin/UserDetailModal.vue'

const router = useRouter()
const userStore = useUserStore()

// 检查管理员权限
if (!userStore.userInfo || !userStore.userInfo.is_admin) {
  alert('权限不足：需要管理员权限')
  router.push('/home')
}

// 状态管理
const usersList = ref([])
const usersLoading = ref(false)
const userSearchKeyword = ref('')
const selectedUser = ref(null)
const studentIdSearch = ref('')
const studentIdResult = ref(null)
const postsTab = ref('i_need')
const studentIdLoading = ref(false)
const searchMode = ref('list')

// 获取用户列表
const searchUsers = async () => {
  usersLoading.value = true
  try {
    const res = await getAllUsers({
      keyword: userSearchKeyword.value,
      page: 1,
      page_size: 50
    })
    if (res.status === 'success') {
      usersList.value = res.data.items
    }
  } catch (e) {
    console.error('获取用户列表失败', e)
  } finally {
    usersLoading.value = false
  }
}

// 打开用户详情
const openUserDetail = (user) => {
  selectedUser.value = user
}

// 刷新用户列表
const refreshUsers = () => {
  searchUsers()
}

// 根据学号查询用户帖子
const searchByStudentId = async () => {
  if (!studentIdSearch.value.trim()) {
    alert('请输入学号')
    return
  }
  
  studentIdLoading.value = true
  try {
    const res = await getUserByStudentId(studentIdSearch.value.trim())
    if (res.status === 'success') {
      studentIdResult.value = res.data
      postsTab.value = 'i_need'
    } else {
      alert(res.message || '查询失败')
      studentIdResult.value = null
    }
  } catch (e) {
    console.error('查询失败', e)
    alert('查询失败：' + (e.response?.data?.message || e.message || '未知错误'))
    studentIdResult.value = null
  } finally {
    studentIdLoading.value = false
  }
}

// 切换搜索模式时，清空结果
watch(searchMode, (newMode) => {
  if (newMode === 'list') {
    studentIdResult.value = null
    studentIdSearch.value = ''
  } else {
    userSearchKeyword.value = ''
  }
})

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'active': '招募中',
    'trading': '进行中',
    'sold': '已完成',
    'deleted': '已下架'
  }
  return statusMap[status] || '未知'
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classMap = {
    'active': 'status-recruiting',
    'trading': 'status-trading',
    'sold': 'status-completed',
    'deleted': 'status-deleted'
  }
  return classMap[status] || 'status-unknown'
}

onMounted(() => {
  searchUsers()
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

.search-bar {
  margin-bottom: 1rem;
}

.search-mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 0.5rem;
}

.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-tab.active {
  background: white;
  color: #3b82f6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  gap: 0.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
}

.search-btn-inline {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
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

.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.user-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.badge-admin {
  background: #3b82f6;
  color: white;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.badge-banned {
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.student-id-result {
  background: #f9fafb;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.close-result-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.result-user-info {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-label {
  font-weight: 600;
  color: #6b7280;
  min-width: 4rem;
}

.points-highlight {
  color: #3b82f6;
  font-weight: 700;
}

.result-posts {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
}

.posts-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.tab-btn {
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #6b7280;
  cursor: pointer;
  margin-bottom: -2px;
}

.tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.posts-list {
  max-height: 400px;
  overflow-y: auto;
}

.post-item-result {
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
  border-left: 4px solid;
}

.post-item-i-need {
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-left-color: #f97316;
}

.post-item-i-provide {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-left-color: #3b82f6;
}

.post-header-result {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.post-title-result {
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.post-price-badge {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.post-badges-result {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.badge-type, .badge-status {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-bounty {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.badge-service {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.status-recruiting {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
}

.status-trading {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.status-completed {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #3730a3;
}

.status-deleted {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #4b5563;
}

.post-content-result {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.6;
}

.empty-posts {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}
</style>

