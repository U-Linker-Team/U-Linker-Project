<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="header-back" @click="router.push('/admin')">
        <span class="iconify" data-icon="mdi:arrow-left"></span>
      </div>
      <span class="page-title">统计报表</span>
      <div style="width: 2rem;"></div>
    </header>

    <main class="page-content">
      <!-- 时间范围选择 -->
      <div class="stats-controls">
        <div class="control-group">
          <label>开始日期</label>
          <input 
            v-model="statsStartDate" 
            type="date" 
            class="date-input"
            @change="loadDailyStats"
          />
        </div>
        <div class="control-group">
          <label>结束日期</label>
          <input 
            v-model="statsEndDate" 
            type="date" 
            class="date-input"
            @change="loadDailyStats"
          />
        </div>
        <div class="control-group">
          <label>分组方式</label>
          <select v-model="statsGroupBy" @change="loadDailyStats" class="select-input">
            <option value="day">按天</option>
            <option value="week">按周</option>
            <option value="month">按月</option>
          </select>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="stats-actions">
        <button @click="loadDailyStats" class="action-btn refresh-btn">
          <span class="iconify" data-icon="mdi:refresh"></span>
          刷新数据
        </button>
        <button @click="exportStats" class="action-btn export-btn">
          <span class="iconify" data-icon="mdi:download"></span>
          导出Excel
        </button>
        <button @click="showCharts = !showCharts" class="action-btn chart-btn">
          <span class="iconify" data-icon="mdi:chart-line"></span>
          {{ showCharts ? '隐藏图表' : '显示图表' }}
        </button>
      </div>

      <!-- 统计摘要 -->
      <div v-if="dailyStats" class="stats-summary">
        <h3 class="summary-title">
          <span class="iconify" data-icon="mdi:chart-box"></span>
          统计摘要
        </h3>
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-label">新增用户总数</div>
            <div class="summary-value">{{ dailyStats.summary?.total_new_users || 0 }}</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">新增帖子总数</div>
            <div class="summary-value">{{ dailyStats.summary?.total_new_posts || 0 }}</div>
          </div>
          <div class="summary-card summary-card-active">
            <div class="summary-label">
              <span class="iconify" data-icon="mdi:account-clock"></span>
              活跃用户数
            </div>
            <div class="summary-value text-green-600">{{ dailyStats.summary?.active_users_last_7_days || 0 }}</div>
            <div class="summary-hint">最近7天有操作</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">新增悬赏任务</div>
            <div class="summary-value text-orange-600">{{ dailyStats.summary?.total_new_bounties || 0 }}</div>
          </div>
          <div class="summary-card">
            <div class="summary-label">新增服务任务</div>
            <div class="summary-value text-blue-600">{{ dailyStats.summary?.total_new_services || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- 详细统计数据表格 -->
      <div v-if="dailyStats" class="stats-table-section">
        <h3 class="table-title">
          <span class="iconify" data-icon="mdi:table"></span>
          详细统计数据
        </h3>
        <div class="table-wrapper">
          <table class="stats-table">
            <thead>
              <tr>
                <th>{{ statsGroupBy === 'day' ? '日期' : statsGroupBy === 'week' ? '周' : '月' }}</th>
                <th>新增用户</th>
                <th>新增帖子</th>
                <th>悬赏任务</th>
                <th>服务任务</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in dailyStats.daily_stats" :key="index">
                <td>{{ statsGroupBy === 'day' ? item.date : item.period }}</td>
                <td>{{ item.new_users }}</td>
                <td>{{ item.new_posts_total }}</td>
                <td class="text-orange-600">{{ item.new_bounties || 0 }}</td>
                <td class="text-blue-600">{{ item.new_services || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 图表区域 -->
      <div v-if="showCharts" class="charts-section">
        <h3 class="chart-title">
          <span class="iconify" data-icon="mdi:chart-line"></span>
          数据趋势图表
        </h3>
        <div class="chart-controls">
          <button 
            v-for="type in ['line', 'bar', 'pie']" 
            :key="type"
            @click="loadChart(type)"
            :class="['chart-type-btn', { active: chartType === type }]"
          >
            {{ type === 'line' ? '折线图' : type === 'bar' ? '柱状图' : '饼图' }}
          </button>
        </div>
        <div v-if="chartData" class="chart-container">
          <div class="chart-placeholder">
            <div class="chart-usage-tip">
              <span class="iconify" data-icon="mdi:information"></span>
              <div class="tip-content">
                <p class="tip-title">使用提示：</p>
                <p class="tip-text">
                  在 ECharts 编辑器中，请将下方数据赋值给 <code>option</code> 变量：
                </p>
                <p class="tip-code">option = <span class="code-placeholder">（下方 JSON 数据）</span>;</p>
                <p class="tip-note">💡 复制下方 JSON 数据，在 ECharts 编辑器中输入 <code>option = </code> 后粘贴即可</p>
              </div>
            </div>
            <p class="chart-hint">图表数据已加载，可使用 ECharts 等图表库渲染</p>
            <pre class="chart-data-preview">{{ JSON.stringify(chartData, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getStats, getDailyStats, exportStatsExcel, getStatsCharts } from '@/api/admin'

const router = useRouter()
const userStore = useUserStore()

if (!userStore.userInfo || !userStore.userInfo.is_admin) {
  alert('权限不足：需要管理员权限')
  router.push('/home')
}

const stats = ref({})
const dailyStats = ref(null)
const statsLoading = ref(false)
const statsStartDate = ref('')
const statsEndDate = ref('')
const statsGroupBy = ref('day')
const showCharts = ref(false)
const chartType = ref('line')
const chartData = ref(null)

const loadDailyStats = async () => {
  statsLoading.value = true
  try {
    const params = {
      group_by: statsGroupBy.value
    }
    if (statsStartDate.value) params.start_date = statsStartDate.value
    if (statsEndDate.value) params.end_date = statsEndDate.value
    
    const res = await getDailyStats(params)
    if (res.status === 'success') {
      dailyStats.value = res.data
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
    alert('获取统计数据失败：' + (e.response?.data?.message || e.message))
  } finally {
    statsLoading.value = false
  }
}

const exportStats = async () => {
  try {
    const params = {
      group_by: statsGroupBy.value
    }
    if (statsStartDate.value) params.start_date = statsStartDate.value
    if (statsEndDate.value) params.end_date = statsEndDate.value
    
    const response = await exportStatsExcel(params)
    const blob = response.data
    
    if (!(blob instanceof Blob) || blob.size === 0) {
      alert('导出失败：服务器返回的数据格式错误')
      return
    }
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const now = new Date()
    const timestamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`
    link.setAttribute('download', `系统统计报表_${timestamp}.xlsx`)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    alert('导出成功！文件已下载')
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败：' + (error.response?.data?.message || error.message || '未知错误'))
  }
}

const loadChart = async (type) => {
  chartType.value = type
  try {
    const res = await getStatsCharts({
      type: type,
      time_range: '7days'
    })
    if (res.status === 'success') {
      chartData.value = res.data.chart_data
    }
  } catch (e) {
    console.error('获取图表数据失败', e)
    alert('获取图表数据失败：' + (e.response?.data?.message || e.message))
  }
}

onMounted(async () => {
  // 获取基础统计信息
  try {
    const res = await getStats()
    if (res.status === 'success') {
      stats.value = res.data
    }
  } catch (e) {
    console.error('获取统计信息失败', e)
  }
  
  // 设置默认日期范围（最近30天）
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30)
  
  statsEndDate.value = endDate.toISOString().split('T')[0]
  statsStartDate.value = startDate.toISOString().split('T')[0]
  
  await loadDailyStats()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.page-header {
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-back {
  cursor: pointer;
  padding: 0.5rem;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.stats-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.date-input, .select-input {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.stats-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.export-btn {
  background: #3b82f6;
  color: white;
}

.chart-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.stats-summary {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-radius: 0.75rem;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: white;
  padding: 1rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.summary-card-active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
}

.summary-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.summary-hint {
  font-size: 0.625rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.stats-table-section {
  margin-bottom: 1.5rem;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.stats-table thead {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.stats-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.stats-table td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #1f2937;
  border-bottom: 1px solid #f3f4f6;
}

.stats-table tbody tr:hover {
  background: #f9fafb;
}

.charts-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.chart-controls {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.chart-type-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-type-btn.active {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.chart-container {
  min-height: 300px;
  padding: 2rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.chart-placeholder {
  text-align: center;
}

.chart-usage-tip {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 2px solid #3b82f6;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.chart-usage-tip .iconify {
  font-size: 1.5rem;
  color: #3b82f6;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-weight: 700;
  color: #1e40af;
  margin: 0 0 0.5rem 0;
  font-size: 0.9375rem;
}

.tip-text {
  color: #1e3a8a;
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

.tip-text code {
  background: rgba(59, 130, 246, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: #1e40af;
  font-weight: 600;
}

.tip-code {
  background: #1e293b;
  color: #e2e8f0;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  margin: 0.5rem 0 0 0;
  overflow-x: auto;
  white-space: pre;
  border: 1px solid #334155;
}

.code-placeholder {
  color: #94a3b8;
  font-style: italic;
}

.tip-note {
  color: #475569;
  font-size: 0.8125rem;
  margin: 0.75rem 0 0 0;
  line-height: 1.5;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tip-note code {
  background: rgba(59, 130, 246, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.8125rem;
  color: #1e40af;
  font-weight: 600;
}

.chart-hint {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.chart-data-preview {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  text-align: left;
  max-height: 400px;
  overflow: auto;
  border: 1px solid #e5e7eb;
}

.text-green-600 {
  color: #16a34a;
}

.text-orange-600 {
  color: #ea580c;
}

.text-blue-600 {
  color: #2563eb;
}
</style>

