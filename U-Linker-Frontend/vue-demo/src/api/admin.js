import request from '@/utils/request'

// ================= 用户管理 =================

// 获取所有用户列表
export function getAllUsers(params) {
  return request.get('/admin/users', { params })
}

// 获取用户详情
export function getUserDetail(userId) {
  return request.get(`/admin/users/${userId}`)
}

// 根据学号获取用户全景记录（包括所有帖子）
export function getUserByStudentId(studentId) {
  return request.get(`/admin/users/by_student_id/${studentId}`)
}

// 管理用户积分
export function manageUserPoints(userId, data) {
  return request.post(`/admin/users/${userId}/points`, data)
}

// 封禁用户
export function banUser(userId, data) {
  return request.post(`/admin/users/${userId}/ban`, data)
}

// 解封用户
export function unbanUser(userId) {
  return request.post(`/admin/users/${userId}/unban`)
}

// ================= 帖子管理 =================

// 获取所有帖子
export function getAllPosts(params) {
  return request.get('/admin/posts', { params })
}

// ================= 订单管理 =================

// 获取所有订单
export function getAllOrders(params) {
  return request.get('/admin/orders', { params })
}

// ================= 积分管理 =================

// 获取所有积分流动记录
export function getAllPointsHistory(params) {
  return request.get('/admin/points/history', { params })
}

// ================= 统计信息 =================

// 获取系统统计信息
export function getStats() {
  return request.get('/admin/stats')
}

// 获取每日统计数据（5.4）
export function getDailyStats(params) {
  return request.get('/admin/stats/daily', { params })
}

// 导出统计数据为Excel（5.5）
export function exportStatsExcel(params) {
  return request.get('/admin/stats/export', {
    params,
    responseType: 'blob'
  })
}


// 获取统计数据图表数据（5.6）
export function getStatsCharts(params) {
  return request.get('/admin/stats/charts', { params })
}

// ================= 帖子导入导出 =================


// 导出帖子为 Excel
export function exportPostsExcel() {
  return request.get('/admin/posts/export', {
    responseType: 'blob'  // 重要：指定响应类型为blob，用于处理文件下载
  })
}


// 从 Excel 导入帖子
export function importPostsExcel(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/admin/posts/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

