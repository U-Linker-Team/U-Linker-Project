/**
 * 学院选项常量
 * 用于注册、编辑资料等场景的学院选择
 */

export const COLLEGE_OPTIONS = [
  { value: 'maynooth', label: '梅努斯国际工程学院' },
  { value: 'electrical', label: '电气工程与自动化学院' },
  { value: 'mechanical', label: '机械工程与自动化学院' },
  { value: 'math', label: '数学与统计学院' },
  { value: 'petrochemical', label: '石油化工学院' },
  { value: 'civil', label: '土木工程学院' },
  { value: 'foreign', label: '外国语学院' },
  { value: 'economics', label: '经济与管理学院' },
  { value: 'mining', label: '紫金地质与矿业学院' },
  { value: 'architecture', label: '建筑与城乡规划学院' },
  { value: 'chemistry', label: '化学学院' },
  { value: 'material', label: '材料科学与工程学院' },
  { value: 'biology', label: '生物科学与工程学院' },
  { value: 'environment', label: '环境与安全学院' },
  { value: 'law', label: '法学院' },
  { value: 'computer', label: '计算机与大数据学院' },
  { value: 'physics', label: '物理与信息工程学院' },
  { value: 'humanities', label: '人文社会科学学院' }
]

/**
 * 根据学院值获取学院标签
 * @param {string} value - 学院值（如 'maynooth'）
 * @returns {string} 学院标签（如 '梅努斯国际工程学院'）或原始值
 */
export function getCollegeLabel(value) {
  if (!value) return '未设置学院'
  const college = COLLEGE_OPTIONS.find(item => item.value === value)
  return college ? college.label : value
}

/**
 * 根据学院标签获取学院值
 * @param {string} label - 学院标签（如 '梅努斯国际工程学院'）
 * @returns {string} 学院值（如 'maynooth'）或原始值
 */
export function getCollegeValue(label) {
  if (!label) return ''
  const college = COLLEGE_OPTIONS.find(item => item.label === label)
  return college ? college.value : label
}

