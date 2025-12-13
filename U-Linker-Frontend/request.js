/**
 * Axios 请求封装
 * 统一处理请求/响应拦截、错误处理、Token管理
 */
import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '',  // 使用代理，不需要baseURL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    
    // 后端返回格式: { status: 'success'/'error', message: '...', data: {...} }
    if (res.status === 'success') {
      return res
    } else {
      // 业务错误
      console.warn('业务错误:', res.message)
      return Promise.reject(new Error(res.message || '操作失败'))
    }
  },
  error => {
    // 网络错误或HTTP错误
    console.error('响应错误:', error)
    
    let message = '网络错误，请稍后重试'
    
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          // 清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/'
          break
        case 403:
          message = '没有权限访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || '请求失败'
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查网络'
    }
    
    return Promise.reject(new Error(message))
  }
)

export default request
