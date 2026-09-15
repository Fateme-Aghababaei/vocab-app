<template>
  <form class="flex flex-col rounded-xl2 content-panel border p-5 sm:p-7" :aria-busy="saving" @submit.prevent="submit">
    <h2 class="text-lg font-semibold">
      Settings
    </h2>
    <p class="mt-1 text-sm text-quiet">
      A little practice, at a time that works for you.
    </p>

    <fieldset :disabled="saving" class="my-6 grid min-w-0 gap-5 sm:grid-cols-2">
      <legend class="sr-only">
        Profile and study preferences
      </legend>
      <div class="sm:col-span-2">
        <label for="profile-name" class="mb-1.5 block text-sm font-medium text-copy">Name</label>
        <InputText
          id="profile-name"
          v-model="form.name"
          autocomplete="name"
          :maxlength="150"
          :disabled="saving"
          class="w-full"
        />
      </div>
      <div class="min-w-0">
        <label for="profile-goal" class="mb-1.5 block text-sm font-medium text-copy">Daily Goal</label>
        <Select
          v-model="form.daily_goal"
          input-id="profile-goal"
          :options="dailyGoals"
          option-label="label"
          option-value="value"
          :disabled="saving"
          class="w-full"
        />
      </div>
      <div class="min-w-0">
        <label for="profile-time" class="mb-1.5 block text-sm font-medium text-copy">Preferred Study Time</label>
        <InputText
          id="profile-time"
          v-model="form.preferred_study_time"
          type="time"
          step="1"
          :disabled="saving"
          class="w-full min-w-0"
        />
      </div>
      <div class="flex flex-wrap items-center justify-between gap-4 rounded-2xl bg-subtle p-4 sm:col-span-2">
        <div class="min-w-0 flex-1">
          <label for="profile-notifications" class="block text-sm font-medium text-copy">Notifications enabled</label>
          <p id="notifications-help" class="mt-1 text-xs text-quiet">
            Save your reminder preference. Browser notifications also need permission on this device.
          </p>
        </div>
        <ToggleSwitch
          v-model="form.notifications_enabled"
          input-id="profile-notifications"
          :disabled="saving"
          :pt="{ input: { 'aria-describedby': 'notifications-help' } }"
          class="shrink-0"
        />
        <NotificationButton v-if="form.notifications_enabled" class="w-full" />
      </div>
    </fieldset>

    <div class="mt-auto flex flex-col gap-3 border-t border-line-soft pt-5 sm:flex-row sm:items-center sm:justify-between">
      <p class="text-xs text-quiet">
        {{ hasChanges ? 'You have unsaved changes.' : 'Your preferences, your pace.' }}
      </p>
      <Button
        type="submit"
        :label="saving ? 'Saving…' : 'Save Changes'"
        :loading="saving"
        :disabled="saving || !hasChanges"
        class="w-full sm:w-auto"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import ToggleSwitch from "primevue/toggleswitch";
import NotificationButton from "@/components/NotificationButton.vue";
import type { StudySettings } from "@/types";

const props = defineProps<{
  settings: StudySettings;
  saving: boolean;
}>();
const emit = defineEmits<{ save: [settings: StudySettings] }>();
const dailyGoals = [5, 10, 15, 20].map((value) => ({ label: `${value} words`, value }));

function editableSettings(settings: StudySettings) {
  return {
    name: settings.name,
    daily_goal: settings.daily_goal,
    preferred_study_time: settings.preferred_study_time ?? "",
    notifications_enabled: settings.notifications_enabled,
  };
}

function normalizeTime(time: string | null) {
  if (!time) return null;
  return time.length === 5 ? `${time}:00` : time;
}

const form = reactive(editableSettings(props.settings));
watch(() => props.settings, (settings) => Object.assign(form, editableSettings(settings)));

const hasChanges = computed(() => (
  form.name !== props.settings.name
  || form.daily_goal !== props.settings.daily_goal
  || normalizeTime(form.preferred_study_time) !== normalizeTime(props.settings.preferred_study_time)
  || form.notifications_enabled !== props.settings.notifications_enabled
));

function submit() {
  if (props.saving || !hasChanges.value) return;
  emit("save", {
    ...editableSettings(form),
    name: form.name.trim(),
    preferred_study_time: normalizeTime(form.preferred_study_time),
  });
}
</script>
