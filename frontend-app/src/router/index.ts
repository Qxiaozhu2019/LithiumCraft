import { createRouter, createWebHistory } from "vue-router";

import { authStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { public: true }
    },
    {
      path: "/",
      component: () => import("@/layouts/WorkspaceLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "/dashboard" },
        { path: "dashboard", name: "dashboard", component: () => import("@/views/DashboardView.vue") },
        { path: "intelligence", name: "intelligence", component: () => import("@/views/IntelligenceListView.vue") },
        { path: "intelligence/:id", name: "intelligence-detail", component: () => import("@/views/IntelligenceDetailView.vue"), props: true },
        { path: "daily-briefs", name: "daily-briefs", component: () => import("@/views/DailyBriefsView.vue") },
        { path: "sources", name: "sources", component: () => import("@/views/SourcesView.vue") },
        { path: "crawl-logs", name: "crawl-logs", component: () => import("@/views/CrawlLogsView.vue") },
        { path: "settings", name: "settings", component: () => import("@/views/SettingsView.vue") }
      ]
    },
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" }
  ]
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated.value) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && authStore.isAuthenticated.value) {
    return { path: String(to.query.redirect || "/dashboard") };
  }
  return true;
});

export default router;
