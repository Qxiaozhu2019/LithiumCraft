<template>
  <el-container v-if="authStore.isAuthenticated.value" class="workspace-shell">
    <el-aside width="264px" class="workspace-aside">
      <RouterLink to="/" class="brand-lockup">
        <span>LC</span>
        <div>
          <strong>LithiumCraft</strong>
          <small>锂电资讯门户</small>
        </div>
      </RouterLink>

      <p class="menu-section">公开内容</p>
      <el-menu :default-active="route.path" router class="workspace-menu">
        <el-menu-item index="/">门户首页</el-menu-item>
        <el-menu-item index="/intelligence">资讯列表</el-menu-item>
        <el-menu-item index="/daily-briefs">每日简报</el-menu-item>
      </el-menu>

      <p class="menu-section admin-section">后台管理</p>
      <el-menu :default-active="route.path" router class="workspace-menu">
        <el-menu-item index="/admin/sources">来源管理</el-menu-item>
        <el-menu-item index="/admin/crawl-logs">抓取日志</el-menu-item>
        <el-menu-item index="/admin/settings">系统设置</el-menu-item>
      </el-menu>

      <div class="compliance-note">
        <b>合规边界</b>
        <span>仅处理公开来源；不绕过登录、付费墙、验证码或 robots 限制。</span>
      </div>
    </el-aside>

    <el-container>
      <el-header class="workspace-topbar">
        <div>
          <span class="pulse-dot"></span>
          <span>锂电资讯门户 · 后台已登录</span>
        </div>
        <el-dropdown @command="handleCommand">
          <button class="user-chip">
            {{ authStore.state.username || "admin" }}
            <span>退出</span>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="workspace-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>

  <div v-else class="portal-shell">
    <header class="portal-topbar">
      <RouterLink to="/" class="portal-brand">
        <span>LC</span>
        <div>
          <strong>LithiumCraft</strong>
          <small>锂电资讯门户</small>
        </div>
      </RouterLink>
      <nav class="portal-nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/intelligence">资讯</RouterLink>
        <RouterLink to="/daily-briefs">简报</RouterLink>
      </nav>
      <RouterLink class="portal-login" to="/login">管理登录</RouterLink>
    </header>

    <main class="portal-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";

import { authStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();

function handleCommand(command: string) {
  if (command === "logout") {
    authStore.logout();
    router.push("/");
  }
}
</script>
