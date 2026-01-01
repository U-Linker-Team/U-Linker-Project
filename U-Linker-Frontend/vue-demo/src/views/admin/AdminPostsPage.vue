<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="header-back" @click="router.push('/admin')">
        <span class="iconify" data-icon="mdi:arrow-left"></span>
      </div>
      <span class="page-title">帖子管理</span>
      <div style="width: 2rem;"></div>
    </header>

    <main class="page-content">
      <div class="search-bar">
        <input 
          v-model="postSearchKeyword"
          @input="searchPosts"
          type="text" 
          placeholder="搜索帖子（标题、内容、作者）"
          class="search-input"
        />
      </div>
      
      <!-- 导入导出按钮 -->
      <div class="action-buttons">
        <button @click="exportPosts" class="action-btn export-btn">
          <span class="iconify" data-icon="mdi:download"></span>
          导出帖子数据
        </button>
        <label class="action-btn import-btn">
          <input 
            type="file" 
            accept=".xlsx,.xls" 
            @change="handleFileImport" 
            style="display: none"
          />
          <span class="iconify" data-icon="mdi:upload"></span>
          导入帖子数据
        </label>
      </div>
      
      <div class="table-container">
        <div v-if="postsLoading" class="loading">加载中...</div>
        <div v-else-if="postsList.length === 0" class="empty">暂无帖子</div>
        <div v-else class="post-list">
          <div 
            v-for="post in postsList" 
            :key="post.id"
            class="post-item"
          >
            <div class="post-title">{{ post.title }}</div>
            <div class="post-meta">
              {{ post.author?.name || '未知用户' }} · 
              {{ post.post_type === 'bounty' ? '悬赏' : '服务' }} · 
              {{ post.status === 'active' ? '招募中' : post.status === 'trading' ? '进行中' : post.status === 'sold' ? '已完成' : '已下架' }}
            </div>
            <div class="post-price">{{ post.price }} 积分</div>
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
import { getAllPosts, exportPostsExcel, importPostsExcel } from '@/api/admin'

const router = useRouter()
const userStore = useUserStore()

if (!userStore.userInfo || !userStore.userInfo.is_admin) {
  alert('权限不足：需要管理员权限')
  router.push('/home')
}

const postsList = ref([])
const postsLoading = ref(false)
const postSearchKeyword = ref('')

const searchPosts = async () => {
  postsLoading.value = true
  try {
    const res = await getAllPosts({
      keyword: postSearchKeyword.value,
      page: 1,
      page_size: 100
    })
    if (res.status === 'success') {
      postsList.value = res.data.items
    }
  } catch (e) {
    console.error('获取帖子列表失败', e)
  } finally {
    postsLoading.value = false
  }
}

const exportPosts = async () => {
  try {
    const response = await exportPostsExcel()
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
    link.setAttribute('download', `帖子数据报表_${timestamp}.xlsx`)
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

const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    alert('只支持 Excel 文件 (.xlsx, .xls)')
    return
  }
  
  if (!confirm(`确定要导入文件 "${file.name}" 吗？\n\n注意：\n1. Excel 文件必须包含以下列：标题、内容、价格(积分)、类型、作者用户名\n2. 类型必须是"悬赏"或"服务"\n3. 悬赏任务会自动扣除作者积分`)) {
    event.target.value = ''
    return
  }
  
  try {
    const res = await importPostsExcel(file)
    if (res.status === 'success') {
      const data = res.data
      let message = `导入完成！\n成功：${data.success_count} 条\n失败：${data.error_count} 条`
      
      if (data.errors && data.errors.length > 0) {
        message += '\n\n错误详情：\n' + data.errors.slice(0, 5).join('\n')
        if (data.errors.length > 5) {
          message += `\n... 还有 ${data.errors.length - 5} 个错误`
        }
      }
      
      alert(message)
      
      if (data.success_count > 0) {
        await searchPosts()
      }
    } else {
      alert(res.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    alert('导入失败：' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    event.target.value = ''
  }
}

onMounted(() => {
  searchPosts()
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

.search-bar {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
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

.export-btn {
  background: #3b82f6;
  color: white;
}

.import-btn {
  background: #10b981;
  color: white;
  cursor: pointer;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.post-item {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.post-title {
  font-weight: 600;
  color: #1f2937;
}

.post-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.post-price {
  font-weight: 600;
  color: #3b82f6;
}
</style>

