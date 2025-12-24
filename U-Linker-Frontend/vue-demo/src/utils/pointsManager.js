// 积分管理器
export const pointsManager = {
  // 获取当前积分
  getPoints() {
    const points = localStorage.getItem('userPoints')
    return points ? parseInt(points) : 350 // 默认350分
  },
  
  // 更新积分
  updatePoints(points) {
    localStorage.setItem('userPoints', points.toString())
    // 触发积分更新事件
    window.dispatchEvent(new CustomEvent('pointsUpdated', { detail: { points } }))
  },
  
  // 增加积分
  addPoints(amount) {
    const current = this.getPoints()
    const newPoints = current + amount
    this.updatePoints(newPoints)
    return newPoints
  },
  
  // 减少积分
  deductPoints(amount) {
    const current = this.getPoints()
    const newPoints = Math.max(0, current - amount) // 积分不为负
    this.updatePoints(newPoints)
    return newPoints
  }
}