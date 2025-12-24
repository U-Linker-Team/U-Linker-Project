<template>
  <div class="home-container">
    <div class="mobile-frame">
      <div class="status-bar"></div>

      <!-- 顶部导航 -->
      <header class="header-bar">
        <span class="app-title">U-Linker</span>
        <div class="header-icons">
          <!-- 消息 -->
          <div class="icon-btn" @click="router.push('/chat')">
            <Icon icon="mdi:bell-outline" class="w-6 h-6 text-gray-600" />
          </div>
          <!-- 搜索按钮 -->
          <div class="icon-btn" @click="openSearch">
            <Icon icon="mdi:magnify" class="w-6 h-6 text-gray-600" />
          </div>
        </div>
      </header>

      <!-- ================= 🔍 搜索面板 (全屏覆盖) ================= -->
      <div v-if="showSearchBar" class="search-panel animate-fade-in">
        <!-- 搜索头 -->
        <div class="search-header">
          <div class="search-input-wrapper">
            <Icon icon="mdi:magnify" class="w-5 h-5 text-gray-400" />
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索任务标题..."
              class="search-input"
              @keyup.enter="handleSearch"
              autofocus
            />
            <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">
              <Icon icon="mdi:close-circle" class="w-5 h-5 text-gray-400" />
            </button>
          </div>
          <button class="cancel-btn" @click="closeSearch">取消</button>
        </div>

        <!-- 排序按钮 (仅在有搜索词或有结果时显示) -->
        <div v-if="searchKeyword || searchResultList.length > 0" class="flex items-center gap-3 px-4 py-2 border-b border-gray-50">
           <span v-for="opt in sortOptions" :key="opt.value"
             @click="changeSort(opt.value)"
             :class="['text-xs px-3 py-1 rounded-full cursor-pointer transition-colors', 
               sortBy === opt.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600']"
           >
             {{ opt.label }}
           </span>
        </div>

        <!-- 搜索内容主体 -->
        <div class="search-body">
          <!-- A. 加载中 -->
          <div v-if="searchLoading" class="py-10 text-center text-gray-400 text-sm">
            <Icon icon="mdi:loading" class="w-8 h-8 animate-spin mx-auto mb-2" />
            搜索中...
          </div>

          <!-- B. 搜索结果列表 -->
          <div v-else-if="searchResultList.length > 0" class="search-results px-4 py-3 space-y-3">
            <div class="text-xs text-gray-400 mb-2">找到 {{ searchResultList.length }} 个结果</div>
            <TaskCard 
              v-for="item in searchResultList" 
              :key="item.id" 
              :data="item"
              @click="openDetail(item.id)"
            />
          </div>

          <!-- C. 无结果 -->
          <div v-else-if="searchKeyword && !searchLoading" class="py-20 text-center text-gray-400">
            <Icon icon="mdi:file-search-outline" class="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">未找到相关任务</p>
          </div>

          <!-- D. 初始状态 (热门搜索词) -->
          <div v-else class="px-6 py-8">
            <div class="flex items-center gap-2 text-sm font-bold text-gray-800 mb-4">
              <Icon icon="mdi:fire" class="text-red-500" /> 热门搜索
            </div>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in ['取快递', '代买饭', '二手书', '修电脑', '占座']" 
                :key="tag"
                @click="quickSearch(tag)"
                class="px-3 py-1.5 bg-gray-100 rounded-full text-xs text-gray-600 cursor-pointer hover:bg-blue-50 hover:text-blue-600"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <!-- ================= 搜索面板结束 ================= -->

      <!-- 主页内容 (被搜索面板覆盖) -->
      <main class="main-content">
        <!-- Banner -->
        <div class="banner">
          <div class="banner-content">
            <h3 class="banner-title">校园互助新体验</h3>
            <p class="banner-subtitle">查看最新公告 ></p>
          </div>
        </div>

        <!-- 功能卡片 -->
        <div class="function-cards">
          <div class="function-card need-card" @click="goToPublish('bounty')">
            <div class="card-icon"><Icon icon="mdi:hand-extended-outline" class="w-8 h-8 text-blue-600" /></div>
            <div class="card-text"><h3 class="card-title">我需要</h3><p class="card-desc">发布悬赏 / 寻求帮助</p></div>
          </div>
          <div class="function-card provide-card" @click="goToPublish('service')">
            <div class="card-icon"><Icon icon="mdi:briefcase-outline" class="w-8 h-8 text-orange-500" /></div>
            <div class="card-text"><h3 class="card-title">我能提供</h3><p class="card-desc">出售技能 / 赚取积分</p></div>
          </div>
        </div>

        <!-- 积分卡片 -->
        <div class="points-card" @click="router.push('/points-detail')">
          <div class="points-info">
            <div class="points-label"><Icon icon="mdi:wallet-outline" class="w-4 h-4" /> 当前积分余额</div>
            <div class="points-value">{{ currentPoints }}</div>
          </div>
          <div class="points-icon"><Icon icon="mdi:currency-usd" class="w-6 h-6 text-yellow-400" /></div>
        </div>

        <!-- 热门互助 (只展示 homeList) -->
        <div class="hot-tasks">
          <div class="section-header">
            <h2 class="section-title">热门互助</h2>
            <span class="more-link" @click="router.push('/market')">更多 <Icon icon="mdi:chevron-right" class="w-4 h-4" /></span>
          </div>
          <div class="tasks-list space-y-3">
            <TaskCard v-for="item in homeList" :key="item.id" :data="item" @click="openDetail(item.id)" />
            
            <div v-if="loadingHome" class="text-center text-gray-400 py-4 text-sm">加载中...</div>
          </div>
        </div>
      </main>

      <TaskDetailModal :show="showDetail" :taskId="currentTaskId" @close="showDetail = false" />
      <BottomNav active-tab="home" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useUserStore } from '@/stores/user'
import { getPostList } from '@/api/market'
// 组件
import TaskCard from '@/components/market/TaskCard.vue' 
import BottomNav from '@/components/common/BottomNav.vue'
import TaskDetailModal from '@/components/market/TaskDetailModal.vue'

const router = useRouter()
const userStore = useUserStore()
const currentPoints = computed(() => userStore.userInfo?.points || 0)

// === 1. 首页数据 (独立) ===
const homeList = ref([]) // 专门存首页热门
const loadingHome = ref(false)

const fetchHomeData = async () => {
  loadingHome.value = true
  try {
    const res = await getPostList({ page: 1, page_size: 5, sort: 'time' }) 
    if (res.status === 'success') {
      homeList.value = res.data.items
    }
  } finally {
    loadingHome.value = false
  }
}

// === 2. 搜索逻辑 (独立) ===
const showSearchBar = ref(false)
const searchKeyword = ref('')
const searchResultList = ref([]) // 专门存搜索结果
const searchLoading = ref(false)
const sortBy = ref('created_at') // 搜索时的排序

const sortOptions = [
  { label: '最新', value: 'created_at' },
  { label: '积分最高', value: 'price_desc' },
  { label: '积分最低', value: 'price_asc' }
]

// 打开/关闭搜索
const openSearch = () => { showSearchBar.value = true }
const closeSearch = () => { 
  showSearchBar.value = false
  // 可以在这里清空搜索，也可以保留上次状态
  // clearSearch() 
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResultList.value = []
}

// 快捷搜索
const quickSearch = (tag) => {
  searchKeyword.value = tag
  handleSearch()
}

// 切换排序
const changeSort = (val) => {
  sortBy.value = val
  if (searchKeyword.value) handleSearch()
}

// 执行搜索 API
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) return
  
  searchLoading.value = true
  
  // 参数转换
  let sortParam = 'time', orderParam = 'desc'
  if (sortBy.value === 'price_desc') { sortParam = 'price'; orderParam = 'desc' }
  if (sortBy.value === 'price_asc') { sortParam = 'price'; orderParam = 'asc' }

  try {
    const res = await getPostList({ 
      keyword: searchKeyword.value, 
      sort: sortParam,
      order: orderParam,
      page: 1, 
      page_size: 20 
    })
    if (res.status === 'success') {
      searchResultList.value = res.data.items
    }
  } catch (e) {
    console.error(e)
  } finally {
    searchLoading.value = false
  }
}

// === 3. 公共交互 ===
const showDetail = ref(false)
const currentTaskId = ref(null)

const goToPublish = (type) => router.push(`/publish?type=${type}`)
const openDetail = (id) => {
  if (!id) return
  currentTaskId.value = id
  showDetail.value = true
}

onMounted(() => {
  fetchHomeData()
  
  // 监听帖子删除事件
  const handlePostDeleted = () => {
    console.log('帖子被删除，刷新主页数据')
    fetchHomeData()
  }
  
  window.addEventListener('post-deleted', handlePostDeleted)
})


</script>

<style scoped>
/* 基础容器 & 移动端框架 */
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
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 状态栏 & 顶部导航 */
.status-bar { height: 2rem; background-color: white; width: 100%; flex-shrink: 0; }
.header-bar {
  height: 3.5rem;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 1.25rem; border-bottom: 1px solid #f9fafb; background-color: white;
  position: sticky; top: 0; z-index: 10; flex-shrink: 0;
}
.app-title { font-size: 1.25rem; font-weight: 700; color: #2563eb; letter-spacing: -0.025em; }
.header-icons { display: flex; gap: 1rem; }
.header-icon { width: 1.5rem; height: 1.5rem; color: #4b5563; cursor: pointer; }

/* 主内容区域 */
.main-content {
  flex: 1; overflow-y: auto; padding: 0 1.25rem 5rem; /* 底部留白给 BottomNav */
  background-color: white;
  -ms-overflow-style: none; scrollbar-width: none;
}
.main-content::-webkit-scrollbar { display: none; }

/* Banner */
.banner {
  margin-top: 1.25rem; height: 10rem; border-radius: 1rem; overflow: hidden; position: relative;
  background: linear-gradient(to right, #3b82f6, #4f46e5);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex; align-items: center; justify-content: center;
}
.banner-title { font-size: 1.125rem; font-weight: 700; color: white; }
.banner-subtitle {
  font-size: 0.75rem; color: #93c5fd; margin-top: 0.25rem;
  background: rgba(255, 255, 255, 0.2); padding: 0.25rem 0.75rem; border-radius: 9999px;
}

/* 功能卡片 */
.function-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }
.function-card {
  border-radius: 1rem; padding: 1.25rem; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 0.75rem; cursor: pointer;
  border: 1px solid transparent; transition: all 0.2s ease;
}
.function-card:active { transform: scale(0.95); }
.need-card { background-color: #eff6ff; border-color: #dbeafe; }
.provide-card { background-color: #fffbeb; border-color: #fef3c7; }
.card-icon {
  width: 3.5rem; height: 3.5rem; background-color: white; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.need-card .card-icon .iconify { width: 2rem; height: 2rem; color: #2563eb; }
.provide-card .card-icon .iconify { width: 2rem; height: 2rem; color: #f59e0b; }
.card-title { font-size: 1.125rem; font-weight: 700; color: #1f2937; }
.card-desc { font-size: 0.75rem; font-weight: 500; margin-top: 0.25rem; }
.need-card .card-desc { color: #2563eb; }
.provide-card .card-desc { color: #f59e0b; }

/* 积分卡片 */
.points-card {
  margin-top: 1.5rem; background: linear-gradient(to bottom right, #111827, #1f2937);
  border-radius: 1rem; padding: 1.25rem; color: white;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}
.points-label { display: flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; color: #9ca3af; }
.points-value { font-size: 1.875rem; font-weight: 700; color: #fbbf24; }
.points-icon { width: 2.5rem; height: 2.5rem; background-color: rgba(255, 255, 255, 0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.points-icon .iconify { width: 1.5rem; height: 1.5rem; color: #fbbf24; }

/* 热门互助 */
.hot-tasks { margin-top: 2rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-title { font-size: 1.125rem; font-weight: 700; color: #1f2937; }
.more-link { font-size: 0.75rem; color: #9ca3af; display: flex; align-items: center; cursor: pointer; }
.tasks-list { display: flex; flex-direction: column; gap: 1rem; }

/* 响应式 */
@media (max-width: 400px) {
  .home-container { padding: 0.5rem; }
  .mobile-frame { width: 100%; height: 100vh; border-radius: 0; }
}
</style>