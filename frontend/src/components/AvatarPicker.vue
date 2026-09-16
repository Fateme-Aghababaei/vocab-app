<template>
  <fieldset :disabled="disabled" class="min-w-0">
    <legend class="text-sm font-medium text-copy">
      Choose your avatar
    </legend>
    <p id="avatar-help" class="mt-1 text-xs text-quiet">
      Pick your space companion.
    </p>
    <div class="mt-4 grid grid-cols-4 gap-3" aria-describedby="avatar-help">
      <label
        v-for="option in AVATARS"
        :key="option.id"
        class="group relative cursor-pointer"
        :class="{ 'cursor-wait opacity-60': disabled }"
      >
        <input
          :checked="modelValue === option.id"
          :value="option.id"
          :disabled="disabled"
          type="radio"
          name="profile-avatar"
          class="peer sr-only"
          :aria-label="option.label"
          @change="emit('update:modelValue', option.id)"
        />
        <UserAvatar
          :avatar="option.id"
          :name="option.label"
          class="w-full ring-2 ring-transparent ring-offset-2 ring-offset-surface transition-shadow peer-checked:ring-accent peer-focus-visible:ring-accent group-hover:ring-accent-line"
        />
        <span v-if="modelValue === option.id" class="absolute bottom-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-on-primary" aria-hidden="true">
          <i class="pi pi-check text-[0.65rem]"></i>
        </span>
      </label>
    </div>
    <div class="mt-3 flex flex-wrap items-center justify-between gap-2">
      <p class="text-xs text-quiet" aria-live="polite">
        {{ selectedLabel }}
      </p>
      <button
        v-if="modelValue"
        type="button"
        :disabled="disabled"
        class="min-h-11 px-2 text-xs font-medium text-accent hover:text-accent-strong disabled:opacity-50"
        @click="emit('update:modelValue', '')"
      >
        Use my initial
      </button>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { computed } from "vue";
import UserAvatar from "@/components/UserAvatar.vue";
import { AVATARS } from "@/constants/avatars";
import type { AvatarId } from "@/constants/avatars";

const props = defineProps<{ modelValue: AvatarId | ""; disabled?: boolean }>();
const emit = defineEmits<{ "update:modelValue": [avatar: AvatarId | ""] }>();
const selectedLabel = computed(() => AVATARS.find((option) => option.id === props.modelValue)?.label ?? "Using your initial");
</script>
