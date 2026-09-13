<template>
  <button
    type="button"
    class="header-action"
    :disabled="enabling"
    :aria-label="label"
    :title="label"
    @click="handleEnable"
  >
    <i :class="enabling ? 'pi pi-spinner pi-spin' : permission === 'granted' && isSupported ? 'pi pi-bell-plus' : 'pi pi-bell'" aria-hidden="true"></i>
  </button>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useToast } from "primevue/usetoast";
import { useNotifications } from "@/composables/useNotifications";

const { isSupported, permission, requestPermission, sendTestNotification } = useNotifications();
const toast = useToast();
const enabling = ref(false);
const label = computed(() => isSupported && permission.value === "granted" ? "Notifications are on" : "Enable notifications");

async function handleEnable() {
  if (isSupported) permission.value = Notification.permission;
  if (!isSupported || permission.value === "denied" || permission.value === "granted") {
    toast.add({
      severity: "info",
      summary: "Notifications",
      detail: !isSupported
        ? "Notifications aren’t available in this browser. On iPhone, install Memento on your home screen and open it there."
        : permission.value === "denied"
          ? "Notifications are blocked. Allow them in your browser’s site settings to enable reminders."
          : "Notifications are enabled. You can change this in your browser’s site settings.",
      life: 6000,
    });
    return;
  }
  enabling.value = true;
  try {
    const granted = await requestPermission();
    toast.add({
      severity: granted ? "success" : "info",
      summary: granted ? "Notifications enabled" : "Notifications remain off",
      detail: granted ? "You’ll receive reminders when words are due for review." : "You can enable notifications later using this button or your browser’s site settings.",
      life: 5000,
    });
    if (granted) void sendTestNotification().catch(() => {});
  } finally {
    enabling.value = false;
  }
}
</script>
