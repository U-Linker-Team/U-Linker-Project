import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 1. 用户信息
  const userInfo = ref(null) // 刷新后这里会变成 null
  
  // 2. [新增] 全局未读消息数
  const unreadCount = ref(0)


  // normalize 后端返回的 user 对象字段
  const normalizeUser = (data) => {
    if (!data) return null
    return {
      ...data,
      // 支持后端返回 student_id 或 studentId
      studentId: data.studentId || data.student_id || '',
      // 兼容可能的 avatar 字段（后端可能返回 avatar/url）
      avatar: data.avatar || data.url || '',
      // 兼容 is_admin / isAdmin
      is_admin: typeof data.is_admin !== 'undefined' ? data.is_admin : data.isAdmin || false,
      // 保持原有 id/name/username/college/points 等
      id: data.id,
      name: data.name || data.username || '',
      username: data.username || '',
      college: data.college || '',
      points: data.points || 0
    }
  }
  
  // 登录动作
  const login = (data) => {
    // 规范化数据后再存储，确保字段统一
    const normalized = normalizeUser(data)
    userInfo.value = normalized
    // 可以顺便存到 localStorage 做持久化备份
    localStorage.setItem('u-linker-user', JSON.stringify(normalized))
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
        const parsed = JSON.parse(local)
        // 从缓存读取时也要规范化，确保格式一致
        userInfo.value = normalizeUser(parsed)
      } catch(e) {
        console.error('解析用户缓存失败', e)
      }
    }
  }
  
  // 立即执行初始化
  init()

  return { userInfo, unreadCount, login, logout }
})