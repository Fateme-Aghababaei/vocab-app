<template>
  <div class="flex flex-wrap items-center gap-1">
    <StreakBadge v-if="auth.isAuthenticated" />
    <InstallApp compact />
    <ThemeToggle />
  </div>
</template>

<script setup lang="ts">
import ThemeToggle from "@/components/ThemeToggle.vue";
import InstallApp from "@/components/InstallApp.vue";
import StreakBadge from "@/components/StreakBadge.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
</script>
