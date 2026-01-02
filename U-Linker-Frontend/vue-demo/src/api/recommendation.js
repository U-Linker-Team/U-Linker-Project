import request from '@/utils/request'

// 获取个性化推荐帖子
export function getRecommendations(params = {}) {
  return request.get('/recommendation/posts', { params })
}

// 记录用户浏览帖子
export function recordView(data) {
  return request.post('/recommendation/record_view', data)
}

