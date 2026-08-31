<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="t in toasts" :key="t.id" :class="['toast', t.type]">
          <span class="toast-icon">{{ t.type === 'error' ? '⚠️' : t.type === 'success' ? '✅' : 'ℹ️' }}</span>
          <span>{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '../stores/toast'
import { storeToRefs } from 'pinia'
const store = useToastStore()
const { toasts } = storeToRefs(store)
</script>

<style scoped>
.toast-container {
  position: fixed; top: 80px; right: 24px; z-index: 9999;
  display: flex; flex-direction: column; gap: 10px; pointer-events: none;
}
.toast {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 20px; border-radius: 12px;
  font-size: 14px; font-weight: 500;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  pointer-events: auto; min-width: 240px; max-width: 380px;
}
.toast.error {
  background: #FFF5F5; border: 1.5px solid #FED7D7; color: #C53030;
}
.toast.success {
  background: #F0FFF4; border: 1.5px solid #C6F6D5; color: #276749;
}
.toast.info {
  background: #EBF8FF; border: 1.5px solid #BEE3F8; color: #2A69AC;
}
.toast-icon { font-size: 16px; }
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { opacity: 0; transform: translateX(60px); }
.toast-leave-to { opacity: 0; transform: translateX(60px); }
</style>
