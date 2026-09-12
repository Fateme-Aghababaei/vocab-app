<template>
  <div class="min-h-screen bg-stone-50 flex items-center justify-center px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="flex flex-col items-center mb-8">
        <div
          class="w-10 h-10 rounded-xl bg-pink-500 flex items-center justify-center text-white font-display font-semibold text-lg mb-3"
        >
          V
        </div>
        <h1 class="font-display text-2xl font-semibold text-stone-900">
          Create your account
        </h1>
        <p class="text-stone-500 text-sm mt-1">
          Start building a vocabulary that sticks.
        </p>
      </div>

      <form class="rounded-xl2 bg-white border border-stone-200 shadow-soft px-6 py-7 flex flex-col gap-4" @submit.prevent="handleSubmit">
        <div
          v-if="error"
          class="rounded-lg bg-pink-50 border border-pink-200 text-pink-700 text-sm px-3 py-2"
        >
          {{ error }}
        </div>

        <div>
          <label
            for="name"
            class="block text-sm font-medium text-stone-700 mb-1.5"
          >Name <span class="text-stone-400 font-normal">(optional)</span></label>
          <InputText
            id="name"
            v-model="name"
            class="w-full"
            autocomplete="name"
            placeholder="Alex"
          />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-stone-700 mb-1.5">Email</label>
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
          <label for="password" class="block text-sm font-medium text-stone-700 mb-1.5">Password</label>
          <Password
            id="password"
            v-model="password"
            class="w-full"
            input-class="w-full"
            toggle-mask
            autocomplete="new-password"
            placeholder="At least 8 characters"
          />
        </div>

        <div>
          <label
            for="confirm-password"
            class="block text-sm font-medium text-stone-700 mb-1.5"
          >Confirm password</label>
          <Password
            id="confirm-password"
            v-model="confirmPassword"
            class="w-full"
            input-class="w-full"
            :feedback="false"
            toggle-mask
            autocomplete="new-password"
            placeholder="Type it again"
          />
          <p v-if="passwordsMismatch" class="text-xs text-pink-600 mt-1">
            Passwords don't match.
          </p>
        </div>

        <button
          type="submit"
          class="mt-2 rounded-full bg-pink-500 hover:bg-pink-600 disabled:bg-stone-300 text-white font-semibold py-2.5 transition-colors flex items-center justify-center gap-2"
          :disabled="loading || !canSubmit"
        >
          <i v-if="loading" class="pi pi-spin pi-spinner"></i>
          Create account
        </button>
      </form>

      <p class="text-center text-sm text-stone-500 mt-5">
        Already have an account?
        <router-link
          to="/login"
          class="text-pink-600 font-medium hover:text-pink-700"
        >
          Log in
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import { useAuthStore } from "@/stores/auth";
import { apiErrorMessage } from "@/services/api";

const router = useRouter();
const auth = useAuthStore();

const name = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");

const passwordsMismatch = computed(
  () => confirmPassword.value.length > 0 && password.value !== confirmPassword.value,
);

const canSubmit = computed(
  () => !!email.value && password.value.length >= 8 && !passwordsMismatch.value,
);

async function handleSubmit() {
  if (!canSubmit.value) return;
  loading.value = true;
  error.value = "";
  try {
    await auth.register(email.value, password.value, name.value);
    router.push("/");
  } catch (e) {
    error.value = apiErrorMessage(e);
  } finally {
    loading.value = false;
  }
}
</script>
