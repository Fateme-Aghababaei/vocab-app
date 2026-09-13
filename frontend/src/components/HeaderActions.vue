<template>
  <div class="flex shrink-0 items-center gap-1">
    <InstallApp />
    <NotificationButton />
    <ThemeToggle />
  </div>
</template>

<script setup lang="ts">
import ThemeToggle from "@/components/ThemeToggle.vue";
import InstallApp from "@/components/InstallApp.vue";
import NotificationButton from "@/components/NotificationButton.vue";
</script>
