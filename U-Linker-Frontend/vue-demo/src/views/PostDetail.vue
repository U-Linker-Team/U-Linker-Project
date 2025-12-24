<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航 -->
    <div class="bg-white p-4 shadow-sm flex items-center sticky top-0 z-10">
      <button @click="$router.back()" class="text-gray-600 mr-4">
        <!-- 返回图标 -->
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
      </button>
      <span class="font-bold text-lg">详情</span>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="p-10 text-center text-gray-500">
      <div class="animate-spin inline-block w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
      <p>正在获取详情...</p>
    </div>

    <!-- 帖子内容 -->
    <div v-else-if="post" class="p-4 space-y-4">
      <div class="bg-white p-5 rounded-xl shadow-sm">
        <div class="flex justify-between items-start mb-4">
          <span 
            :class="`px-3 py-1 rounded-full text-xs font-bold ${post.post_type === 'bounty' ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`"
          >
            {{ post.post_type === 'bounty' ? '悬赏求助' : '服务出售' }}
          </span>
          <span class="text-2xl font-bold text-orange-500">{{ post.price }} <span class="text-sm text-gray-400">积分</span></span>
        </div>
        
        <h1 class="text-xl font-bold mb-2">{{ post.title }}</h1>
        
        <div class="flex items-center gap-2 mt-4 pb-4 border-b border-gray-100">
          <div class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden">
             <img v-if="post.author.avatar" :src="post.author.avatar" class="w-full h-full object-cover"/>
             <div v-else class="w-full h-full flex items-center justify-center bg-gray-300 text-white text-xl">👤</div>
          </div>
          <div>
            <div class="font-bold text-sm">{{ post.author.name }}</div>
            <div class="text-xs text-gray-400">{{ post.created_at }}</div>
          </div>
        </div>

        <div class="mt-4 text-gray-700 leading-relaxed whitespace-pre-wrap">
          {{ post.content }}
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="fixed bottom-0 left-0 right-0 p-4 bg-white border-t flex items-center gap-3 z-20">
        <button @click="handleChat" class="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-bold">
          私聊联系
        </button>

        <div v-if="isMine" class="flex-1 bg-gray-200 text-gray-500 py-3 rounded-lg font-bold text-center">
          我的发布
        </div>

        <template v-else>
          <button 
            v-if="post.post_type === 'bounty'"
            @click="handleApply"
            class="flex-[2] bg-blue-500 text-white py-3 rounded-lg font-bold shadow-lg active:scale-95 transition"
          >
            我来帮忙 (申请)
          </button>
          <button 
            v-else
            @click="handlePurchase"
            class="flex-[2] bg-green-500 text-white py-3 rounded-lg font-bold shadow-lg active:scale-95 transition"
          >
            立即购买
          </button>
        </template>
      </div>
    </div>
    
    <!-- 404 状态 -->
    <div v-else class="p-10 text-center text-gray-500">
      <p class="text-4xl mb-4">🏜️</p>
      <p>该帖子不存在或已被删除</p>
      <button @click="$router.push('/market')" class="mt-4 text-blue-500 underline">返回市场</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// 【更新】引入 getPostDetail
import { getPostDetail } from '@/api/market' 
import { purchaseService, applyTask } from '@/api/transaction'
import { createSession } from '@/api/chat'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref(null)
const loading = ref(true)

// 从 URL 获取 ID
const postId = parseInt(route.params.id)

// 判断是否是自己发布的
const isMine = computed(() => {
  return post.value && userStore.userInfo && post.value.author.id === userStore.userInfo.id
})

// 【核心修改】调用 API 获取详情
const fetchDetail = async () => {
  try {
    loading.value = true
    // 调用后端 /market/detail/<postId>
    const res = await getPostDetail(postId)
    
    // 适配后端返回值结构: res = { status: "success", data: post_object }
    if (res.status === 'success') {
      post.value = res.data
    } else {
      post.value = null
    }
  } catch (e) {
    console.error('获取详情失败:', e)
    post.value = null
  } finally {
    loading.value = false
  }
}

const handleChat = async () => {
  if (isMine.value) return alert('不能和自己聊天')
  try {
    const res = await createSession({
      my_id: userStore.userInfo.id,
      target_id: post.value.author.id
    })
    router.push(`/chat/${res.data.session_id}`)
  } catch (e) {}
}

const handleApply = async () => {
  if (!confirm('确定要申请帮忙吗？')) return
  try {
    await applyTask({
      applicant_id: userStore.userInfo.id,
      post_id: post.value.id
    })
    alert('申请成功！已通知发布者')
    router.push('/profile')
  } catch (e) {}
}

const handlePurchase = async () => {
  if (userStore.userInfo.points < post.value.price) return alert('积分不足')
  if (!confirm(`确定消耗 ${post.value.price} 积分购买吗？`)) return
  try {
    await purchaseService({
      post_id: post.value.id
    })
    
    // 刷新用户积分
    try {
      const userRes = await getUserProfile(userStore.userInfo.id)
      userStore.login(userRes.data)
    } catch (err) {
      console.error('刷新积分失败', err)
    }

    alert('购买成功！积分已扣除/冻结')
    router.push('/profile')
  } catch (e) {
    console.error('购买失败:', e)
    alert(e.message || '购买失败')
  }
}

onMounted(fetchDetail)
</script>