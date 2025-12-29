import request from '@/utils/request'

// 获取市场列表
export function getPostList(params) {
  return request.get('/market/list', { params })
}

// 发布帖子
export function addPost(data) {
  return request.post('/market/add', data)
}

// 【新增】获取帖子详情 - 对应后端 /market/detail/<int:post_id>
export function getPostDetail(postId) {
  return request.get(`/market/detail/${postId}`)
}

// 获取我发布的帖子
export function getMyPublished(params) {
  return request.get('/market/my_published', { params })
}

// 删除帖子（包含悬赏退款逻辑）
export function deletePost(data) {
  return request.post('/market/delete', data)
}