<template>
  <el-container class="workspace-shell">
    <el-aside width="264px" class="workspace-aside">
      <RouterLink to="/" class="brand-lockup">
        <span>LC</span>
        <div>
          <strong>LithiumCraft</strong>
          <small>Intelligence Desk</small>
        </div>
      </RouterLink>

      <el-menu :default-active="route.path" router class="workspace-menu">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/intelligence">情报列表</el-menu-item>
        <el-menu-item index="/daily-briefs">每日摘要</el-menu-item>
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
          <span>公开锂电情报首页</span>
        </div>
        <el-dropdown v-if="authStore.isAuthenticated.value" @command="handleCommand">
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
        <RouterLink v-else class="user-chip" to="/login">管理登录</RouterLink>
      </el-header>
      <el-main class="workspace-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
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
