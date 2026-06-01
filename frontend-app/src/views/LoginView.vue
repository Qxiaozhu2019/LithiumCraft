<template>
  <main class="login-screen">
    <section class="login-hero">
      <p class="eyebrow">LithiumCraft MVP</p>
      <h1>锂电工艺后台管理入口。</h1>
      <p>登录后维护公开来源、抓取任务、系统参数和工艺资料摘要。</p>
      <div class="signal-board">
        <span>公开来源</span>
        <span>低频抓取</span>
        <span>AI 摘要</span>
        <span>风险拦截</span>
      </div>
    </section>

    <el-card class="login-card" shadow="never">
      <template #header>
        <div>
          <p class="eyebrow">Admin Access</p>
          <h2>内部账号登录</h2>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" size="large" autocomplete="username" placeholder="admin" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" autocomplete="current-password" show-password placeholder="请输入密码" @keyup.enter="submit" />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
        <el-button class="login-button" type="primary" size="large" :loading="loading" @click="submit">进入后台</el-button>
      </el-form>
    </el-card>
  </main>
</template>

<script setup lang="ts">
import type { FormInstance, FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { authStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const formRef = ref<FormInstance>();
const loading = ref(false);
const error = ref("");
const form = reactive({ username: "", password: "" });
const rules: FormRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
};

async function submit() {
  if (!formRef.value) return;
  await formRef.value.validate();
  loading.value = true;
  error.value = "";
  try {
    await authStore.login(form.username, form.password);
    ElMessage.success("登录成功");
    router.replace(String(route.query.redirect || "/admin/crawl-logs"));
  } catch (err) {
    error.value = err instanceof Error ? err.message : "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>
