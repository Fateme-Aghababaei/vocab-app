<template>
  <div
    v-if="loading"
    class="rounded-xl2 content-panel border p-7"
    role="status"
    aria-live="polite"
    aria-busy="true"
  >
    <div class="flex items-center gap-4">
      <Skeleton shape="circle" size="5rem" />
      <div class="flex-1">
        <Skeleton width="60%" height="1.5rem" class="mb-3" />
        <Skeleton width="80%" />
      </div>
    </div>
    <Skeleton height="7rem" class="mt-6" />
    <p class="mt-5 text-center text-sm text-quiet">
      Loading your profile…
    </p>
  </div>

  <section v-else-if="loadError" class="rounded-xl2 content-panel border p-7 text-center">
    <h2 class="text-lg font-semibold">
      We couldn’t load your profile
    </h2>
    <p class="my-4 text-sm text-quiet" role="alert">
      {{ loadError }}
    </p>
    <Button label="Try again" icon="pi pi-refresh" @click="loadProfile" />
  </section>

  <div v-else-if="profile" class="flex flex-col gap-6">
    <section class="rounded-xl2 content-panel border p-5 sm:p-7" aria-labelledby="profile-name-heading">
      <div class="flex flex-col gap-5 sm:flex-row sm:items-center">
        <div class="relative h-20 w-20 shrink-0">
          <UserAvatar :avatar="profile.avatar" :name="profile.name" class="h-20 w-20 text-3xl ring-4 ring-accent-soft/50" />
          <button
            type="button"
            class="absolute -bottom-2 -right-2 flex h-11 w-11 items-center justify-center rounded-full border-4 border-surface bg-primary text-on-primary shadow-soft transition-colors hover:bg-primary-hover disabled:opacity-50"
            aria-label="Edit avatar"
            title="Edit avatar"
            aria-haspopup="dialog"
            :disabled="saving || avatarSaving || loggingOut"
            @click="avatarDialogVisible = true"
          >
            <i class="pi pi-pencil text-sm" aria-hidden="true"></i>
          </button>
        </div>
        <div class="min-w-0 flex-1">
          <h2 id="profile-name-heading" class="break-words text-2xl font-semibold" dir="auto">
            {{ profile.name || profile.email }}
          </h2>
          <p class="mt-1 break-all text-sm text-quiet">
            {{ profile.email }}
          </p>
          <div class="mt-3 flex flex-wrap items-center gap-2">
            <span class="rounded-full bg-accent-soft px-3 py-1.5 text-sm font-medium text-accent-strong">
              <span aria-hidden="true">🪐</span> Level {{ profile.level }}: <bdi>{{ profile.level_title }}</bdi>
            </span>
            <span class="rounded-full bg-warning-soft px-3 py-1.5 text-sm font-semibold text-warning-ink">
              ⭐ {{ profile.xp }} XP
            </span>
          </div>
          <div v-if="profile.level_progress" class="mt-4 max-w-md">
            <template v-if="profile.level_progress.next_planet">
              <p id="planet-progress-label" class="text-xs text-quiet">
                {{ profile.level_progress.xp_remaining }} XP to {{ profile.level_progress.next_planet }}
              </p>
              <div
                class="mt-2 h-2 overflow-hidden rounded-full bg-subtle"
                role="progressbar"
                aria-labelledby="planet-progress-label"
                :aria-valuenow="planetProgressPercentage"
                :aria-valuemin="0"
                :aria-valuemax="100"
              >
                <div class="h-full rounded-full bg-primary transition-[width] duration-500" :style="{ width: `${planetProgressPercentage}%` }"></div>
              </div>
              <p v-if="profile.xp === 0" class="mt-2 text-xs text-quiet">
                Your journey begins on {{ profile.level_title }}. Review your first word to earn XP.
              </p>
            </template>
            <p v-else class="text-sm font-medium text-accent-strong">
              <span aria-hidden="true">🌌</span> All eight planets reached. Keep exploring with every word.
            </p>
          </div>
        </div>
      </div>
      <div class="mt-6 grid gap-3 border-t border-line-soft pt-6 sm:grid-cols-2">
        <div class="rounded-2xl bg-warning-soft p-4">
          <p class="mb-1 text-xs font-medium text-warning-copy">
            Current streak
          </p>
          <p v-if="profile.streak_count > 0" class="text-xl font-semibold tabular-nums text-warning-ink">
            🔥 {{ profile.streak_count }} {{ profile.streak_count === 1 ? 'Day' : 'Days' }}
          </p>
          <template v-else>
            <p class="text-lg font-semibold text-warning-ink">
              Your next streak starts here
            </p>
            <p class="mt-2 text-sm text-warning-copy">
              Review a word today to start your streak.
            </p>
            <router-link to="/review" class="mt-2 inline-flex min-h-11 items-center text-sm font-semibold text-accent hover:text-accent-strong">
              Start reviewing <i class="pi pi-arrow-right ml-2 text-xs" aria-hidden="true"></i>
            </router-link>
          </template>
          <p class="mt-2 text-sm text-warning-copy">
            {{ profile.max_streak > 0 ? `🏆 Best Streak: ${profile.max_streak} ${profile.max_streak === 1 ? 'Day' : 'Days'}` : 'Your first streak will set your personal best.' }}
          </p>
        </div>
        <div class="rounded-2xl bg-accent-soft p-4">
          <p class="font-semibold text-accent-strong">
            ❄️ {{ profile.streak_freeze_count }} Freeze Available
          </p>
          <p class="mt-2 text-sm leading-relaxed text-copy">
            A freeze protects your streak for one missed day, so it won’t reset.
          </p>
          <p v-if="profile.streak_freeze_count === 0" class="mt-2 text-xs text-quiet">
            You have no freezes available right now.
          </p>
        </div>
      </div>
    </section>

    <div class="grid items-stretch gap-6 xl:grid-cols-2">
      <div class="flex min-w-0 flex-col gap-6">
        <section
          class="rounded-xl2 content-panel border p-5 sm:p-7"
          :class="{ 'progress-completed': profile.today_progress.is_completed }"
          aria-labelledby="progress-heading"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 id="progress-heading" class="text-lg font-semibold">
              Today’s progress
            </h2>
            <span v-if="profile.today_progress.is_completed" class="completion-label flex items-center gap-2 text-sm font-semibold" role="status">
              <i class="completion-check pi pi-check-circle" aria-hidden="true"></i>
              Goal completed!
            </span>
          </div>
          <p id="progress-description" class="mt-3 text-sm text-copy">
            {{ profile.today_progress.reviewed_today }} of {{ profile.today_progress.goal }} words reviewed today
          </p>
          <div class="mt-4 flex items-center gap-3">
            <div
              class="h-3 flex-1 overflow-hidden rounded-full bg-subtle"
              role="progressbar"
              aria-labelledby="progress-heading"
              aria-describedby="progress-description"
              :aria-valuenow="progressPercentage"
              :aria-valuemin="0"
              :aria-valuemax="100"
            >
              <div class="progress-fill h-full rounded-full bg-primary transition-[width] duration-500" :style="{ width: `${progressPercentage}%` }"></div>
            </div>
            <span class="text-sm font-semibold tabular-nums text-copy">{{ progressPercentage }}%</span>
          </div>
          <p class="mt-4 text-xs leading-relaxed text-quiet">
            {{ profile.today_progress.is_completed ? 'Your daily practice is done. Enjoy the progress you’ve made!' : 'Every word counts. Keep going toward your daily goal.' }}
          </p>
        </section>
        <WordUniverseCard :stats="profile.garden_stats" class="xl:flex-1" />
      </div>
      <ProfileSettingsForm
        v-if="settings"
        :settings="settings"
        :saving="saving || avatarSaving"
        @save="saveProfile"
      />
    </div>
  </div>

  <AvatarDialog
    v-if="profile"
    v-model:visible="avatarDialogVisible"
    :avatar="profile.avatar"
    :name="profile.name"
    :saving="avatarSaving"
    @save="saveAvatar"
  />

  <div class="mt-6 flex justify-end border-t border-line-soft pt-5">
    <Button
      :label="loggingOut ? 'Logging out…' : 'Log out'"
      icon="pi pi-sign-out"
      severity="secondary"
      outlined
      :loading="loggingOut"
      :disabled="loggingOut || saving || avatarSaving"
      class="w-full sm:w-auto"
      @click="handleLogout"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Skeleton from "primevue/skeleton";
import { useToast } from "primevue/usetoast";
import WordUniverseCard from "@/components/WordUniverseCard.vue";
import ProfileSettingsForm from "@/components/ProfileSettingsForm.vue";
import UserAvatar from "@/components/UserAvatar.vue";
import AvatarDialog from "@/components/AvatarDialog.vue";
import { api, apiErrorMessage } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import { useWordsStore } from "@/stores/words";
import type { StudySettings, UserProfile } from "@/types";
import type { AvatarId } from "@/constants/avatars";

const auth = useAuthStore();
const router = useRouter();
const words = useWordsStore();
const toast = useToast();
const loggingOut = ref(false);
const profile = ref<UserProfile | null>(null);
const settings = ref<StudySettings | null>(null);
const avatarDialogVisible = ref(false);
const avatarSaving = ref(false);
const loading = ref(true);
const loadError = ref("");
const saving = ref(false);
const progressPercentage = computed(() => Math.min(100, Math.max(0, profile.value?.today_progress.percentage ?? 0)));
const planetProgressPercentage = computed(() => Math.min(100, Math.max(0, profile.value?.level_progress?.percentage ?? 0)));

function applyProfile(updated: UserProfile, syncSettings = false) {
  profile.value = updated;
  if (syncSettings) {
    settings.value = {
      name: updated.name,
      daily_goal: updated.daily_goal,
      preferred_study_time: updated.preferred_study_time,
      notifications_enabled: updated.notifications_enabled,
    };
  }
  if (auth.user) {
    auth.user = { ...auth.user, name: updated.name, email: updated.email, streak_count: updated.streak_count, avatar: updated.avatar };
    auth.streakError = false;
  }
}

async function loadProfile() {
  loading.value = true;
  loadError.value = "";
  try {
    applyProfile(await api.getProfile(), true);
  } catch (error) {
    loadError.value = apiErrorMessage(error);
  } finally {
    loading.value = false;
  }
}

async function saveProfile(updatedSettings: StudySettings) {
  if (saving.value || avatarSaving.value || loggingOut.value) return;
  saving.value = true;
  try {
    applyProfile(await api.updateProfile(updatedSettings), true);
    toast.add({ severity: "success", summary: "Changes saved", detail: "Your profile settings have been updated.", life: 3500 });
  } catch (error) {
    toast.add({ severity: "error", summary: "Couldn’t save changes", detail: `${apiErrorMessage(error)} Your edits are kept. Please try again.`, life: 6000 });
  } finally {
    saving.value = false;
  }
}

async function saveAvatar(avatar: AvatarId | "") {
  if (avatarSaving.value || saving.value || loggingOut.value) return;
  avatarSaving.value = true;
  try {
    applyProfile(await api.updateProfile({ avatar }));
    avatarDialogVisible.value = false;
    toast.add({ severity: "success", summary: "Avatar updated", life: 3500 });
  } catch (error) {
    toast.add({ severity: "error", summary: "Couldn’t save avatar", detail: `${apiErrorMessage(error)} Please try again.`, life: 6000 });
  } finally {
    avatarSaving.value = false;
  }
}

async function handleLogout() {
  if (loggingOut.value || saving.value || avatarSaving.value) return;
  loggingOut.value = true;
  try {
    await auth.logout();
    words.$reset();
    await router.replace("/login");
  } finally {
    loggingOut.value = false;
  }
}

onMounted(loadProfile);
</script>

<style scoped>
.progress-completed {
  border-color: var(--p-green-500);
}
.completion-label {
  color: var(--p-green-700);
}
.progress-completed .progress-fill {
  background: var(--p-green-600);
}
:global([data-theme="dark"]) .completion-label {
  color: var(--p-green-400);
}
.completion-check {
  animation: check-appear 450ms ease-out;
}
@keyframes check-appear {
  from { opacity: 0; transform: scale(0.5); }
  to { opacity: 1; transform: scale(1); }
}
</style>
