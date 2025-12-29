import request from '@/utils/request'

// 1. 购买服务 (场景 A: Service Flow)
// 对应后端: POST /transaction/purchase
// 参数: { buyer_id, post_id }
export function purchaseService(data) {
  return request.post('/transaction/purchase', data)
}

// 2. 申请悬赏任务 (场景 B: Bounty Flow - 帮手发起)
// 对应后端: POST /transaction/apply
// 参数: { post_id, message }
export function applyTask(data) {
  // request 实例已经设置了 withCredentials: true，不需要重复设置
  return request.post('/transaction/apply', data)
}

// 3. 雇主选择帮手 (场景 B: Bounty Flow - 雇主确认)
// 对应后端: POST /transaction/select_helper
// 参数: { owner_id, post_id, helper_id }
export function selectHelper(data) {
  return request.post('/transaction/select_helper', data)
}

// 4. 确认订单完成 (通用接口)
// 对应后端: POST /transaction/confirm_complete
// 参数: { order_id, user_id }
export function confirmComplete(data) {
  return request.post('/transaction/confirm_complete', data)
}

// 5. 获取我参与的订单 (买家或卖家)
// 对应后端: GET /transaction/my_involved
// 参数: { user_id, page, page_size }
export function getMyInvolved(params) {
  return request.get('/transaction/my_involved', { params })
}

// 6. 获取积分变动历史
// 对应后端: GET /transaction/points/history
// 参数: { user_id, page, page_size }
export function getPointsHistory(params) {
  return request.get('/transaction/points/history', { params })
}

// 7. 手动创建订单 (备用接口)
// 对应后端: POST /transaction/create_order
// 参数: { buyer_id, seller_id, post_id, status? }
export function createOrder(data) {
  return request.post('/transaction/create_order', data)
}

// 8. 取消订单
// 对应后端: POST /transaction/cancel_order
// 参数: { order_id }
export function cancelOrder(data) {
  return request.post('/transaction/cancel_order', data)
}