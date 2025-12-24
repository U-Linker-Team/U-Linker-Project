<template>
  <footer class="bg-white border-t border-gray-200 flex justify-around items-center h-14 z-30 flex-shrink-0 fixed bottom-0 left-0 right-0 w-full">
    <div 
      v-for="item in navItems" 
      :key="item.key"
      class="flex flex-col items-center justify-center w-full h-full cursor-pointer group"
      :class="{ 'text-blue-600': activeTab === item.key }"
      @click="handleNav(item.key)"
    >
      <Icon 
        :icon="activeTab === item.key ? item.activeIcon : item.icon" 
        class="w-6 h-6 transition-colors"
        :class="activeTab === item.key ? 'text-blue-600' : 'text-gray-400 group-hover:text-blue-600'"
      />
      <span 
        class="text-[10px] mt-0.5 transition-colors"
        :class="activeTab === item.key ? 'text-blue-600 font-bold' : 'text-gray-400 group-hover:text-blue-600'"
      >
        {{ item.label }}
      </span>
      
      <!-- 
        👇 修正点 1：直接使用 userStore.unreadCount 
        这样 App.vue 更新了 Store，这里就会自动变
      -->
      <span 
        v-if="item.key === 'message' && userStore.unreadCount > 0" 
        class="absolute top-1 right-8 w-2 h-2 bg-red-500 rounded-full"
      ></span>
    </div>
  </footer>
</template>

<script setup>
// import { ref } from 'vue' // 不需要 ref 了，因为数据在 store 里
import { Icon } from '@iconify/vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'home'
  }
})

const router = useRouter()
const userStore = useUserStore()

// 👇 修正点 2：删除了那行错误的 const 定义
// 我们直接用 userStore 实例即可

const navItems = [
  { key: 'home', label: '首页', icon: 'mdi:compass-outline', activeIcon: 'mdi:compass' },
  { key: 'market', label: '市场', icon: 'mdi:storefront-outline', activeIcon: 'mdi:storefront' }, 
  { key: 'message', label: '消息', icon: 'mdi:message-outline', activeIcon: 'mdi:message' },
  { key: 'profile', label: '我的', icon: 'mdi:account-outline', activeIcon: 'mdi:account' }
]

const handleNav = (key) => {
  switch (key) {
    case 'home':
      router.push('/home')
      break
    case 'market':
      router.push('/market') 
      break
    case 'message':
      router.push('/chat')
      break
    case 'profile':
      router.push('/profile')
      break
    default:
      console.warn('未知的导航:', key)
  }
}
</script>

<style scoped>
footer > div {
  position: relative;
  -webkit-tap-highlight-color: transparent; 
}
</style>