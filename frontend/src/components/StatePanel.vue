<template>
  <section
    class="flex flex-col items-center gap-3 text-center"
    :class="compact ? 'py-5' : 'rounded-xl2 content-panel border px-6 py-10 sm:py-14'"
    :aria-busy="kind === 'loading'"
  >
    <span class="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent" aria-hidden="true">
      <i :class="kind === 'loading' ? 'pi pi-spinner pi-spin' : kind === 'error' ? 'pi pi-exclamation-circle' : 'pi pi-sparkles'" class="text-xl"></i>
    </span>
    <div :role="kind === 'error' ? 'alert' : 'status'">
      <h2 class="font-semibold text-heading" :class="compact ? 'text-base' : 'text-xl'">
        {{ title }}
      </h2>
      <p v-if="description" class="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-quiet">
        {{ description }}
      </p>
    </div>
    <router-link
      v-if="actionLabel && to"
      :to="to"
      class="mt-2 inline-flex min-h-11 items-center justify-center rounded-full bg-primary px-5 py-2 text-sm font-semibold text-on-primary hover:bg-primary-hover"
    >
      {{ actionLabel }}
    </router-link>
    <Button
      v-else-if="actionLabel"
      :label="actionLabel"
      class="mt-2"
      @click="$emit('action')"
    />
    <slot></slot>
  </section>
</template>

<script setup lang="ts">
import Button from "primevue/button";
withDefaults(defineProps<{
  title: string;
  description?: string;
  kind?: "empty" | "loading" | "error";
  actionLabel?: string;
  to?: string;
  compact?: boolean;
}>(), { kind: "empty", description: "", actionLabel: "", to: "", compact: false });
defineEmits<{ action: [] }>();
</script>
