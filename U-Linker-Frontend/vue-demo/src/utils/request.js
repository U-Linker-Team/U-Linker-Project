import axios from 'axios'

// 创建实例
// 直接请求后端，不使用代理（避免前端路由被误代理）
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 直接请求后端
  timeout: 5000, // 请求超时时间
  withCredentials: true 
})

// 请求拦截器 (确保所有请求都携带 credentials)
service.interceptors.request.use(
  config => {
    // 确保所有请求都携带 credentials
    config.withCredentials = true
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 
service.interceptors.response.use(
  response => {
    // response.data 就是后端返回的那个字典: { status, message, data }
    const res = response.data

    // 修改逻辑：根据后端 response.py 的定义
    // 后端成功时 status 为 'success'，失败时为 'error'
    
    // 如果 status 存在，且不等于 'success'，说明是业务逻辑错误（如：积分不足、密码错误）
    if (res.status && res.status !== 'success') {
      // 检查是否是轮询接口的登录错误（不应该弹窗打扰用户）
      const isPollingRequest = response.config?.url && (
        response.config.url.includes('/chat/unread_total') || 
        response.config.url.includes('/chat/list')
      )
      
      // 检查是否是登录相关的错误
      const isLoginError = res.message && (
        res.message.includes('登录') || 
        res.message.includes('未登录') ||
        res.message.includes('请先登录')
      )
      
      // 如果是轮询接口的登录错误，只打印日志，不弹窗
      if (isPollingRequest && isLoginError) {
        console.warn('[轮询] 登录状态失效:', res.message)
        return Promise.reject(new Error(res.message || 'Error'))
      }
      
      // 其他错误正常弹窗
      alert(res.message || '操作失败')
      // 抛出错误，这样前端页面的 try-catch 就能捕获到，不会继续执行
      return Promise.reject(new Error(res.message || 'Error'))
    }

    // 如果成功，直接把整个数据包返回（或者只返回 res.data，看你个人习惯）
    // 这里建议返回 res，因为有时候前端页面也需要用到 message
    return res
  },
  error => {
    // 这里处理的是 HTTP 状态码错误 (比如 404, 500, 网络断开)
    console.error('API Error:', error)
    
    // 检查是否是轮询接口
    const isPollingRequest = error.config?.url && (
      error.config.url.includes('/chat/unread_total') || 
      error.config.url.includes('/chat/list')
    )
    
    // 检查是否是登录相关的错误
    const isLoginError = error.response?.data?.message && (
      error.response.data.message.includes('登录') || 
      error.response.data.message.includes('未登录') ||
      error.response.data.message.includes('请先登录')
    )
    
    // 如果是轮询接口的登录错误，只打印日志，不弹窗
    if (isPollingRequest && isLoginError) {
      console.warn('[轮询] 登录状态失效:', error.response?.data?.message)
      return Promise.reject(error)
    }
    
    // 只在非 404 错误时弹出提示（404 可能是前端路由，不应该弹提示）
    if (error.response?.status !== 404) {
      // 延迟弹出，避免阻塞页面渲染
      setTimeout(() => {
        alert(error.response?.data?.message || '网络连接失败')
      }, 100)
    }
    return Promise.reject(error)
  }
)

export default service