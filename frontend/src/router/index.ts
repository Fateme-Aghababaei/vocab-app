import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "landing",
      component: () => import("@/views/LandingView.vue"),
      meta: { public: true },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { public: true },
    },
    {
      path: "/signup",
      name: "signup",
      component: () => import("@/views/SignupView.vue"),
      meta: { public: true },
    },
    {
      path: "/app",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue"),
      meta: { title: "Good to see you", description: "Here’s what your vocabulary practice looks like today." },
    },
    {
      path: "/review",
      name: "review",
      component: () => import("@/views/ReviewView.vue"),
      meta: { title: "Review", description: "" },
    },
    {
      path: "/library",
      name: "library",
      component: () => import("@/views/LibraryView.vue"),
      meta: { title: "Library", description: "Browse, search, and fine-tune everything you’ve saved." },
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("@/views/ProfileView.vue"),
      meta: { title: "Your profile", description: "Explore your word universe and make your practice your own." },
    },
    {
      path: "/add",
      name: "add-word",
      component: () => import("@/views/AddWordView.vue"),
      meta: { title: "Add Vocabulary", description: "Look up a single word or extract key vocabulary from real-world text." },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (!auth.initialized) {
    await auth.init();
  }

  const isPublic = !!to.meta.public;

  if (!isPublic && !auth.isAuthenticated) {
    return { name: "login", query: to.fullPath !== "/" ? { next: to.fullPath } : undefined };
  }

  if (isPublic && to.name !== "landing" && auth.isAuthenticated) {
    return { name: "dashboard" };
  }

  return true;
});

router.afterEach((to) => {
  const landing = to.name === "landing";
  document.title = landing
    ? "Memento — English vocabulary flashcards & spaced repetition"
    : `${to.meta.title || (to.name === "signup" ? "Create an account" : "Log in")} — Memento`;
  document.querySelector('meta[name="robots"]')?.setAttribute("content", landing ? "index, follow" : "noindex, follow");
});

export default router;
