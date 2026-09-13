<template>
  <div class="flex-1 bg-canvas flex items-center justify-center px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="flex flex-col items-center mb-8">
        <img src="/memento.png" alt="Memento" class="app-logo w-10 h-10 mb-3 shrink-0 object-contain" />
        <h1 class="font-display text-2xl font-semibold text-heading">
          Welcome back
        </h1>
        <p class="text-quiet text-sm mt-1">
          Log in to keep reviewing your words.
        </p>
      </div>

      <form class="rounded-xl2 bg-surface border border-line shadow-soft px-6 py-7 flex flex-col gap-4" @submit.prevent="handleSubmit">
        <div
          v-if="error"
          class="rounded-lg bg-accent-soft border border-accent-line text-accent-strong text-sm px-3 py-2"
        >
          {{ error }}
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-copy mb-1.5">Email</label>
          <InputText
            id="email"
            v-model="email"
            type="email"
            class="w-full"
            autocomplete="email"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-copy mb-1.5">Password</label>
          <Password
            id="password"
            v-model="password"
            class="w-full"
            input-class="w-full"
            :feedback="false"
            toggle-mask
            autocomplete="current-password"
            placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
          />
        </div>

        <button
          type="submit"
          class="mt-2 rounded-full bg-primary hover:bg-primary-hover disabled:bg-chart-neutral text-on-primary font-semibold py-2.5 transition-colors flex items-center justify-center gap-2"
          :disabled="loading || !email || !password"
        >
          <i v-if="loading" class="pi pi-spin pi-spinner"></i>
          Log in
        </button>
      </form>

      <p class="text-center text-sm text-quiet mt-5">
        New here?
        <router-link
          to="/signup"
          class="text-accent font-medium hover:text-accent-strong"
        >
          Create an account
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import { useAuthStore } from "@/stores/auth";
import { apiErrorMessage } from "@/services/api";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleSubmit() {
  if (!email.value || !password.value) return;
  loading.value = true;
  error.value = "";
  try {
    await auth.login(email.value, password.value);
    const next = typeof route.query.next === "string" ? route.query.next : "/";
    router.push(next);
  } catch (e) {
    error.value = apiErrorMessage(e);
  } finally {
    loading.value = false;
  }
}
</script>
