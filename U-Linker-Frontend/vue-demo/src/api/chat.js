import request from '@/utils/request'

export function getChatList(userId) {
  return request.get('/chat/list', { params: { user_id: userId } })
}

export function getHistory(sessionId) {
  return request.get('/chat/history', { params: { session_id: sessionId } })
}

export function sendMessage(data) {
  // 如果有文件，使用FormData上传
  if (data.file) {
    const formData = new FormData()
    formData.append('session_id', data.session_id)
    formData.append('file', data.file)
    if (data.content) {
      formData.append('content', data.content)
    }
    // 注意：不要手动设置 Content-Type，让浏览器自动生成 multipart boundary
    // 否则后端可能拿不到 request.files['file']
    return request.post('/chat/send', formData)
  } else {
    // 文本消息
    return request.post('/chat/send', data)
  }
}

export function createSession(data) {
  return request.post('/chat/create_session', data)
}

export function getPointsRules() {
  return request.get('/chat/points_rules')
}
