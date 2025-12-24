<template>
  <Transition name="toast">
    <div 
      v-if="visible"
      class="absolute top-20 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-sm px-5 py-2.5 rounded-full shadow-xl z-50 flex items-center gap-2"
    >
      <Icon :icon="currentIcon" class="w-5 h-5" />
      <span>{{ currentText }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const visible = ref(false)
const currentText = ref('')
const currentIcon = ref('mdi:check-circle')

let timeout = null

const show = (text, icon = 'mdi:check-circle') => {
  if (timeout) {
    clearTimeout(timeout)
  }
  
  currentText.value = text
  currentIcon.value = icon
  visible.value = true
  
  timeout = setTimeout(() => {
    visible.value = false
  }, 2000)
}

defineExpose({ show })
</script>

<style scoped>
.toast-enter-active {
  animation: toastIn 0.3s ease-out forwards;
}

.toast-leave-active {
  animation: toastOut 0.25s ease-in forwards;
}

@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}

@keyframes toastOut {
  from { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  to { opacity: 0; transform: translateX(-50%) translateY(-10px) scale(0.95); }
}
</style>
