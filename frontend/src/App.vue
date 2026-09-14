<template>
  <div class="app-backdrop min-h-dvh text-body">
    <Toast position="top-right" />
    <ConfirmDialog />

    <div v-if="isPublicRoute" class="flex min-h-dvh flex-col pb-[max(0.5rem,env(safe-area-inset-bottom))]">
      <router-view />
      <AppFooter v-if="route.name !== 'landing'" />
    </div>

    <div v-else class="flex min-h-dvh">
      <aside
        class="app-sidebar hidden md:flex md:flex-col border border-line glass-panel"
      >
        <div class="flex items-center gap-2.5 px-2 mb-8">
          <img src="/memento.svg" alt="" class="app-logo w-8 h-8 shrink-0 object-contain" />
          <span class="font-display text-lg font-semibold text-heading">Memento</span>
        </div>

        <nav aria-label="Main navigation" class="flex flex-col gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="item.to"
            :aria-current="isActive(item.name) ? 'page' : undefined"
            class="group flex items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors"
            :class="
              isActive(item.name)
                ? 'bg-accent-soft text-accent-strong'
                : 'text-secondary hover:bg-subtle hover:text-heading'
            "
          >
            <span class="flex items-center gap-3">
              <i
                :class="[item.icon, isActive(item.name) ? 'text-accent' : 'text-faint']"
              ></i>
              {{ item.label }}
            </span>
            <span
              v-if="item.name === 'review' && dueBadge > 0"
              class="rounded-full bg-warning text-badge-ink text-xs font-semibold px-2 py-0.5 min-w-[1.5rem] text-center"
            >
              {{ dueBadge }}
            </span>
          </router-link>
        </nav>

        <div class="mt-auto flex flex-col gap-3">
          <p class="px-2 text-xs text-faint leading-relaxed">
            Save a word once, review it forever&nbsp;&mdash; a little every day.
          </p>
          <div class="flex items-center justify-between gap-2 rounded-xl border border-line px-3 py-2.5">
            <div class="min-w-0">
              <p class="text-sm font-medium text-body truncate">
                {{ auth.user?.name }}
              </p>
              <p class="text-xs text-faint truncate">
                {{ auth.user?.email }}
              </p>
            </div>
            <button
              type="button"
              class="shrink-0 text-faint hover:text-accent transition-colors p-1.5"
              aria-label="Log out"
              title="Log out"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out"></i>
            </button>
          </div>
        </div>
      </aside>

      <main class="app-main flex flex-1 min-w-0 flex-col">
        <header
          class="mobile-header fixed top-0 inset-x-0 z-40 flex min-h-16 items-center justify-between gap-3 border-b border-line glass-panel px-4 py-3 md:hidden sm:px-6"
        >
          <div class="flex min-w-0 items-center gap-2">
            <img src="/memento.svg" alt="" class="app-logo h-7 w-7 shrink-0 object-contain md:hidden" />
            <span class="font-display text-base font-semibold text-heading md:hidden">Memento</span>
          </div>
          <div class="flex shrink-0 items-center gap-1">
            <button
              type="button"
              class="header-action md:hidden"
              aria-label="Log out"
              title="Log out"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out" aria-hidden="true"></i>
            </button>
          </div>
        </header>
        <div class="app-content flex flex-1 flex-col w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-[calc(5.5rem+env(safe-area-inset-top))] md:pt-6 pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-2">
          <div class="flex-1 min-w-0">
            <header class="page-header mb-6">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <h1 class="text-2xl font-semibold">
                  {{ route.meta.title }}
                </h1>
                <HeaderActions />
              </div>
              <p v-if="route.meta.description" class="mt-1 text-quiet">
                {{ route.meta.description }}
              </p>
            </header>
            <router-view />
          </div>
          <AppFooter class="mt-2" />
        </div>
      </main>
    </div>

    <nav
      v-if="!isPublicRoute"
      aria-label="Main navigation"
      class="mobile-nav md:hidden fixed bottom-0 inset-x-0 glass-panel border-t border-line flex justify-around items-center py-2 px-2 z-40"
    >
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        :aria-current="isActive(item.name) ? 'page' : undefined"
        class="relative flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium"
        :class="isActive(item.name) ? 'text-accent' : 'text-faint'"
      >
        <i :class="item.icon" class="text-lg"></i>
        {{ item.label }}
        <span
          v-if="item.name === 'review' && dueBadge > 0"
          class="absolute -top-0.5 right-1 w-2 h-2 rounded-full bg-warning"
        ></span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import HeaderActions from "@/components/HeaderActions.vue";
import AppFooter from "@/components/AppFooter.vue";
import Toast from "primevue/toast";
import ConfirmDialog from "primevue/confirmdialog";
import { useWordsStore } from "@/stores/words";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const store = useWordsStore();
const auth = useAuthStore();

const navItems = [
  { name: "dashboard", label: "Today", icon: "pi pi-home", to: "/app" },
  { name: "review", label: "Review", icon: "pi pi-bolt", to: "/review" },
  { name: "library", label: "Library", icon: "pi pi-book", to: "/library" },
  { name: "add-word", label: "Add word", icon: "pi pi-plus", to: "/add" },
];

const isActive = (name: string) => route.name === name;
const dueBadge = computed(() => store.dueCount);
const isPublicRoute = computed(() => !!route.meta.public);

watch(
  () => auth.isAuthenticated,
  (authed) => {
    if (authed) store.fetchDueWords();
  },
  { immediate: true },
);

onMounted(() => {
  if (auth.isAuthenticated) store.fetchDueWords();
});

async function handleLogout() {
  await auth.logout();
  store.$reset();
  router.push("/login");
}
</script>
