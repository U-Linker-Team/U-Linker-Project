<template>
  <!-- 列表骨架屏 (聊天列表、订单列表等) -->
  <div v-if="variant === 'list'" class="skeleton-list">
    <div 
      v-for="i in count" 
      :key="i" 
      class="skeleton-list-item"
    >
      <!-- 头像占位 -->
      <div class="skeleton-avatar"></div>
      <!-- 文本区域 -->
      <div class="skeleton-content">
        <div class="skeleton-line skeleton-title"></div>
        <div class="skeleton-line skeleton-text"></div>
      </div>
    </div>
  </div>

  <!-- 卡片骨架屏 (市场帖子、首页内容等) -->
  <div v-else-if="variant === 'card'" class="skeleton-card-container">
    <div 
      v-for="i in count" 
      :key="i" 
      class="skeleton-card"
    >
      <!-- 图片占位 -->
      <div class="skeleton-image"></div>
      <!-- 内容区域 -->
      <div class="skeleton-card-body">
        <div class="skeleton-line skeleton-card-title"></div>
        <div class="skeleton-line skeleton-card-desc"></div>
        <div class="skeleton-card-footer">
          <div class="skeleton-avatar-small"></div>
          <div class="skeleton-line skeleton-name"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- 详情页骨架屏 -->
  <div v-else-if="variant === 'detail'" class="skeleton-detail">
    <!-- 头部信息 -->
    <div class="skeleton-detail-header">
      <div class="skeleton-avatar-large"></div>
      <div class="skeleton-detail-info">
        <div class="skeleton-line skeleton-detail-name"></div>
        <div class="skeleton-line skeleton-detail-sub"></div>
      </div>
    </div>
    <!-- 标题 -->
    <div class="skeleton-line skeleton-detail-title"></div>
    <!-- 内容段落 -->
    <div class="skeleton-line skeleton-paragraph"></div>
    <div class="skeleton-line skeleton-paragraph short"></div>
    <div class="skeleton-line skeleton-paragraph"></div>
    <!-- 底部操作 -->
    <div class="skeleton-detail-actions">
      <div class="skeleton-btn"></div>
      <div class="skeleton-btn"></div>
    </div>
  </div>

  <!-- 订单卡片骨架屏 -->
  <div v-else-if="variant === 'order'" class="skeleton-order-list">
    <div 
      v-for="i in count" 
      :key="i" 
      class="skeleton-order-item"
    >
      <!-- 左侧颜色条 -->
      <div class="skeleton-order-bar"></div>
      <!-- 订单内容 -->
      <div class="skeleton-order-content">
        <div class="skeleton-order-header">
          <div class="skeleton-line skeleton-tag"></div>
          <div class="skeleton-line skeleton-status"></div>
        </div>
        <div class="skeleton-line skeleton-order-title"></div>
        <div class="skeleton-order-helper">
          <div class="skeleton-avatar-tiny"></div>
          <div class="skeleton-line skeleton-helper-name"></div>
        </div>
        <div class="skeleton-order-footer">
          <div class="skeleton-line skeleton-price"></div>
          <div class="skeleton-order-actions">
            <div class="skeleton-action-btn"></div>
            <div class="skeleton-action-btn"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  // 骨架屏类型: list | card | detail | order
  variant: {
    type: String,
    default: 'list',
    validator: (val) => ['list', 'card', 'detail', 'order'].includes(val)
  },
  // 骨架屏数量 (用于列表类型)
  count: {
    type: Number,
    default: 4
  }
})
</script>

<style scoped>
/* ==========================================
   骨架屏动画效果
   ========================================== */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 骨架元素基础样式 */
.skeleton-line,
.skeleton-avatar,
.skeleton-avatar-small,
.skeleton-avatar-large,
.skeleton-avatar-tiny,
.skeleton-image,
.skeleton-btn,
.skeleton-order-bar,
.skeleton-tag,
.skeleton-status,
.skeleton-action-btn {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

/* ==========================================
   列表骨架屏 (聊天、基础列表)
   ========================================== */
.skeleton-list {
  padding: 0;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #f3f4f6;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-title {
  width: 40%;
  height: 16px;
}

.skeleton-text {
  width: 70%;
  height: 14px;
}

/* ==========================================
   卡片骨架屏 (市场、首页)
   ========================================== */
.skeleton-card-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px;
}

.skeleton-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.skeleton-image {
  width: 100%;
  height: 120px;
  border-radius: 0;
}

.skeleton-card-body {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-card-title {
  width: 80%;
  height: 14px;
}

.skeleton-card-desc {
  width: 60%;
  height: 12px;
}

.skeleton-card-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.skeleton-avatar-small {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-name {
  width: 50px;
  height: 12px;
}

/* ==========================================
   详情页骨架屏
   ========================================== */
.skeleton-detail {
  padding: 16px;
  background: white;
  min-height: 300px;
}

.skeleton-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.skeleton-avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-detail-name {
  width: 100px;
  height: 16px;
}

.skeleton-detail-sub {
  width: 80px;
  height: 12px;
}

.skeleton-detail-title {
  width: 90%;
  height: 20px;
  margin-bottom: 16px;
}

.skeleton-paragraph {
  width: 100%;
  height: 14px;
  margin-bottom: 10px;
}

.skeleton-paragraph.short {
  width: 70%;
}

.skeleton-detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.skeleton-btn {
  flex: 1;
  height: 44px;
  border-radius: 8px;
}

/* ==========================================
   订单卡片骨架屏
   ========================================== */
.skeleton-order-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-order-item {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.skeleton-order-bar {
  width: 4px;
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  border-radius: 0;
}

.skeleton-order-content {
  flex: 1;
  margin-left: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-tag {
  width: 40px;
  height: 18px;
}

.skeleton-status {
  width: 60px;
  height: 20px;
  border-radius: 10px;
}

.skeleton-order-title {
  width: 85%;
  height: 16px;
}

.skeleton-order-helper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f9fafb;
  padding: 8px;
  border-radius: 8px;
}

.skeleton-avatar-tiny {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-helper-name {
  width: 60px;
  height: 12px;
}

.skeleton-order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
}

.skeleton-price {
  width: 80px;
  height: 14px;
}

.skeleton-order-actions {
  display: flex;
  gap: 8px;
}

.skeleton-action-btn {
  width: 60px;
  height: 28px;
  border-radius: 14px;
}
</style>
