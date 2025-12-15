<template>
  <div class="home-container">
    <!-- 移动端容器 -->
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>

      <!-- 顶部导航 -->
      <header class="header-bar">
        <span class="app-title">U-Linker</span>
        <div class="header-icons">
          <span class="iconify header-icon" data-icon="mdi:bell-outline"></span>
          <span class="iconify header-icon" data-icon="mdi:magnify"></span>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- Banner -->
        <div class="banner">
          <div class="banner-content">
            <h3 class="banner-title">校园互助新体验</h3>
            <p class="banner-subtitle">查看最新公告 ></p>
          </div>
        </div>

        <!-- 双功能卡片 -->
        <div class="function-cards">
          <!-- 我需要 -->
          <div class="function-card need-card">
            <div class="card-icon">
              <span class="iconify" data-icon="mdi:hand-extended-outline"></span>
            </div>
            <div class="card-text">
              <h3 class="card-title">我需要</h3>
              <p class="card-desc">发布悬赏 / 寻求帮助</p>
            </div>
          </div>

          <!-- 我能提供 -->
          <div class="function-card provide-card">
            <div class="card-icon">
              <span class="iconify" data-icon="mdi:briefcase-outline"></span>
            </div>
            <div class="card-text">
              <h3 class="card-title">我能提供</h3>
              <p class="card-desc">出售技能 / 赚取积分</p>
            </div>
          </div>
        </div>

        <!-- 积分卡片 -->
        <div class="points-card">
          <div class="points-info">
            <div class="points-label">
              <span class="iconify" data-icon="mdi:wallet-outline"></span>
              当前积分余额
            </div>
            <div class="points-value">256</div>
          </div>
          <div class="points-icon">
            <span class="iconify" data-icon="mdi:currency-usd"></span>
          </div>
        </div>

        <!-- 热门互助 -->
        <div class="hot-tasks">
          <div class="section-header">
            <h2 class="section-title">热门互助</h2>
            <span class="more-link">
              更多 <span class="iconify" data-icon="mdi:chevron-right"></span>
            </span>
          </div>

          <div class="tasks-list">
            <!-- 悬赏任务 -->
            <div class="task-item">
              <div class="task-icon reward">
                <span class="iconify" data-icon="mdi:package-variant"></span>
              </div>
              <div class="task-content">
                <div class="task-header">
                  <h3 class="task-title">代取快递到南区宿舍</h3>
                  <span class="task-reward">+15</span>
                </div>
                <p class="task-desc">南区3号楼，今晚8点前</p>
                <div class="task-tags">
                  <span class="task-tag">悬赏</span>
                  <span class="task-time">刚刚发布</span>
                </div>
              </div>
            </div>

            <!-- 服务任务 -->
            <div class="task-item">
              <div class="task-icon service">
                <span class="iconify" data-icon="mdi:school-outline"></span>
              </div>
              <div class="task-content">
                <div class="task-header">
                  <h3 class="task-title">提供高等数学辅导</h3>
                  <span class="task-price">25/时</span>
                </div>
                <p class="task-desc">本人数学系大三，可辅导期末复习</p>
                <div class="task-tags">
                  <span class="task-tag">服务</span>
                  <span class="task-consultants">12人已咨询</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部导航栏 -->
      <footer class="bottom-nav">
        <div class="nav-item active">
          <div class="nav-icon">
            <span class="iconify" data-icon="mdi:compass"></span>
          </div>
          <span class="nav-label">首页</span>
        </div>
        <div class="nav-item">
          <div class="nav-icon">
            <span class="iconify" data-icon="mdi:file-document-outline"></span>
          </div>
          <span class="nav-label">任务</span>
        </div>
        <div class="nav-item">
          <div class="nav-icon">
            <span class="iconify" data-icon="mdi:cart-outline"></span>
          </div>
          <span class="nav-label">订单</span>
        </div>
        <div class="nav-item">
          <div class="nav-icon">
            <span class="iconify" data-icon="mdi:account-outline"></span>
          </div>
          <span class="nav-label">我的</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 示例交互方法
const handleBannerClick = () => {
  console.log('点击Banner')
}

const handleNeedCardClick = () => {
  console.log('点击我需要')
}

const handleProvideCardClick = () => {
  console.log('点击我能提供')
}

const handleTaskClick = (type) => {
  console.log(`点击${type}任务`)
}
</script>

<style scoped>
/* 基础容器 */
.home-container {
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
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 状态栏 */
.status-bar {
  height: 2rem;
  background-color: white;
  width: 100%;
  flex-shrink: 0;
}

/* 顶部导航 */
.header-bar {
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  border-bottom: 1px solid #f9fafb;
  background-color: white;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: -0.025em;
}

.header-icons {
  display: flex;
  gap: 1rem;
}

.header-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #4b5563;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.25rem 1.5rem;
  background-color: white;
}

/* 隐藏滚动条 */
.main-content::-webkit-scrollbar {
  display: none;
}

.main-content {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Banner */
.banner {
  margin-top: 1.25rem;
  height: 10rem;
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
  background: linear-gradient(to right, #3b82f6, #4f46e5);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.banner-content {
  text-align: center;
}

.banner-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.025em;
}

.banner-subtitle {
  font-size: 0.75rem;
  color: #93c5fd;
  margin-top: 0.25rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  backdrop-filter: blur(4px);
  display: inline-block;
}

/* 功能卡片 */
.function-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.5rem;
}

.function-card {
  border-radius: 1rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  cursor: pointer;
  border: 1px solid transparent;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.function-card:active {
  transform: scale(0.95);
}

.need-card {
  background-color: #eff6ff;
  border-color: #dbeafe;
}

.need-card:hover {
  background-color: #dbeafe;
}

.provide-card {
  background-color: #fffbeb;
  border-color: #fef3c7;
}

.provide-card:hover {
  background-color: #fef3c7;
}

.card-icon {
  width: 3.5rem;
  height: 3.5rem;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.need-card .card-icon .iconify {
  width: 2rem;
  height: 2rem;
  color: #2563eb;
}

.provide-card .card-icon .iconify {
  width: 2rem;
  height: 2rem;
  color: #f59e0b;
}

.card-text {
  text-align: center;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
}

.card-desc {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0.25rem;
}

.need-card .card-desc {
  color: #2563eb;
}

.provide-card .card-desc {
  color: #f59e0b;
}

/* 积分卡片 */
.points-card {
  margin-top: 1.5rem;
  background: linear-gradient(to bottom right, #111827, #1f2937);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.points-info {
  flex: 1;
}

.points-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.points-label .iconify {
  width: 1rem;
  height: 1rem;
}

.points-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #fbbf24;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.05em;
}

.points-icon {
  width: 2.5rem;
  height: 2.5rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.points-icon .iconify {
  width: 1.5rem;
  height: 1.5rem;
  color: #fbbf24;
}

/* 热门互助 */
.hot-tasks {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
}

.more-link {
  font-size: 0.75rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.more-link .iconify {
  width: 1rem;
  height: 1rem;
  margin-left: 0.25rem;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  background-color: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  display: flex;
  gap: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.task-item:active {
  background-color: #f9fafb;
}

.task-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-icon.reward {
  background-color: #dbeafe;
}

.task-icon.reward .iconify {
  width: 1.5rem;
  height: 1.5rem;
  color: #2563eb;
}

.task-icon.service {
  background-color: #fed7aa;
}

.task-icon.service .iconify {
  width: 1.5rem;
  height: 1.5rem;
  color: #f97316;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.task-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-reward {
  font-size: 0.75rem;
  font-weight: 700;
  color: #2563eb;
  background-color: #dbeafe;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

.task-price {
  font-size: 0.75rem;
  font-weight: 700;
  color: #f97316;
  background-color: #fed7aa;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

.task-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-tags {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.task-tag {
  background-color: #f3f4f6;
  color: #6b7280;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.task-time,
.task-consultants {
  color: #9ca3af;
}

/* 底部导航栏 */
.bottom-nav {
  background-color: white;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 3.75rem;
  padding-bottom: 0.25rem;
  z-index: 30;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.nav-item.active .nav-icon {
  color: #2563eb;
}

.nav-item.active .nav-label {
  color: #2563eb;
}

.nav-icon {
  color: #9ca3af;
  transition: color 0.2s ease;
}

.nav-item:not(.active):hover .nav-icon {
  color: #2563eb;
}

.nav-item:not(.active):hover .nav-label {
  color: #2563eb;
}

.nav-icon .iconify {
  width: 1.5rem;
  height: 1.5rem;
}

.nav-label {
  font-size: 0.625rem;
  font-weight: 500;
  color: #6b7280;
  margin-top: 0.125rem;
  transition: color 0.2s ease;
}

/* 响应式设计 */
@media (max-width: 400px) {
  .home-container {
    padding: 0.5rem;
  }
  
  .mobile-frame {
    width: 100%;
    height: 100vh;
    border-radius: 0;
  }
}

@media (max-height: 850px) {
  .mobile-frame {
    height: auto;
    min-height: 100vh;
    max-height: 812px;
  }
}
</style>