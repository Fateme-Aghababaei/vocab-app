<template>
  <div class="min-h-screen bg-stone-50 text-stone-800">
    <Toast position="top-right" />
    <ConfirmDialog />

    <template v-if="isPublicRoute">
      <router-view />
      <AppFooter />
    </template>

    <div v-else class="flex min-h-screen">
      <aside
        class="hidden md:sticky md:top-0 md:flex md:h-dvh md:self-start md:flex-col md:w-64 md:shrink-0 border-r border-stone-200 bg-white px-5 py-6"
      >
        <div class="flex items-center gap-2.5 px-2 mb-8">
          <img src="/memento.png" alt="" class="w-8 h-8 shrink-0 object-contain" />
          <span class="font-display text-lg font-semibold text-stone-900">Memento</span>
        </div>

        <nav class="flex flex-col gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="item.to"
            class="group flex items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors"
            :class="
              isActive(item.name)
                ? 'bg-pink-50 text-pink-700'
                : 'text-stone-600 hover:bg-stone-100 hover:text-stone-900'
            "
          >
            <span class="flex items-center gap-3">
              <i
                :class="[item.icon, isActive(item.name) ? 'text-pink-600' : 'text-stone-400']"
              ></i>
              {{ item.label }}
            </span>
            <span
              v-if="item.name === 'review' && dueBadge > 0"
              class="rounded-full bg-yellow-400 text-stone-900 text-xs font-semibold px-2 py-0.5 min-w-[1.5rem] text-center"
            >
              {{ dueBadge }}
            </span>
          </router-link>
        </nav>

        <div class="mt-auto flex flex-col gap-3">
          <p class="px-2 text-xs text-stone-400 leading-relaxed">
            Save a word once, review it forever&nbsp;&mdash; a little every day.
          </p>
          <div class="flex items-center justify-between gap-2 rounded-xl border border-stone-200 px-3 py-2.5">
            <div class="min-w-0">
              <p class="text-sm font-medium text-stone-800 truncate">
                {{ auth.user?.name }}
              </p>
              <p class="text-xs text-stone-400 truncate">
                {{ auth.user?.email }}
              </p>
            </div>
            <button
              type="button"
              class="shrink-0 text-stone-400 hover:text-pink-600 transition-colors p-1.5"
              aria-label="Log out"
              title="Log out"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out"></i>
            </button>
          </div>
        </div>
      </aside>

      <header
        class="mobile-header md:hidden fixed top-0 inset-x-0 z-40 flex items-center justify-between bg-white border-b border-stone-200 px-4 py-3"
      >
        <div class="flex items-center gap-2">
          <img src="/memento.png" alt="" class="w-7 h-7 shrink-0 object-contain" />
          <span class="font-display text-base font-semibold text-stone-900">Memento</span>
        </div>
        <button
          type="button"
          class="text-stone-400 hover:text-pink-600 transition-colors p-1.5"
          aria-label="Log out"
          @click="handleLogout"
        >
          <i class="pi pi-sign-out"></i>
        </button>
      </header>

      <main class="flex-1 min-w-0">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-[calc(4rem+env(safe-area-inset-top))] md:pt-6 pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-2">
          <InstallApp />
          <router-view />
          <AppFooter class="mt-2" />
        </div>
      </main>
    </div>

    <nav
      v-if="!isPublicRoute"
      class="mobile-nav md:hidden fixed bottom-0 inset-x-0 bg-white border-t border-stone-200 flex justify-around items-center py-2 px-2 z-40"
    >
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        class="relative flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium"
        :class="isActive(item.name) ? 'text-pink-600' : 'text-stone-400'"
      >
        <i :class="item.icon" class="text-lg"></i>
        {{ item.label }}
        <span
          v-if="item.name === 'review' && dueBadge > 0"
          class="absolute -top-0.5 right-1 w-2 h-2 rounded-full bg-yellow-400"
        ></span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import InstallApp from "@/components/InstallApp.vue";
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
  { name: "dashboard", label: "Dashboard", icon: "pi pi-home", to: "/" },
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
