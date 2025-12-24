<!-- 我的（个人中心） -->

<template>
  <div class="profile-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      <!-- 蓝色背景区域 -->
      <div class="blue-background">
        <!-- 顶部导航 -->
        <header class="header-bar">
          <span class="app-title">个人中心</span>
          <div class="header-icons">
            <span class="iconify header-icon" data-icon="mdi:cog-outline" @click="goToSettings"></span>
          </div>
        </header>
        
        <!-- 用户信息卡片 - 放在蓝色背景上方 -->
        <div class="user-card-wrapper">
          <div class="user-card">
            <div class="user-avatar">
              <!-- 使用 Pinia 里的头像，如果没头像就显示默认图 -->
              <img 
                :src="userInfo.avatar || 'https://via.placeholder.com/100'" 
                alt="用户头像"
                class="avatar-image"
                @error="(e) => e.target.src = 'https://via.placeholder.com/100'"
              >
            </div>
            <div class="user-info">
              <div class="user-name-section">
                <!-- 替换为真实数据 -->
                <h2 class="user-name">{{ userInfo.name || userInfo.username }}</h2>
                <div class="user-tag">
                  <span class="iconify" data-icon="mdi:school-outline"></span>
                  <!-- 替换为真实数据 -->
                  {{ userInfo.college || '未设置学院' }}
                </div>
              </div>
              <button class="edit-button" @click="editProfile">
                <span class="iconify" data-icon="mdi:pencil-outline"></span>
                编辑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 积分卡片 -->
        <div class="points-card">
          <div class="points-info">
            <div class="points-label">当前积分余额</div>
            <!-- 替换为真实数据 -->
            <div class="points-value">{{ userInfo.points || 0 }}</div>
          </div>
          <div class="points-detail" @click="goToPointsDetail">
            积分明细 <span class="iconify" data-icon="mdi:chevron-right"></span>
          </div>
          <!-- 积分图标 -->
          <div class="points-icon">
            <svg class="dollar-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.10 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c0 1.82-1.34 2.98-3.13 3.29z"/>
            </svg>
          </div>
        </div>

        <!-- 功能菜单 -->
        <div class="menu-section">
          <!-- 我的发布 -->
          <div class="menu-item" @click="goToMyPosts">
            <div class="menu-icon" style="background-color: #E6F7FF;">
              <span class="iconify" data-icon="mdi:file-document-edit-outline" style="color: #1890FF;"></span>
            </div>
            <span class="menu-text">我的发布</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right" style="color: #DCDFE6;"></span>
          </div>

          <!-- 我的接受 -->
          <div class="menu-item" @click="goToMyAccepted">
            <div class="menu-icon" style="background-color: #FFF7E6;">
              <span class="iconify" data-icon="mdi:handshake-outline" style="color: #E6A23C;"></span>
            </div>
            <span class="menu-text">我的接受</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right" style="color: #DCDFE6;"></span>
          </div>

          <!-- 聊天记录 -->
          <div class="menu-item" @click="goToChatHistory">
            <div class="menu-icon" style="background-color: #F6FFED;">
              <span class="iconify" data-icon="mdi:message-text-outline" style="color: #52C41A;"></span>
            </div>
            <div class="menu-text-badge">
              <span class="menu-text">聊天记录</span>
              <!-- 暂时写死或者接未读消息数 -->
              <span class="badge">0</span>
            </div>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right" style="color: #DCDFE6;"></span>
          </div>

          <!-- 我的收藏 -->
          <div class="menu-item" @click="goToMyFavorites">
            <div class="menu-icon" style="background-color: #F9F0FF;">
              <span class="iconify" data-icon="mdi:star-outline" style="color: #722ED1;"></span>
            </div>
            <span class="menu-text">我的收藏</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right" style="color: #DCDFE6;"></span>
          </div>
        </div>

        <!-- 退出登录按钮 -->
        <div class="logout-section">
          <button class="logout-button" @click="handleLogout">
            退出登录
          </button>
        </div>
      </main>

      <!-- 退出登录确认弹窗 -->
      <div v-if="showLogoutModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-icon">
            <span class="iconify logout-icon" data-icon="mdi:logout-variant"></span>
          </div>
          
          <h2 class="modal-title">确定要退出登录吗？</h2>
          
          <p class="modal-description">
            退出后您将无法收到即时消息通知，<br>下次使用需要重新登录。
          </p>
          
          <div class="modal-buttons">
            <button class="modal-btn cancel-btn" @click="cancelLogout">取消</button>
            <button class="modal-btn confirm-btn" @click="confirmLogout">确认退出</button>
          </div>
        </div>
      </div>

      <!-- 复用公共 BottomNav 组件 -->
      <BottomNav active-tab="profile" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue' 
import { useUserStore } from '@/stores/user' 
// 引入 API
import { getUserProfile, logout } from '@/api/auth'
// 引入组件
import BottomNav from '@/components/common/BottomNav.vue'

const router = useRouter()
const userStore = useUserStore()

// 1. 直接从 Pinia 取用户信息 (这是响应式的，一旦 Store 变了，页面跟着变)
const userInfo = computed(() => userStore.userInfo || {})

const showLogoutModal = ref(false)

// 2. 页面加载时，去后端刷新一次最新数据 (比如最新积分)
onMounted(async () => {
  // 如果 Store 里有 ID，就用 ID 去查最新资料
  if (userInfo.value.id) {
    try {
      const res = await getUserProfile(userInfo.value.id)
      // 更新 Store，这样页面上的积分、头像就会自动变成最新的
      userStore.login(res.data) 
    } catch (e) {
      console.error('刷新用户信息失败', e)
    }
  }
})

// --- 各种跳转逻辑 ---
const goToSettings = () => console.log('跳转到设置页面')
const editProfile = () => router.push('/edit-profile')
const goToPointsDetail = () => router.push('/points-detail')
const goToMyPosts = () => router.push('/order?type=published')
const goToMyAccepted = () => router.push('/order?type=accepted')
const goToChatHistory = () => router.push('/chat') // 指向聊天列表
const goToMyFavorites = () => router.push('/collect')

// --- 退出登录逻辑 ---
const handleLogout = () => showLogoutModal.value = true
const cancelLogout = () => showLogoutModal.value = false
const closeModal = (e) => {
  if (e.target.classList.contains('modal-overlay')) showLogoutModal.value = false
}

const confirmLogout = async () => {
  try {
    // 1. 告诉后端我要退出了
    await logout()
  } catch (e) {
    // 即使后端报错，前端也要强制登出
  } finally {
    // 2. 清除前端状态
    userStore.logout() // 这个方法在 stores/user.js 里定义过
    showLogoutModal.value = false
    router.push('/login')
  }
}
</script>

<style scoped>
/* 基础容器 */
.profile-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

/* 移动端框架 */
.mobile-frame {
  width: 375px;
  height: 812px;
  background-color: #F7F8FA;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 蓝色背景区域 */
.blue-background {
  height: 14rem;
  background: linear-gradient(135deg, #1890FF 0%, #36CFC9 100%);
  position: relative;
  flex-shrink: 0;
}

/* 顶部导航 */
.header-bar {
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  color: white;
}

.app-title { font-size: 1.125rem; font-weight: 600; }
.header-icon { font-size: 1.5rem; cursor: pointer; }

/* 用户信息卡片 */
.user-card-wrapper {
  position: absolute;
  bottom: -2rem;
  left: 0;
  width: 100%;
  padding: 0 1rem;
  z-index: 10;
}

.user-card {
  background-color: white;
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-name-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name { font-size: 1.125rem; font-weight: 700; color: #333; margin: 0; }
.user-tag {
  display: flex; align-items: center; gap: 0.25rem;
  font-size: 0.75rem; color: #999;
  background-color: #F5F5F5; padding: 0.125rem 0.5rem; border-radius: 1rem;
  width: fit-content;
}

.edit-button {
  display: flex; align-items: center; gap: 0.25rem;
  background: none; border: 1px solid #E8E8E8;
  padding: 0.25rem 0.75rem; border-radius: 1rem;
  font-size: 0.75rem; color: #666; cursor: pointer;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 3rem 1rem 1rem;
  overflow-y: auto;
}

/* 积分卡片 */
.points-card {
  background: linear-gradient(135deg, #333333 0%, #000000 100%);
  border-radius: 1rem;
  padding: 1.25rem;
  color: #FFD700;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.points-label { font-size: 0.75rem; opacity: 0.8; margin-bottom: 0.25rem; }
.points-value { font-size: 1.75rem; font-weight: 700; font-family: monospace; }
.points-detail {
  font-size: 0.75rem; display: flex; align-items: center;
  background: rgba(255, 215, 0, 0.2); padding: 0.25rem 0.5rem; border-radius: 1rem; cursor: pointer;
}
.points-icon {
  position: absolute; right: -0.5rem; bottom: -1rem;
  opacity: 0.1; transform: rotate(-15deg);
}
.dollar-icon { width: 5rem; height: 5rem; }

/* 菜单区域 */
.menu-section {
  background-color: white; border-radius: 1rem;
  padding: 0.5rem 0; margin-bottom: 1rem;
}
.menu-item {
  display: flex; align-items: center; padding: 1rem;
  cursor: pointer; transition: background-color 0.2s;
}
.menu-item:active { background-color: #F9F9F9; }
.menu-icon {
  width: 2rem; height: 2rem; border-radius: 0.5rem;
  display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;
}
.menu-text { flex: 1; font-size: 0.9375rem; color: #333; }
.menu-text-badge { flex: 1; display: flex; align-items: center; justify-content: space-between; padding-right: 0.5rem; }
.badge {
  background-color: #FF4D4F; color: white;
  font-size: 0.75rem; padding: 0 0.4rem; border-radius: 1rem;
}

/* 退出登录 */
.logout-section { padding: 0 1rem; margin-bottom: 1rem; }
.logout-button {
  width: 100%; padding: 0.875rem;
  background-color: white; color: #FF4D4F;
  border: none; border-radius: 0.75rem;
  font-size: 0.9375rem; cursor: pointer;
}

/* 弹窗样式 */
.modal-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.5); z-index: 50;
  display: flex; align-items: center; justify-content: center;
}
.modal-content {
  background-color: white; width: 80%; border-radius: 1rem; padding: 1.5rem; text-align: center;
}
.modal-icon {
  width: 3.5rem; height: 3.5rem; background-color: #FFF1F0;
  border-radius: 50%; color: #FF4D4F; margin: 0 auto 1rem;
  display: flex; align-items: center; justify-content: center;
}
.logout-icon { font-size: 1.75rem; }
.modal-title { font-size: 1.125rem; font-weight: 700; color: #333; margin-bottom: 0.5rem; }
.modal-description { font-size: 0.875rem; color: #999; margin-bottom: 1.5rem; line-height: 1.5; }
.modal-buttons { display: flex; gap: 0.75rem; }
.modal-btn { flex: 1; padding: 0.75rem; border-radius: 2rem; font-size: 0.9375rem; cursor: pointer; border: none; }
.cancel-btn { background-color: #F5F5F5; color: #666; }
.confirm-btn { background-color: #FF4D4F; color: white; }

/* 响应式适配 */
@media (max-width: 400px) {
  .profile-container { padding: 0; }
  .mobile-frame { width: 100%; height: 100vh; border-radius: 0; }
}
</style>