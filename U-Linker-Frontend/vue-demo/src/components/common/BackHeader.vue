<template>
  <!-- 
    布局说明：
    h-14: 高度与 BottomNav 保持一致 (3.5rem)
    sticky top-0: 吸顶效果
    z-40: 层级比内容高，略高于 footer (z-30) 以免滚动穿透问题
  -->
  <header class="bg-white border-b border-gray-200 flex items-center justify-between px-4 h-14 sticky top-0 z-40 w-full flex-shrink-0">
    
    <!-- 左侧：返回按钮 -->
    <div class="w-10 flex justify-start">
      <button 
        @click="handleBack" 
        class="p-1 -ml-2 rounded-full active:bg-gray-100 transition-colors text-gray-600 hover:text-blue-600"
      >
        <Icon icon="mdi:chevron-left" class="w-8 h-8" />
      </button>
    </div>

    <!-- 中间：标题 -->
    <h1 class="flex-1 text-center text-lg font-bold text-gray-800 truncate">
      {{ title }}
    </h1>

    <!-- 右侧：插槽或占位符 -->
    <!-- 如果父组件传了 right 插槽，就显示；否则显示空 div 占位，保证标题居中 -->
    <div class="w-10 flex justify-end">
      <slot name="right"></slot>
    </div>
    
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

// 接收父组件传来的标题
const props = defineProps({
  title: {
    type: String,
    default: '标题'
  },
  // 可选：是否自定义返回逻辑（默认为 false，即自动返回上一页）
  customBack: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['back'])
const router = useRouter()

const handleBack = () => {
  if (props.customBack) {
    // 如果开启了自定义返回，触发事件让父组件处理
    emit('back')
  } else {
    // 默认行为：Vue Router 返回上一页
    router.back()
  }
}
</script>

<style scoped>
/* 防止 flex 布局在某些极端情况下被压缩 */
header {
  box-sizing: border-box;
}
</style>