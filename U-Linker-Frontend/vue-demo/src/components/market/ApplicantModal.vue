<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-8">
      <div class="w-full bg-white rounded-2xl p-6 flex flex-col items-center text-center shadow-2xl animate-zoom-in">
        <h2 class="text-xl font-bold text-gray-900 mb-4 tracking-tight">选择帮助者</h2>
        
        <div class="w-full space-y-3 max-h-64 overflow-y-auto mb-4">
          <div v-for="applicant in applicants" :key="applicant.id" 
            @click="$emit('select', applicant)"
            class="bg-gray-50 rounded-xl p-3 flex items-center gap-3 cursor-pointer hover:bg-blue-50 transition-colors">
            <div class="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold flex-shrink-0">
              {{ applicant.avatar }}
            </div>
            <div class="flex-1 min-w-0 text-left">
              <div class="flex items-center gap-2">
                <span class="font-bold text-gray-800 text-sm">{{ applicant.name }}</span>
                <span class="text-xs text-gray-400">{{ applicant.college }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-1 truncate">{{ applicant.message }}</p>
            </div>
          </div>
        </div>
        
        <button @click="$emit('close')" 
          class="w-full bg-[#C7C7CC] text-white text-[17px] font-bold py-3 rounded-xl active:scale-95">
          取消
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean,
  applicants: Array
})

defineEmits(['close', 'select'])
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
