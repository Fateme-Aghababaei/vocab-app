<template>
  <div class="mx-auto w-full max-w-6xl px-5 sm:px-8">
    <header class="flex items-center justify-between gap-4 py-6">
      <router-link to="/" class="flex items-center gap-2 font-display text-xl font-semibold text-heading" aria-label="Memento home">
        <img src="/memento.png" alt="" class="app-logo h-9 w-9 object-contain" />
        Memento
      </router-link>
      <nav aria-label="Main navigation" class="flex items-center gap-4 sm:gap-6">
        <a href="#how-it-works" class="hidden text-sm text-secondary hover:text-accent sm:block">How it works</a>
        <ThemeToggle />
        <router-link to="/login" class="text-sm font-semibold text-accent">
          Log in <span aria-hidden="true">↗</span>
        </router-link>
      </nav>
    </header>

    <main>
      <section class="grid items-center gap-12 py-14 sm:py-20 lg:grid-cols-2 lg:gap-16">
        <div>
          <p class="mb-5 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
            Your vocabulary, growing daily
          </p>
          <h1 class="text-5xl font-medium leading-[1.08] tracking-tight sm:text-6xl">
            Learn words<br />that <em class="text-accent">stick.</em>
          </h1>
          <p class="mt-6 max-w-md text-lg leading-relaxed text-secondary">
            Turn the English words you discover into words you remember. Build your own vocabulary library and keep it fresh with spaced repetition.
          </p>
          <div class="mt-8 flex flex-wrap items-center gap-4">
            <router-link :to="auth.isAuthenticated ? '/app' : '/signup'" class="inline-flex items-center gap-3 rounded-full bg-primary px-6 py-2 font-semibold text-on-primary transition-colors hover:bg-primary-hover">
              Start learning <span aria-hidden="true">→</span>
            </router-link>
            <InstallApp />
          </div>
          <p class="mt-4 text-xs text-quiet">
            Learn in your browser or install Memento on your device.
          </p>
        </div>

        <LandingFlashcards />
      </section>

      <section id="how-it-works" class="scroll-mt-6 border-t border-line py-14 sm:py-20">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-accent">
          A little every day
        </p>
        <h2 class="mt-3 text-3xl sm:text-4xl">
          Make new words part of your world.
        </h2>
        <div class="mt-10 grid gap-8 md:grid-cols-3">
          <article v-for="(feature, index) in features" :key="feature.title">
            <span class="font-display text-3xl text-accent">0{{ index + 1 }}</span>
            <h3 class="mt-4 text-xl font-semibold">
              {{ feature.title }}
            </h3>
            <p class="mt-3 text-sm leading-relaxed text-secondary">
              {{ feature.description }}
            </p>
          </article>
        </div>
      </section>

      <section class="glass-panel mb-10 rounded-3xl border px-6 py-10 text-center sm:p-12">
        <h2 class="text-3xl">
          Your next word is waiting.
        </h2>
        <p class="mx-auto mt-3 max-w-lg text-secondary">
          Save words from what you read, organize your collection, and come back for your daily flashcards.
        </p>
        <router-link :to="auth.isAuthenticated ? '/app' : '/signup'" class="mt-6 inline-flex rounded-full bg-primary px-6 py-3 font-semibold text-on-primary hover:bg-primary-hover">
          Start learning
        </router-link>
        <p class="mt-4 text-xs text-quiet">
          An internet connection is needed for your words and reviews.
        </p>
      </section>
    </main>

    <footer class="flex flex-row flex-wrap items-center justify-between gap-x-8 gap-y-6 border-t border-line py-8 sm:py-10">
      <div>
        <router-link to="/" class="inline-flex items-center gap-2 font-display text-lg font-semibold text-heading" aria-label="Memento home">
          <img src="/memento.png" alt="" class="app-logo h-7 w-7 object-contain" />
          Memento
        </router-link>
        <p class="mt-2 text-xs text-quiet">
          made with <span role="img" aria-label="love">❤️</span> by Memento team
        </p>
      </div>
      <nav aria-label="Footer navigation" class="flex flex-row flex-wrap gap-x-5 gap-y-3 text-sm text-secondary">
        <a href="#how-it-works" class="hover:text-accent">How it works</a>
        <router-link :to="auth.isAuthenticated ? '/app' : '/signup'" class="hover:text-accent">
          Start learning
        </router-link>
        <router-link to="/login" class="hover:text-accent">
          Log in
        </router-link>
      </nav>
      <nav v-if="contactLinks.length" aria-label="Contact Memento" class="flex flex-row flex-wrap items-center gap-2">
        <a
          v-for="contact in contactLinks"
          :key="contact.label"
          :href="contact.href"
          :target="contact.external ? '_blank' : undefined"
          :rel="contact.external ? 'noopener noreferrer' : undefined"
          :aria-label="contact.label + (contact.external ? ' (opens in a new tab)' : '')"
          :title="contact.label"
          class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-line text-secondary transition-colors hover:border-accent-line hover:text-accent"
        >
          <i :class="contact.icon" aria-hidden="true"></i>
        </a>
      </nav>
    </footer>
  </div>
</template>

<script setup lang="ts">
import LandingFlashcards from "@/components/LandingFlashcards.vue";
import InstallApp from "@/components/InstallApp.vue";
import ThemeToggle from "@/components/ThemeToggle.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const email = import.meta.env.VITE_CONTACT_EMAIL?.trim() || "hello@example.com";
const contactLinks = [
  ...(email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    ? [{ label: "Email us", icon: "pi pi-envelope", href: `mailto:${email}`, external: false }] : []),
  ...[
    { label: "Instagram", icon: "pi pi-instagram", url: import.meta.env.VITE_INSTAGRAM_URL || "https://example.com/instagram" },
    { label: "Telegram", icon: "pi pi-telegram", url: import.meta.env.VITE_TELEGRAM_URL || "https://example.com/telegram" },
    { label: "GitHub", icon: "pi pi-github", url: import.meta.env.VITE_GITHUB_URL || "https://example.com/github" },
  ].flatMap(({ label, icon, url }) => {
    try {
      const parsed = new URL(url);
      return parsed.protocol === "https:" ? [{ label, icon, href: parsed.href, external: true }] : [];
    } catch {
      return [];
    }
  }),
];
const features = [
  { title: "Capture your curiosity", description: "Add a word or find vocabulary in a passage. Use AI to draft definitions and examples, then make them your own." },
  { title: "Give every word a home", description: "Keep your vocabulary together in a personal library with categories, examples, and usage notes." },
  { title: "Remember for longer", description: "Review with flashcards on a schedule that adapts to how well you remember each word." },
];
</script>
