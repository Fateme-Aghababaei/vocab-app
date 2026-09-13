<template>
  <button
    type="button"
    class="header-action"
    :aria-pressed="isDark"
    aria-label="Dark mode"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggleTheme"
  >
    <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'" aria-hidden="true"></i>
  </button>
</template>

<script setup lang="ts">
import { isDark, toggleTheme } from "@/services/theme";
</script>
