<template>
  <div class="home-container">
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>
      
      <!-- 顶部导航 -->
      <header class="header-bar">
        <button @click="router.back()" class="back-button">
          <span class="iconify" data-icon="mdi:arrow-left"></span>
        </button>
        <span class="app-title">为您推荐</span>
        <div class="header-icons">
          <button @click="refreshRecommendations" class="refresh-btn">
            <span class="iconify" data-icon="mdi:refresh"></span>
          </button>
        </div>
      </header>

      <!-- 主要内容 -->
      <main class="main-content">
        <!-- 用户偏好提示 -->
        <div v-if="userPreferences && (userPreferences.preferred_type || userPreferences.preferred_price_range)" 
             class="preference-card">
          <div class="preference-header">
            <span class="iconify" data-icon="mdi:account-star"></span>
            <span class="preference-title">您的偏好</span>
          </div>
          <div class="preference-content">
            <div v-if="userPreferences.preferred_type" class="preference-item">
              <span class="preference-label">偏好类型：</span>
              <span class="preference-value">{{ userPreferences.preferred_type === 'bounty' ? '悬赏任务' : '服务任务' }}</span>
            </div>
            <div v-if="userPreferences.preferred_price_range" class="preference-item">
              <span class="preference-label">价格区间：</span>
              <span class="preference-value">{{ userPreferences.preferred_price_range[0] }} - {{ userPreferences.preferred_price_range[1] }} 积分</span>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">正在为您推荐...</p>
        </div>

        <!-- 推荐列表 -->
        <div v-else-if="recommendations.length > 0" class="recommendations-list">
          <div 
            v-for="post in recommendations" 
            :key="post.id"
            class="recommendation-card"
            @click="goToPostDetail(post.id)"
          >
            <!-- 推荐标签 -->
            <div class="recommendation-badge">
              <span class="iconify" data-icon="mdi:star"></span>
              <span>推荐</span>
              <span class="recommendation-score">{{ post.recommendation_score }}分</span>
            </div>

            <!-- 帖子信息 -->
            <div class="post-header">
              <h3 class="post-title">{{ post.title }}</h3>
              <div class="post-price">
                <span class="price-value">{{ post.price }}</span>
                <span class="price-unit">积分</span>
              </div>
            </div>

            <!-- 帖子类型和状态 -->
            <div class="post-meta">
              <span :class="['post-type-badge', post.post_type === 'bounty' ? 'type-bounty' : 'type-service']">
                <span class="iconify" :data-icon="post.post_type === 'bounty' ? 'mdi:currency-usd' : 'mdi:handshake'"></span>
                {{ post.post_type === 'bounty' ? '悬赏' : '服务' }}
              </span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>

            <!-- 推荐理由 -->
            <div v-if="post.recommendation_reasons && post.recommendation_reasons.length > 0" class="recommendation-reasons">
              <div class="reasons-header">
                <span class="iconify" data-icon="mdi:lightbulb-on"></span>
                <span>推荐理由</span>
              </div>
              <div class="reasons-list">
                <span 
                  v-for="(reason, index) in post.recommendation_reasons" 
                  :key="index"
                  class="reason-tag"
                >
                  {{ reason }}
                </span>
              </div>
            </div>

            <!-- 作者信息 -->
            <div class="post-author">
              <div class="author-avatar">
                <img v-if="post.author?.avatar" :src="post.author.avatar" />
                <span v-else class="iconify" data-icon="mdi:account"></span>
              </div>
              <div class="author-info">
                <span class="author-name">{{ post.author?.name || post.author?.username || '未知用户' }}</span>
                <span v-if="post.author?.college" class="author-college">{{ post.author.college }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <span class="iconify" data-icon="mdi:star-off"></span>
          </div>
          <p class="empty-text">暂无推荐</p>
          <p class="empty-hint">多浏览一些帖子，我们会为您推荐更合适的内容</p>
          <button @click="router.push('/market')" class="empty-btn">
            去市场看看
          </button>
        </div>
      </main>

      <BottomNav active-tab="home" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecommendations, recordView } from '@/api/recommendation'
import BottomNav from '@/components/common/BottomNav.vue'

const router = useRouter()

const loading = ref(false)
const recommendations = ref([])
const userPreferences = ref(null)

// 获取推荐
const loadRecommendations = async () => {
  loading.value = true
  try {
    const res = await getRecommendations({ limit: 20 })
    if (res.status === 'success') {
      recommendations.value = res.data.recommendations || []
      userPreferences.value = res.data.user_preferences || null
    }
  } catch (error) {
    console.error('获取推荐失败', error)
  } finally {
    loading.value = false
  }
}

// 刷新推荐
const refreshRecommendations = () => {
  loadRecommendations()
}

// 跳转到帖子详情
const goToPostDetail = async (postId) => {
  // 记录浏览
  try {
    await recordView({ post_id: postId })
  } catch (error) {
    console.error('记录浏览失败', error)
  }
  
  // 跳转到详情页
  router.push(`/post/${postId}`)
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return timeStr.split(' ')[0]
  }
}

onMounted(() => {
  loadRecommendations()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.mobile-frame {
  width: 375px;
  height: 812px;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.status-bar {
  height: 2rem;
  background-color: white;
  width: 100%;
  flex-shrink: 0;
}

.header-bar {
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

.back-button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
}

.app-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.header-icons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* 偏好卡片 */
.preference-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #bae6fd;
}

.preference-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #0369a1;
  margin-bottom: 0.75rem;
}

.preference-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preference-item {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
}

.preference-label {
  color: #64748b;
  margin-right: 0.5rem;
}

.preference-value {
  color: #1e293b;
  font-weight: 500;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

/* 推荐列表 */
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.recommendation-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border-color: #3b82f6;
}

/* 推荐标签 */
.recommendation-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  box-shadow: 0 2px 4px rgba(251, 191, 36, 0.3);
}

.recommendation-score {
  background: rgba(255, 255, 255, 0.3);
  padding: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.625rem;
}

/* 帖子头部 */
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.post-title {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
  margin: 0;
}

.post-price {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  flex-shrink: 0;
}

.price-value {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.price-unit {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 帖子元信息 */
.post-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.post-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-bounty {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid #fbbf24;
}

.type-service {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border: 1px solid #60a5fa;
}

.post-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

/* 推荐理由 */
.recommendation-reasons {
  background: #f9fafb;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid #3b82f6;
}

.reasons-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #3b82f6;
  margin-bottom: 0.5rem;
}

.reasons-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reason-tag {
  display: inline-block;
  background: white;
  color: #475569;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  border: 1px solid #e2e8f0;
}

/* 作者信息 */
.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.author-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-avatar .iconify {
  font-size: 1.25rem;
  color: #9ca3af;
}

.author-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.author-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.author-college {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.empty-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

/* 响应式 */
@media (min-width: 768px) {
  .home-container {
    padding: 0;
    align-items: stretch;
  }
  .mobile-frame {
    width: 100%;
    height: 100vh;
    max-width: 100%;
    border-radius: 0;
    box-shadow: none;
  }
  .status-bar {
    display: none;
  }
}
</style>

