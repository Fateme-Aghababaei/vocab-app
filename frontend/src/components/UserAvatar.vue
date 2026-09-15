<template>
  <span class="relative inline-flex aspect-square shrink-0 items-center justify-center overflow-hidden rounded-full bg-accent-soft font-semibold text-accent-strong" aria-hidden="true">
    <span v-if="!portrait || !loaded">{{ initial }}</span>
    <i v-if="!initial && (!portrait || !loaded)" class="pi pi-user"></i>
    <img
      v-if="portrait && !failed"
      :src="avatarImage(portrait.id)"
      alt=""
      class="pointer-events-none absolute inset-0 h-full w-full object-cover"
      :class="{ 'opacity-0': !loaded }"
      draggable="false"
      @load="loaded = true"
      @error="failed = true; loaded = false"
    />
  </span>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { AVATARS, avatarImage } from "@/constants/avatars";

const props = defineProps<{ avatar?: string; name?: string }>();
const loaded = ref(false);
const failed = ref(false);
const initial = computed(() => Array.from(props.name?.trim() ?? "")[0]?.toLocaleUpperCase() ?? "");
const portrait = computed(() => AVATARS.find((option) => option.id === props.avatar));
watch(() => props.avatar, () => {
  loaded.value = false;
  failed.value = false;
});
</script>
