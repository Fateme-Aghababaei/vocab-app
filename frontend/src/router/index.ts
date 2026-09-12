import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
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
      path: "/",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue"),
    },
    {
      path: "/review",
      name: "review",
      component: () => import("@/views/ReviewView.vue"),
    },
    {
      path: "/library",
      name: "library",
      component: () => import("@/views/LibraryView.vue"),
    },
    {
      path: "/add",
      name: "add-word",
      component: () => import("@/views/AddWordView.vue"),
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

  if (isPublic && auth.isAuthenticated) {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
