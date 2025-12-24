import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user' // 引入 Store 用于判断登录状态

const routes = [
  
  // --- 1. 认证模块 ---
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/loginPage.vue')
  },
 
  {
    path: '/register', 
    name: 'Register',
    component: () => import('../views/RegisterPage.vue')
  },
  
   // --- 2. 根路径重定向 ---
  {
    path: '/',
    redirect: '/home' // 2. 访问根目录，尝试去首页
  },
  // --- 2. 核心市场模块 ---
  {
    path: "/home",
    name: "Home",
    component: () => import('../views/HomePage.vue')
  },
  // 2. 市场页 (专门找任务的地方)
  {
    path: "/market",
    name: "Market",
    component: () => import('../views/MarketPage.vue') 
  },
  {
    path: '/post/:id', // [新增] 帖子详情页
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue')
  },
  {
  path: '/publish',
  alias: '/provide-service', 
  name: 'ProvideService',
  component: () => import('../views/ProvideService.vue')
  },  
 
  // --- 3. 个人中心模块 ---
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileCenter.vue')
  },

  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: () => import('../views/EditProfile.vue')
  },

  {
    path: '/points-detail',
    name: 'PointsDetail',
    component: () => import('../views/PointsDetailView.vue')
  },
  {
    path: '/collect',
    name: 'Collect',
    component: () => import('../views/CollectPage.vue')
  },
  {
  path: '/order',
  name: 'Order',
  component: () => import('../views/OrderPage.vue')
  },
  
  //--- 4. 聊天模块 ---
  {
    path: '/chat',
    name: 'ChatList',
    component: () => import('../views/ChatList.vue')
  },
  {
    path: '/chat/:session_id',
    name: 'ChatDetail',
    component: () => import('../views/ChatDetail.vue')
  }
]



const router = createRouter({
  history: createWebHistory(),
  routes
})

// ==========================================
// 🛡️ 路由守卫 (保安)
// ==========================================
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 1. 定义白名单：不需要登录就能访问的页面
  const whiteList = ['/login', '/register']

  // 2. 打印日志方便调试
  console.log(`[路由守卫] 从 ${from.path} -> 去 ${to.path}, 用户信息:`, userStore.userInfo ? '已登录' : '未登录')

  // 3. 核心判断逻辑
  // 如果要去的地方是白名单 (登录/注册)，直接放行
  if (whiteList.includes(to.path)) {
    next()
    return
  }

  // 如果要去的地方不是白名单，且用户没有登录信息
  if (!userStore.userInfo) {
    console.log('[路由守卫] 用户未登录，拦截跳转到登录页')
    next('/login') // 强制踢回登录页
  } else {
    // 用户已登录，放行
    next()
  }
})

export default router