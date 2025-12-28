<template>
  <div class="admin-container">
    <div class="mobile-frame">
      <!-- 状态栏占位 -->
      <div class="status-bar"></div>
      <!-- 顶部导航 -->
      <header class="header-bar">
        <div class="header-back" @click="router.push('/home')">
          <span class="iconify" data-icon="mdi:arrow-left"></span>
        </div>
        <span class="app-title">管理员后台</span>
        <div class="header-icons">
          <span class="iconify header-icon" data-icon="mdi:refresh" @click="refreshStats"></span>
        </div>
      </header>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:account-group"></span>
              总用户数
            </div>
            <div class="stat-value">{{ stats.users?.total || 0 }}</div>
          </div>
          <div class="stat-card stat-card-available">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:account-check"></span>
              可用用户
            </div>
            <div class="stat-value text-blue-600">{{ stats.users?.active || 0 }}</div>
            <div class="stat-hint">未被封禁或已解封</div>
          </div>
          <div class="stat-card stat-card-active">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:account-clock"></span>
              活跃用户
            </div>
            <div class="stat-value text-green-600">
              {{ dailyStats?.summary?.active_users_last_7_days ?? (statsLoading ? '加载中...' : '点击统计报表查看') }}
            </div>
            <div class="stat-hint">最近7天有操作</div>
          </div>
          <div class="stat-card stat-card-banned">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:account-cancel"></span>
              封禁用户
            </div>
            <div class="stat-value text-red-600">{{ stats.users?.banned || 0 }}</div>
            <div class="stat-hint">当前被封禁</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:file-document"></span>
              总帖子数
            </div>
            <div class="stat-value">{{ stats.posts?.total || 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">
              <span class="iconify" data-icon="mdi:shopping"></span>
              总订单数
            </div>
            <div class="stat-value">{{ stats.orders?.total || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- 功能菜单 -->
      <main class="main-content">
        <div class="menu-section">
          <div class="menu-item" @click="activeTab = 'users'">
            <span class="iconify menu-icon" data-icon="mdi:account-group"></span>
            <span class="menu-text">用户管理</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
          <div class="menu-item" @click="activeTab = 'posts'">
            <span class="iconify menu-icon" data-icon="mdi:file-document"></span>
            <span class="menu-text">帖子管理</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
          <div class="menu-item" @click="activeTab = 'orders'">
            <span class="iconify menu-icon" data-icon="mdi:shopping"></span>
            <span class="menu-text">订单管理</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
          <div class="menu-item" @click="activeTab = 'points'">
            <span class="iconify menu-icon" data-icon="mdi:currency-usd"></span>
            <span class="menu-text">积分流动</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
          <div class="menu-item" @click="activeTab = 'stats'">
            <span class="iconify menu-icon" data-icon="mdi:chart-line"></span>
            <span class="menu-text">统计报表</span>
            <span class="iconify arrow-icon" data-icon="mdi:chevron-right"></span>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="content-section">
          <!-- 用户管理 -->
          <div v-if="activeTab === 'users'" class="tab-content">
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
          </div>

          <!-- 帖子管理 -->
          <div v-if="activeTab === 'posts'" class="tab-content">
            <div class="search-bar">
              <input 
                v-model="postSearchKeyword"
                @input="searchPosts"
                type="text" 
                placeholder="搜索帖子（标题、内容、作者）"
                class="search-input"
              />
            </div>
            <!-- 导入导出按钮 -->
            <div class="action-buttons">
              <button @click="exportPosts" class="action-btn export-btn">
                <span class="iconify" data-icon="mdi:download"></span>
                导出帖子数据
              </button>
              <label class="action-btn import-btn">
                <input 
                  type="file" 
                  accept=".xlsx,.xls" 
                  @change="handleFileImport" 
                  style="display: none"
                />
                <span class="iconify" data-icon="mdi:upload"></span>
                导入帖子数据
              </label>
            </div>
            <div class="table-container">
              <div v-if="postsLoading" class="loading">加载中...</div>
              <div v-else-if="postsList.length === 0" class="empty">暂无帖子</div>
              <div v-else class="post-list">
                <div 
                  v-for="post in postsList" 
                  :key="post.id"
                  class="post-item"
                >
                  <div class="post-title">{{ post.title }}</div>
                  <div class="post-meta">
                    {{ post.author?.name || '未知用户' }} · 
                    {{ post.post_type === 'bounty' ? '悬赏' : '服务' }} · 
                    {{ post.status === 'active' ? '招募中' : post.status === 'trading' ? '进行中' : post.status === 'sold' ? '已完成' : '已下架' }}
                  </div>
                  <div class="post-price">{{ post.price }} 积分</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 订单管理 -->
          <div v-if="activeTab === 'orders'" class="tab-content">
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
          </div>

          <!-- 积分流动 -->
          <div v-if="activeTab === 'points'" class="tab-content">
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
          </div>

          <!-- 统计报表 (5.4-5.6) -->
          <div v-if="activeTab === 'stats'" class="tab-content">
            <!-- 时间范围选择 -->
            <div class="stats-controls">
              <div class="control-group">
                <label>开始日期</label>
                <input 
                  v-model="statsStartDate" 
                  type="date" 
                  class="date-input"
                  @change="loadDailyStats"
                />
              </div>
              <div class="control-group">
                <label>结束日期</label>
                <input 
                  v-model="statsEndDate" 
                  type="date" 
                  class="date-input"
                  @change="loadDailyStats"
                />
              </div>
              <div class="control-group">
                <label>分组方式</label>
                <select v-model="statsGroupBy" @change="loadDailyStats" class="select-input">
                  <option value="day">按天</option>
                  <option value="week">按周</option>
                  <option value="month">按月</option>
                </select>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="stats-actions">
              <button @click="loadDailyStats" class="action-btn refresh-btn">
                <span class="iconify" data-icon="mdi:refresh"></span>
                刷新数据
              </button>
              <button @click="exportStats" class="action-btn export-btn">
                <span class="iconify" data-icon="mdi:download"></span>
                导出Excel
              </button>
              <button @click="showCharts = !showCharts" class="action-btn chart-btn">
                <span class="iconify" data-icon="mdi:chart-line"></span>
                {{ showCharts ? '隐藏图表' : '显示图表' }}
              </button>
            </div>

            <!-- 统计摘要 -->
            <div v-if="dailyStats" class="stats-summary">
              <h3 class="summary-title">
                <span class="iconify" data-icon="mdi:chart-box"></span>
                统计摘要
              </h3>
              <div class="summary-grid">
                <div class="summary-card">
                  <div class="summary-label">新增用户总数</div>
                  <div class="summary-value">{{ dailyStats.summary?.total_new_users || 0 }}</div>
                </div>
                <div class="summary-card">
                  <div class="summary-label">新增帖子总数</div>
                  <div class="summary-value">{{ dailyStats.summary?.total_new_posts || 0 }}</div>
                </div>
                <div class="summary-card summary-card-active">
                  <div class="summary-label">
                    <span class="iconify" data-icon="mdi:account-clock"></span>
                    活跃用户数
                  </div>
                  <div class="summary-value text-green-600">{{ dailyStats.summary?.active_users_last_7_days || 0 }}</div>
                  <div class="summary-hint">最近7天有操作</div>
                </div>
                <div class="summary-card">
                  <div class="summary-label">新增悬赏任务</div>
                  <div class="summary-value text-orange-600">{{ dailyStats.summary?.total_new_bounties || 0 }}</div>
                </div>
                <div class="summary-card">
                  <div class="summary-label">新增服务任务</div>
                  <div class="summary-value text-blue-600">{{ dailyStats.summary?.total_new_services || 0 }}</div>
                </div>
              </div>
            </div>

            <!-- 用户类型说明卡片 -->
            <div class="user-types-info">
              <h4 class="info-title">
                <span class="iconify" data-icon="mdi:information"></span>
                用户类型说明
              </h4>
              <div class="info-cards">
                <div class="info-card info-card-available">
                  <div class="info-card-header">
                    <span class="iconify" data-icon="mdi:account-check"></span>
                    <span class="info-card-title">可用用户</span>
                  </div>
                  <div class="info-card-content">
                    <div class="info-card-value">{{ stats.users?.active || 0 }}</div>
                    <div class="info-card-desc">没有被封禁或封禁已过期的用户</div>
                  </div>
                </div>
                <div class="info-card info-card-active">
                  <div class="info-card-header">
                    <span class="iconify" data-icon="mdi:account-clock"></span>
                    <span class="info-card-title">活跃用户</span>
                  </div>
                  <div class="info-card-content">
                    <div class="info-card-value text-green-600">{{ dailyStats?.summary?.active_users_last_7_days || '-' }}</div>
                    <div class="info-card-desc">最近7天内有登录或注册操作的用户</div>
                  </div>
                </div>
                <div class="info-card info-card-banned">
                  <div class="info-card-header">
                    <span class="iconify" data-icon="mdi:account-cancel"></span>
                    <span class="info-card-title">封禁用户</span>
                  </div>
                  <div class="info-card-content">
                    <div class="info-card-value text-red-600">{{ stats.users?.banned || 0 }}</div>
                    <div class="info-card-desc">当前时间仍在封禁期内的用户</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 详细统计数据表格 -->
            <div v-if="dailyStats" class="stats-table-section">
              <h3 class="table-title">
                <span class="iconify" data-icon="mdi:table"></span>
                详细统计数据
              </h3>
              <div class="table-wrapper">
                <table class="stats-table">
                  <thead>
                    <tr>
                      <th>{{ statsGroupBy === 'day' ? '日期' : statsGroupBy === 'week' ? '周' : '月' }}</th>
                      <th>新增用户</th>
                      <th>新增帖子</th>
                      <th>悬赏任务</th>
                      <th>服务任务</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in dailyStats.daily_stats" :key="index">
                      <td>{{ statsGroupBy === 'day' ? item.date : item.period }}</td>
                      <td>{{ item.new_users }}</td>
                      <td>{{ item.new_posts_total }}</td>
                      <td class="text-orange-600">{{ item.new_bounties || 0 }}</td>
                      <td class="text-blue-600">{{ item.new_services || 0 }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 图表区域 -->
            <div v-if="showCharts" class="charts-section">
              <h3 class="chart-title">
                <span class="iconify" data-icon="mdi:chart-line"></span>
                数据趋势图表
              </h3>
              <div class="chart-controls">
                <button 
                  v-for="type in ['line', 'bar', 'pie']" 
                  :key="type"
                  @click="loadChart(type)"
                  :class="['chart-type-btn', { active: chartType === type }]"
                >
                  {{ type === 'line' ? '折线图' : type === 'bar' ? '柱状图' : '饼图' }}
                </button>
              </div>
              <div v-if="chartData" class="chart-container">
                <div class="chart-placeholder">
                  <p class="chart-hint">图表数据已加载，可使用 ECharts 等图表库渲染</p>
                  <pre class="chart-data-preview">{{ JSON.stringify(chartData, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <BottomNav active-tab="profile" />
    </div>

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
import { getStats, getAllUsers, getAllPosts, getAllOrders, getAllPointsHistory, exportPostsExcel, importPostsExcel, getUserByStudentId, getDailyStats, exportStatsExcel, getStatsCharts } from '@/api/admin'
import { getImageUrl } from '@/utils/imageHelper'
import BottomNav from '@/components/common/BottomNav.vue'
import UserDetailModal from '@/components/admin/UserDetailModal.vue'

const router = useRouter()
const userStore = useUserStore()

// 检查管理员权限
const checkAdmin = () => {
  if (!userStore.userInfo || !userStore.userInfo.is_admin) {
    alert('权限不足：需要管理员权限')
    router.push('/home')
    return false
  }
  return true
}

// 状态管理
const activeTab = ref('users')
const stats = ref({})
const usersList = ref([])
const postsList = ref([])
const ordersList = ref([])
const pointsList = ref([])
const usersLoading = ref(false)
const postsLoading = ref(false)
const ordersLoading = ref(false)
const pointsLoading = ref(false)
const userSearchKeyword = ref('')
const postSearchKeyword = ref('')
const selectedUser = ref(null)
const studentIdSearch = ref('')
const studentIdResult = ref(null)
const postsTab = ref('i_need')
const studentIdLoading = ref(false)
const searchMode = ref('list') // 'list' 或 'studentId'

// 统计报表相关状态 (5.4-5.6)
const dailyStats = ref(null)
const statsLoading = ref(false)
const statsStartDate = ref('')
const statsEndDate = ref('')
const statsGroupBy = ref('day')
const showCharts = ref(false)
const chartType = ref('line')
const chartData = ref(null)

// 获取统计信息
const refreshStats = async () => {
  try {
    const res = await getStats()
    if (res.status === 'success') {
      stats.value = res.data
    }
    // 如果统计报表页面已打开，同时加载每日统计
    if (activeTab.value === 'stats') {
      await loadDailyStats()
    }
  } catch (e) {
    console.error('获取统计信息失败', e)
  }
}

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

// 获取帖子列表
const searchPosts = async () => {
  postsLoading.value = true
  try {
    const res = await getAllPosts({
      keyword: postSearchKeyword.value,
      page: 1,
      page_size: 50
    })
    if (res.status === 'success') {
      postsList.value = res.data.items
    }
  } catch (e) {
    console.error('获取帖子列表失败', e)
  } finally {
    postsLoading.value = false
  }
}

// 获取订单列表
const fetchOrders = async () => {
  ordersLoading.value = true
  try {
    const res = await getAllOrders({
      page: 1,
      page_size: 50
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

// 获取积分流动记录
const fetchPointsHistory = async () => {
  pointsLoading.value = true
  try {
    const res = await getAllPointsHistory({
      page: 1,
      page_size: 50
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

// 打开用户详情
const openUserDetail = (user) => {
  selectedUser.value = user
}

// 刷新用户列表
const refreshUsers = () => {
  searchUsers()
  refreshStats()
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
      postsTab.value = 'i_need' // 默认显示"我需要"
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

// 导出帖子数据
const exportPosts = async () => {
  try {
    const response = await exportPostsExcel()
    
    // 检查响应数据
    if (!response || !response.data) {
      alert('导出失败：服务器返回的数据为空')
      return
    }
    
    // response.data 应该是 Blob 类型（因为设置了 responseType: 'blob'）
    const blob = response.data
    
    // 验证 Blob
    if (!(blob instanceof Blob)) {
      console.error('响应数据不是 Blob 类型:', typeof blob, blob)
      alert('导出失败：服务器返回的数据格式错误')
      return
    }
    
    // 验证 Blob 大小
    if (blob.size === 0) {
      alert('导出失败：文件大小为0，可能是服务器错误')
      return
    }
    
    // 验证 MIME 类型
    if (blob.type && !blob.type.includes('spreadsheet') && !blob.type.includes('excel')) {
      console.warn('文件 MIME 类型可能不正确:', blob.type)
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名（使用标准格式）
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hour = String(now.getHours()).padStart(2, '0')
    const minute = String(now.getMinutes()).padStart(2, '0')
    const second = String(now.getSeconds()).padStart(2, '0')
    const timestamp = `${year}${month}${day}_${hour}${minute}${second}`
    
    link.setAttribute('download', `帖子数据报表_${timestamp}.xlsx`)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    alert('导出成功！文件已下载')
  } catch (error) {
    console.error('导出失败:', error)
    console.error('错误详情:', error.response)
    alert('导出失败：' + (error.response?.data?.message || error.message || '未知错误'))
  }
}

// 处理文件导入
const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    alert('只支持 Excel 文件 (.xlsx, .xls)')
    return
  }
  
  // 确认导入
  if (!confirm(`确定要导入文件 "${file.name}" 吗？\n\n注意：\n1. Excel 文件必须包含以下列：标题、内容、价格(积分)、类型、作者用户名\n2. 类型必须是"悬赏"或"服务"\n3. 悬赏任务会自动扣除作者积分`)) {
    event.target.value = '' // 清空文件选择
    return
  }
  
  try {
    const res = await importPostsExcel(file)
    if (res.status === 'success') {
      const data = res.data
      let message = `导入完成！\n成功：${data.success_count} 条\n失败：${data.error_count} 条`
      
      if (data.errors && data.errors.length > 0) {
        message += '\n\n错误详情：\n' + data.errors.slice(0, 5).join('\n')
        if (data.errors.length > 5) {
          message += `\n... 还有 ${data.errors.length - 5} 个错误`
        }
      }
      
      alert(message)
      
      // 刷新帖子列表
      if (data.success_count > 0) {
        await searchPosts()
        await refreshStats()
      }
    } else {
      alert(res.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    alert('导入失败：' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    // 清空文件选择，允许重复选择同一文件
    event.target.value = ''
  }
}

// 监听标签切换
const watchTab = () => {
  if (activeTab.value === 'users') {
    searchUsers()
  } else if (activeTab.value === 'posts') {
    searchPosts()
  } else if (activeTab.value === 'orders') {
    fetchOrders()
  } else if (activeTab.value === 'points') {
    fetchPointsHistory()
  }
}

// 加载每日统计数据 (5.4)
const loadDailyStats = async () => {
  statsLoading.value = true
  try {
    const params = {
      group_by: statsGroupBy.value
    }
    if (statsStartDate.value) params.start_date = statsStartDate.value
    if (statsEndDate.value) params.end_date = statsEndDate.value
    
    const res = await getDailyStats(params)
    if (res.status === 'success') {
      dailyStats.value = res.data
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
    alert('获取统计数据失败：' + (e.response?.data?.message || e.message))
  } finally {
    statsLoading.value = false
  }
}

// 导出统计数据 (5.5)
const exportStats = async () => {
  try {
    const params = {
      group_by: statsGroupBy.value
    }
    if (statsStartDate.value) params.start_date = statsStartDate.value
    if (statsEndDate.value) params.end_date = statsEndDate.value
    
    const response = await exportStatsExcel(params)
    const blob = response.data
    
    if (!(blob instanceof Blob) || blob.size === 0) {
      alert('导出失败：服务器返回的数据格式错误')
      return
    }
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const now = new Date()
    const timestamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`
    link.setAttribute('download', `系统统计报表_${timestamp}.xlsx`)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    alert('导出成功！文件已下载')
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败：' + (error.response?.data?.message || error.message || '未知错误'))
  }
}

// 加载图表数据 (5.6)
const loadChart = async (type) => {
  chartType.value = type
  try {
    const res = await getStatsCharts({
      type: type,
      time_range: '7days'
    })
    if (res.status === 'success') {
      chartData.value = res.data.chart_data
    }
  } catch (e) {
    console.error('获取图表数据失败', e)
    alert('获取图表数据失败：' + (e.response?.data?.message || e.message))
  }
}

// 监听 activeTab 变化
watch(activeTab, (newTab) => {
  watchTab()
  if (newTab === 'stats') {
    // 设置默认日期范围（最近30天）
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)
    
    statsEndDate.value = endDate.toISOString().split('T')[0]
    statsStartDate.value = startDate.toISOString().split('T')[0]
    
    loadDailyStats()
  }
})

onMounted(async () => {
  // 检查管理员权限
  if (!userStore.userInfo || !userStore.userInfo.is_admin) {
    alert('权限不足：需要管理员权限')
    router.push('/home')
    return
  }
  
  // 加载数据
  await refreshStats()
  await searchUsers()
})
</script>

<style scoped>
.admin-container {
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
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 状态栏 */
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
}

.header-back {
  cursor: pointer;
  padding: 0.5rem;
}

.app-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.stats-section {
  padding: 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat-card {
  background: #f9fafb;
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.stat-label .iconify {
  font-size: 1rem;
  color: #6b7280;
}

.stat-hint {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.stat-card-available {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
}

.stat-card-active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
}

.stat-card-banned {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fecaca;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.menu-section {
  margin-bottom: 1.5rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:hover {
  background: #f9fafb;
}

.menu-icon {
  font-size: 1.5rem;
  color: #3b82f6;
}

.menu-text {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
}

.arrow-icon {
  color: #9ca3af;
}

.content-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1rem;
}

.search-bar {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
}

.table-container {
  max-height: 60vh;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.user-list, .post-list, .order-list, .points-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item, .post-item, .order-item, .points-item {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-item {
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
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  min-width: 0;
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

.post-title, .order-title {
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.post-meta, .order-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.post-price, .order-price {
  font-weight: 600;
  color: #3b82f6;
}

.points-item {
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

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn {
  background: #3b82f6;
  color: white;
}

.export-btn:hover {
  background: #2563eb;
}

.import-btn {
  background: #10b981;
  color: white;
  cursor: pointer;
}

.import-btn:hover {
  background: #059669;
}

.action-btn .iconify {
  font-size: 1.125rem;
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

.mode-tab .iconify {
  font-size: 1rem;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  gap: 0.5rem;
}

.search-input-wrapper .search-input {
  flex: 1;
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
  transition: all 0.2s;
  min-width: 3rem;
}

.search-btn-inline:hover {
  background: #2563eb;
}

.search-btn-inline .iconify {
  font-size: 1.25rem;
}

.student-id-result {
  background: #f9fafb;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #e5e7eb;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.result-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.close-result-btn {
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

.close-result-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
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

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #6b7280;
  min-width: 4rem;
  font-size: 0.875rem;
}

.points-highlight {
  color: #3b82f6;
  font-weight: 700;
  font-size: 1.125rem;
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
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
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
  transition: all 0.2s;
}

/* "我需要"帖子 - 橙色系 */
.post-item-i-need {
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-left-color: #f97316;
  box-shadow: 0 2px 4px rgba(249, 115, 22, 0.1);
}

.post-item-i-need:hover {
  box-shadow: 0 4px 8px rgba(249, 115, 22, 0.15);
  transform: translateY(-1px);
}

/* "我能提供"帖子 - 蓝色系 */
.post-item-i-provide {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-left-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.post-item-i-provide:hover {
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.post-header-result {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.post-title-result {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
  flex: 1;
  line-height: 1.4;
}

.post-price-badge {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.post-badges-result {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.badge-type {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-bounty {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid #fbbf24;
}

.badge-service {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border: 1px solid #60a5fa;
}

.badge-type .iconify {
  font-size: 0.875rem;
}

.badge-status {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

/* 状态颜色 */
.status-recruiting {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
  border: 1px solid #4ade80;
}

.status-trading {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border: 1px solid #60a5fa;
}

.status-completed {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #3730a3;
  border: 1px solid #818cf8;
}

.status-deleted {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #4b5563;
  border: 1px solid #9ca3af;
}

.post-content-result {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.6;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.empty-posts {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
  font-size: 0.875rem;
}

/* 响应式 */
@media (min-width: 768px) {
  .admin-container {
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

/* 统计报表样式 */
.stats-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.date-input, .select-input {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.date-input:focus, .select-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.stats-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.refresh-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.chart-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.stats-summary {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.summary-title .iconify {
  font-size: 1.25rem;
  color: #3b82f6;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: white;
  padding: 1rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.summary-card-active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
}

.summary-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.summary-label .iconify {
  font-size: 0.875rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.summary-hint {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.user-types-info {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.info-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.info-title .iconify {
  font-size: 1.125rem;
  color: #3b82f6;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-card {
  padding: 1rem;
  border-radius: 0.75rem;
  border: 2px solid;
  transition: all 0.2s;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-card-available {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-color: #93c5fd;
}

.info-card-active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #86efac;
}

.info-card-banned {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #fca5a5;
}

.info-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.info-card-header .iconify {
  font-size: 1.25rem;
}

.info-card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.info-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-card-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
}

.info-card-desc {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.4;
}

.stats-table-section {
  margin-bottom: 1.5rem;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.table-title .iconify {
  font-size: 1.125rem;
  color: #3b82f6;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.stats-table thead {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.stats-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.stats-table td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #1f2937;
  border-bottom: 1px solid #f3f4f6;
}

.stats-table tbody tr:hover {
  background: #f9fafb;
}

.stats-table tbody tr:last-child td {
  border-bottom: none;
}

.charts-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.chart-title .iconify {
  font-size: 1.125rem;
  color: #8b5cf6;
}

.chart-controls {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.chart-type-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-type-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.chart-type-btn.active {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border-color: #7c3aed;
}

.chart-container {
  min-height: 300px;
  padding: 2rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px dashed #d1d5db;
}

.chart-placeholder {
  text-align: center;
}

.chart-hint {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.chart-data-preview {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  text-align: left;
  max-height: 400px;
  overflow: auto;
  border: 1px solid #e5e7eb;
}

@media (max-width: 400px) {
  .admin-container { padding: 0.5rem; }
  .mobile-frame { width: 100%; height: 100vh; border-radius: 0; }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .summary-grid {
    grid-template-columns: 1fr;
  }
  .info-cards {
    grid-template-columns: 1fr;
  }
}
</style>

