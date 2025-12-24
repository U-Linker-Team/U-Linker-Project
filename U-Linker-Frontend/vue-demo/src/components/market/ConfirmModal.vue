<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-8">
      <div class="w-full bg-white rounded-2xl p-6 flex flex-col items-center text-center shadow-2xl animate-zoom-in">
        <h2 class="text-xl font-bold text-gray-900 mb-3 tracking-tight">确认验收?</h2>
        <p class="text-[15px] text-gray-600 leading-relaxed mb-8 px-2">
          确认后将解冻 <span class="font-bold text-gray-800">{{ points }}积分</span> 并转入对方账户，此操作不可撤销。
        </p>
        <div class="w-full flex gap-4">
          <button @click="$emit('close')" 
            class="flex-1 bg-[#C7C7CC] hover:bg-gray-400 text-white text-[17px] font-bold py-3 rounded-xl transition-colors active:scale-95">
            取消
          </button>
          <button @click="$emit('confirm')" 
            class="flex-1 bg-[#007AFF] hover:bg-blue-600 text-white text-[17px] font-bold py-3 rounded-xl shadow-md transition-colors active:scale-95">
            确认
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean,
  points: Number
})

defineEmits(['close', 'confirm'])
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
