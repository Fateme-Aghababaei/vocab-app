<script setup lang="ts">
import { ref } from 'vue';
import { useNotifications } from '@/composables/useNotifications';

const { isSupported, permission, requestPermission, sendTestNotification } = useNotifications();
const dismissed = ref(localStorage.getItem('vocab_notification_banner_dismissed') === 'true');

const handleEnable = async () => {
  const granted = await requestPermission();
  if (granted) {
    sendTestNotification();
  }
};

const handleDismiss = () => {
  dismissed.value = true;
  localStorage.setItem('vocab_notification_banner_dismissed', 'true');
};
</script>

<template>
  <div
    v-if="isSupported && permission !== 'granted' && !dismissed"
    class="rounded-xl2 border border-pink-100 bg-gradient-to-r from-pink-50/80 to-yellow-50/60 p-4 sm:p-5 shadow-soft flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all"
  >
    <div class="flex items-start gap-3.5">
      <div class="w-10 h-10 rounded-full bg-pink-500 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5 sm:mt-0">
        <i class="pi pi-bell text-lg"></i>
      </div>
      <div>
        <h3 class="font-display font-semibold text-stone-900 text-base sm:text-lg">
          Protect your memory & streak
        </h3>
        <p class="text-stone-600 text-sm mt-0.5">
          Get a gentle daily reminder only when cards are due for review. No spam, ever.
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2.5 shrink-0 self-end sm:self-center">
      <button
        type="button"
        class="text-xs sm:text-sm font-medium text-stone-500 hover:text-stone-800 px-3 py-2 rounded-lg transition-colors"
        @click="handleDismiss"
      >
        Maybe later
      </button>
      <button
        type="button"
        class="rounded-full bg-pink-500 hover:bg-pink-600 text-white text-xs sm:text-sm font-semibold px-4 py-2 shadow-sm transition-all active:scale-95 flex items-center gap-1.5"
        @click="handleEnable"
      >
        <span>Enable reminders</span>
        <i class="pi pi-check text-xs"></i>
      </button>
    </div>
  </div>
</template>