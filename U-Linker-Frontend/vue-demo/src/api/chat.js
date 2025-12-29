import request from '@/utils/request'

export function getChatList(userId) {
  return request.get('/chat/list', { params: { user_id: userId } })
}

export function getHistory(sessionId) {
  return request.get('/chat/history', { params: { session_id: sessionId } })
}

export function sendMessage(data) {
  return request.post('/chat/send', data)
}

export function createSession(data) {
  return request.post('/chat/create_session', data)
}