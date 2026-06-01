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
      children: [
        { path: "", name: "home", component: () => import("@/views/DashboardView.vue") },
        { path: "dashboard", redirect: "/" },
        { path: "processes", name: "processes", component: () => import("@/views/ProcessListView.vue") },
        { path: "processes/:slug", name: "process-detail", component: () => import("@/views/ProcessDetailView.vue"), props: true },
        { path: "intelligence", name: "intelligence", component: () => import("@/views/IntelligenceListView.vue") },
        { path: "intelligence/:id", name: "intelligence-detail", component: () => import("@/views/IntelligenceDetailView.vue"), props: true },
        { path: "daily-briefs", name: "daily-briefs", component: () => import("@/views/DailyBriefsView.vue") },
        { path: "admin/sources", name: "sources", component: () => import("@/views/SourcesView.vue"), meta: { requiresAuth: true } },
        { path: "admin/crawl-logs", name: "crawl-logs", component: () => import("@/views/CrawlLogsView.vue"), meta: { requiresAuth: true } },
        { path: "admin/settings", name: "settings", component: () => import("@/views/SettingsView.vue"), meta: { requiresAuth: true } }
      ]
    },
    { path: "/:pathMatch(.*)*", redirect: "/" }
  ]
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated.value) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && authStore.isAuthenticated.value) {
    return { path: String(to.query.redirect || "/admin/crawl-logs") };
  }
  return true;
});

export default router;
