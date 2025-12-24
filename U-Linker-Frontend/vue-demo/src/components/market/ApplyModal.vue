<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-8">
      <div class="w-full bg-white rounded-2xl p-6 flex flex-col items-center text-center shadow-2xl animate-zoom-in">
        <h2 class="text-xl font-bold text-gray-900 mb-3">申请帮助</h2>
        <p class="text-sm text-gray-500 mb-4 truncate w-full">{{ taskTitle }}</p>
        
        <textarea 
          v-model="message"
          placeholder="说明一下你为什么适合这个任务..."
          class="w-full h-24 border border-gray-200 rounded-xl p-3 text-sm resize-none focus:outline-none focus:border-blue-400 mb-4 bg-white text-gray-900 placeholder-gray-400"
        ></textarea>
        
        <div class="w-full flex gap-4">
          <button @click="handleClose" 
            class="flex-1 bg-[#C7C7CC] text-white text-[17px] font-bold py-3 rounded-xl active:scale-95">
            取消
          </button>
          <button @click="handleSubmit" 
            class="flex-1 bg-[#007AFF] text-white text-[17px] font-bold py-3 rounded-xl shadow-md active:scale-95">
            提交申请
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  show: Boolean,
  taskTitle: String
})

const emit = defineEmits(['close', 'submit'])

const message = ref('')

const handleClose = () => {
  message.value = ''
  emit('close')
}

const handleSubmit = () => {
  emit('submit', message.value)
  message.value = ''
}
</script>

<style scoped>
.animate-zoom-in {
  animation: zoomIn 0.2s ease-out;
}
@keyframes zoomIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
