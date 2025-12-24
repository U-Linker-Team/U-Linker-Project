import request from '@/utils/request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function logout() {
  return request.get('/auth/logout')
}

export function getUserProfile(userId) {
  return request.get('/auth/profile', {
    params: {
      user_id: userId
    }
  })
}

export function updateProfile(formData) {
  return request.post('/auth/update_profile', formData, {
    headers: {
      'Content-Type': 'multipart/form-data' // 明确告诉后端这是文件上传
    }
  })
}