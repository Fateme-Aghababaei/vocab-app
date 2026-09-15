<template>
  <Dialog
    :visible="visible"
    modal
    header="Edit avatar"
    class="mx-4 w-full max-w-sm"
    :draggable="false"
    :closable="false"
    :close-on-escape="!saving"
    :dismissable-mask="!saving"
    :aria-busy="saving"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="mb-6 flex justify-center">
      <UserAvatar :avatar="selected" :name="name" class="h-20 w-20 text-3xl ring-4 ring-accent-soft/50" />
    </div>
    <AvatarPicker v-model="selected" :disabled="saving" />
    <template #footer>
      <Button
        label="Cancel"
        severity="secondary"
        text
        :disabled="saving"
        @click="emit('update:visible', false)"
      />
      <Button
        :label="saving ? 'Saving…' : 'Save avatar'"
        :loading="saving"
        :disabled="saving || selected === (avatar ?? '')"
        @click="save"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import AvatarPicker from "@/components/AvatarPicker.vue";
import UserAvatar from "@/components/UserAvatar.vue";
import type { AvatarId } from "@/constants/avatars";

const props = defineProps<{
  visible: boolean;
  avatar?: AvatarId | "";
  name: string;
  saving: boolean;
}>();
const emit = defineEmits<{
  "update:visible": [visible: boolean];
  save: [avatar: AvatarId | ""];
}>();
const selected = ref<AvatarId | "">(props.avatar ?? "");

watch(() => props.visible, (visible) => {
  if (visible) selected.value = props.avatar ?? "";
});

function save() {
  if (props.saving || selected.value === (props.avatar ?? "")) return;
  emit("save", selected.value);
}
</script>
