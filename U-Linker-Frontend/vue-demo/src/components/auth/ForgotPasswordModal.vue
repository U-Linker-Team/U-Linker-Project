<!-- 忘记密码 -->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>忘记密码</h3>
      <p>密码重置功能开发中...</p>
      <button @click="$emit('close')" class="close-btn">
        关闭
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['close'])
</script>