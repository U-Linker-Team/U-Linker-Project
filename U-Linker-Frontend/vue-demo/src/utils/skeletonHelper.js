/**
 * 骨架图最小显示时间工具函数
 * 确保骨架图至少显示一段时间，提升用户体验
 * 
 * @param {Function} asyncFn - 异步函数（通常是 API 请求）
 * @param {number} minDisplayTime - 最小显示时间（毫秒），默认 300ms
 * @returns {Promise} 返回异步函数的结果
 * 
 * @example
 * const fetchData = async () => {
 *   loading.value = true
 *   try {
 *     const result = await ensureMinDisplayTime(
 *       () => getPostList({ page: 1 }),
 *       300
 *     )
 *     // 处理结果
 *   } finally {
 *     loading.value = false
 *   }
 * }
 */
export function ensureMinDisplayTime(asyncFn, minDisplayTime = 300) {
  const startTime = Date.now()
  
  return new Promise(async (resolve, reject) => {
    try {
      // 执行异步函数
      const result = await asyncFn()
      
      // 计算已经过去的时间
      const elapsedTime = Date.now() - startTime
      
      // 如果时间小于最小显示时间，则延迟
      if (elapsedTime < minDisplayTime) {
        const remainingTime = minDisplayTime - elapsedTime
        await new Promise(resolve => setTimeout(resolve, remainingTime))
      }
      
      resolve(result)
    } catch (error) {
      // 即使出错也要确保最小显示时间
      const elapsedTime = Date.now() - startTime
      if (elapsedTime < minDisplayTime) {
        const remainingTime = minDisplayTime - elapsedTime
        await new Promise(resolve => setTimeout(resolve, remainingTime))
      }
      reject(error)
    }
  })
}

