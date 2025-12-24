<template>
  <!-- 
    这里不需要 id="app"，因为 main.js 里的 mount('#app') 挂载的是 index.html 里的 div。
    直接作为路由出口即可。
  -->
  <router-view />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const userStore = useUserStore()
let pollingTimer = null

// --- 1. 尝试恢复登录状态 (防止刷新页面丢失登录态) ---
const restoreSession = async () => {
  // 如果当前 Pinia 里没有用户信息，尝试向后端要一下
  if (!userStore.userInfo) {
    try {
      // 注意：/auth/profile 需要 user_id 参数，这里暂时跳过
      // 如果需要恢复会话，需要后端提供一个从 session 读取当前用户的接口
      // const res = await request.get('/auth/profile', { params: { user_id: xxx } })
      // if (res.status === 'success') {
      //   userStore.login(res.data)
      //   console.log('✅ 会话恢复成功')
      // }
      console.log('跳过会话恢复（需要后端支持从 session 读取当前用户）')
    } catch (e) {
      // 401 报错说明 cookie 过期了，不用管，路由守卫会处理跳转
      console.log('未登录或会话已过期')
    }
  }
}

// --- 2. 全局消息轮询 (每10秒查一次未读数) ---
const startPolling = () => {
  // 定义轮询函数
  const checkUnread = async () => {
    // 只有登录了才查
    if (userStore.userInfo) {
      try {
        // 调用我们之前在 chat.py 写好的接口
        const res = await request.get('/chat/unread_total')
        if (res.status === 'success') {
          // 假设你在 userStore 里加了一个 unreadCount 字段
          // 或者你可以用 EventBus / ProvideInject 传给 BottomNav
          // 这里简单演示：存入 sessionStorage 或者更新 store
          userStore.unreadCount = res.data.total_unread
        }
      } catch (e) {
        // 如果是登录错误，可能是 session 失效，清除用户信息
        if (e.message && (e.message.includes('登录') || e.message.includes('未登录'))) {
          console.warn('[轮询] Session 失效，清除用户信息')
          userStore.logout()
          // 停止轮询
          if (pollingTimer) {
            clearInterval(pollingTimer)
            pollingTimer = null
          }
        } else {
          console.error('轮询消息失败', e)
        }
      }
    }
  }

  // 立即查一次
  checkUnread()
  // 启动定时器 (10秒一次)
  pollingTimer = setInterval(checkUnread, 10000)
}

onMounted(async () => {
  await restoreSession()
  startPolling()
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
</script>

<style>
/* --- 全局样式重置 --- */
:root {
  /* 解决移动端点击高亮背景色问题 */
  -webkit-tap-highlight-color: transparent;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  background-color: #f3f4f6; /* 全局背景灰，防止刘海屏露白 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  
  /* 禁用移动端双击缩放 */
  touch-action: manipulation; 
  -webkit-font-smoothing: antialiased;
}

#app {
  width: 100%;
  height: 100%;
}

/* 隐藏滚动条但保留滚动功能 (全局通用类) */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>