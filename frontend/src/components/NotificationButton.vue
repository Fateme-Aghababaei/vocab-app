<template>
  <div class="border-t border-line pt-3">
    <button
      v-if="isSupported && permission === 'default'"
      type="button"
      class="inline-flex min-h-11 items-center justify-center gap-2 rounded-full border border-line-strong px-4 py-2 text-sm font-medium text-copy hover:bg-muted disabled:opacity-50"
      :disabled="enabling"
      @click="handleEnable"
    >
      <i :class="enabling ? 'pi pi-spinner pi-spin' : 'pi pi-bell'" aria-hidden="true"></i>
      {{ enabling ? 'Waiting for permission…' : 'Allow browser notifications' }}
    </button>
    <p class="mt-2 text-xs leading-relaxed text-quiet" role="status">
      {{ status }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useNotifications } from "@/composables/useNotifications";

const { isSupported, permission, requestPermission } = useNotifications();
const enabling = ref(false);
const attempted = ref(false);
const status = computed(() => {
  if (!isSupported) return "Browser notifications aren’t available here. On iPhone, install Memento on your home screen and open it there.";
  if (permission.value === "denied") return "Notifications are blocked on this device. Allow them in your browser’s site settings to receive reminders.";
  if (permission.value === "granted") return "Browser permission is granted on this device. Save your notification preference above to control reminders.";
  return attempted.value
    ? "Permission wasn’t granted. You can try again whenever you’re ready."
    : "Allow notifications on this device, then save your preference to receive reminders.";
});

function syncPermission() {
  if (isSupported) permission.value = Notification.permission;
}

async function handleEnable() {
  if (enabling.value) return;
  enabling.value = true;
  try {
    await requestPermission();
    attempted.value = true;
  } finally {
    enabling.value = false;
  }
}

onMounted(() => window.addEventListener("focus", syncPermission));
onUnmounted(() => window.removeEventListener("focus", syncPermission));
</script>
