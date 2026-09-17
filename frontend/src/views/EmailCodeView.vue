<template>
  <div class="auth-page flex-1 flex items-center justify-center px-4 py-10">
    <div class="auth-card w-full max-w-sm">
      <router-link to="/login" class="auth-home text-sm text-secondary">
        <i class="pi pi-chevron-left" aria-hidden="true"></i> Back to login
      </router-link>
      <div class="flex flex-col items-center mb-8">
        <img src="/memento.svg" alt="Memento" class="app-logo w-10 h-10 mb-3 object-contain" />
        <h1 class="font-display text-2xl font-semibold text-heading">
          {{ isReset ? 'Reset password' : 'Confirm your email' }}
        </h1>
        <p class="text-quiet text-sm mt-1 text-center">
          {{ isReset ? 'Get a code by email to choose a new password.' : 'Enter the six-digit code from your email to finish signing up.' }}
        </p>
      </div>
      <form v-if="!complete" class="rounded-xl2 content-panel border px-6 py-7 flex flex-col gap-4" @submit.prevent="submit">
        <p v-if="error" role="alert" class="text-accent-strong text-sm">
          {{ error }}
        </p>
        <p v-if="message" role="status" class="text-copy text-sm">
          {{ message }}
        </p>
        <div v-if="!sent">
          <label for="email" class="block text-sm font-medium text-copy mb-1.5">Email</label>
          <InputText
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            class="w-full"
            required
            :disabled="loading"
            @update:model-value="code = ''; sent = false; message = ''; cooldown = 0"
          />
        </div>
        <template v-if="sent">
          <div>
            <label for="code" class="block text-sm font-medium text-copy mb-1.5">Email code</label>
            <InputText
              id="code"
              v-model="code"
              inputmode="numeric"
              autocomplete="one-time-code"
              pattern="[0-9]{6}"
              maxlength="6"
              class="w-full"
              required
            />
            <p class="text-xs text-quiet mt-1">
              Codes expire after 10 minutes. Check your spam folder too.
            </p>
          </div>
          <template v-if="isReset">
            <div>
              <label for="new-password" class="block text-sm font-medium text-copy mb-1.5">New password</label>
              <Password
                v-model="password"
                input-id="new-password"
                autocomplete="new-password"
                toggle-mask
                class="w-full"
                input-class="w-full"
                placeholder="At least 8 characters"
              />
            </div>
            <div>
              <label for="confirm-password" class="block text-sm font-medium text-copy mb-1.5">Confirm password</label>
              <Password
                v-model="confirmation"
                input-id="confirm-password"
                autocomplete="new-password"
                toggle-mask
                :feedback="false"
                class="w-full"
                input-class="w-full"
              />
            </div>
          </template>
        </template>
        <button type="submit" class="rounded-full glass-primary glass-control text-on-primary font-semibold py-2.5 disabled:opacity-50" :disabled="loading || !email || (sent && !canConfirm)">
          {{ loading ? 'Please wait…' : !sent ? 'Send code' : isReset ? 'Update password' : 'Confirm email' }}
        </button>
        <button
          v-if="sent"
          type="button"
          class="text-sm text-accent disabled:opacity-50"
          :disabled="loading || cooldown > 0"
          @click="send"
        >
          {{ cooldown > 0 ? `Resend code in ${cooldown}s` : 'Resend code' }}
        </button>
      </form>
      <div v-else class="rounded-xl2 content-panel border px-6 py-7 text-center">
        <p role="status" class="text-copy mb-4">
          Your password has been updated.
        </p>
        <router-link to="/login" class="text-accent font-medium">
          Log in with your new password
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import { api, apiErrorMessage } from "@/services/api";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const isReset = computed(() => route.name === "forgot-password");
const email = ref(typeof route.query.email === "string" ? route.query.email : "");
const sent = ref(!isReset.value && !!email.value);
const code = ref("");
const password = ref("");
const confirmation = ref("");
const loading = ref(false);
const complete = ref(false);
const error = ref("");
const message = ref(sent.value ? "We sent a verification code to your email." : "");
const cooldown = ref(sent.value ? 60 : 0);
const timer = window.setInterval(() => { if (cooldown.value > 0) cooldown.value--; }, 1000);
onUnmounted(() => window.clearInterval(timer));
const canConfirm = computed(() => /^[0-9]{6}$/.test(code.value) && (!isReset.value || (password.value.length >= 8 && password.value === confirmation.value)));

async function send() {
  if (loading.value || !email.value || cooldown.value > 0) return;
  loading.value = true;
  error.value = "";
  try {
    const result = await api.sendEmailCode(email.value, isReset.value);
    message.value = result.detail;
    sent.value = true;
    code.value = "";
    cooldown.value = 60;
  } catch (err) {
    error.value = apiErrorMessage(err);
  } finally {
    loading.value = false;
  }
}

async function submit() {
  if (!sent.value) return send();
  if (loading.value || !canConfirm.value) return;
  loading.value = true;
  error.value = "";
  try {
    if (isReset.value) {
      await api.resetPassword(email.value, code.value, password.value);
      password.value = "";
      confirmation.value = "";
      complete.value = true;
    } else {
      await auth.verifyEmail(email.value, code.value);
      await router.push("/app");
    }
  } catch (err) {
    error.value = apiErrorMessage(err);
  } finally {
    loading.value = false;
  }
}
</script>
