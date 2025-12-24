import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 1. 用户信息
  const userInfo = ref(null) // 刷新后这里会变成 null
  
  // 2. [新增] 全局未读消息数
  const unreadCount = ref(0)

  // 登录动作
  const login = (data) => {
    userInfo.value = data
    // 可以顺便存到 localStorage 做持久化备份
    localStorage.setItem('u-linker-user', JSON.stringify(data))
  }

  // 登出动作
  const logout = () => {
    userInfo.value = null
    unreadCount.value = 0
    localStorage.removeItem('u-linker-user')
  }

  // 初始化（尝试从本地缓存读取，防止 F5 瞬间白屏）
  const init = () => {
    const local = localStorage.getItem('u-linker-user')
    if (local) {
      try {
        userInfo.value = JSON.parse(local)
      } catch(e) {}
    }
  }
  
  // 立即执行初始化
  init()

  return { userInfo, unreadCount, login, logout }
})