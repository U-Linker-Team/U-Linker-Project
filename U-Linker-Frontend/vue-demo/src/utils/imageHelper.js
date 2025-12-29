/**
 * 图片 URL 处理工具
 * 用于处理后端返回的相对路径，转换为前端可访问的完整 URL
 */

// 后端地址（开发环境）
const BACKEND_URL = 'http://127.0.0.1:8000'

/**
 * 获取完整的图片 URL
 * @param {string} path - 后端返回的图片路径（相对路径或完整 URL）
 * @returns {string} - 完整的图片 URL
 */
export function getImageUrl(path) {
  if (!path) {
    return '' // 如果没有路径，返回空字符串
  }
  
  // 如果已经是完整 URL（http:// 或 https://），直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  
  // 如果是相对路径，拼接后端地址
  // 确保路径以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  
  // 使用 Vite 代理，直接返回相对路径（代理会自动转发）
  // 这样前端可以通过 /uploads/xxx.jpg 访问，Vite 会代理到后端
  return normalizedPath
}

/**
 * 获取头像 URL（带默认头像）
 * @param {string} avatarPath - 头像路径
 * @returns {string} - 头像 URL 或默认头像
 */
export function getAvatarUrl(avatarPath) {
  if (!avatarPath) {
    // 返回默认头像
    return 'https://via.placeholder.com/100?text=User'
  }
  
  return getImageUrl(avatarPath)
}

/**
 * 处理图片列表（用于帖子多图）
 * @param {string} imagesStr - 逗号分隔的图片路径字符串
 * @returns {Array<string>} - 处理后的图片 URL 数组
 */
export function getImageList(imagesStr) {
  if (!imagesStr) {
    return []
  }
  
  return imagesStr
    .split(',')
    .map(img => img.trim())
    .filter(img => img !== '')
    .map(img => getImageUrl(img))
}

