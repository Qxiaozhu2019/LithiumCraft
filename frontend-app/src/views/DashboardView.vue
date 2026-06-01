<template>
  <article class="process-home">
    <header class="process-masthead">
      <div>
        <p class="process-brand">LithiumCraft</p>
        <h1>锂电池制造工艺知识库</h1>
        <p>围绕电芯制造全流程整理公开资料，聚焦制浆、涂布、辊压、分切、装配、注液、化成、分容与检测。</p>
      </div>
      <RouterLink v-if="!authStore.isAuthenticated.value" class="process-login-link" to="/login">管理登录</RouterLink>
    </header>

    <section class="process-search-panel">
      <label for="process-search">检索制造工艺</label>
      <div class="process-search-row">
        <el-input
          id="process-search"
          v-model="searchTerm"
          size="large"
          clearable
          placeholder="试试：涂布厚度、辊压压实密度、化成分容、极片缺陷"
          @keyup.enter="submitSearch"
        />
        <el-button type="primary" size="large" @click="submitSearch">搜索</el-button>
      </div>
      <div class="process-search-examples">
        <button v-for="example in examples" :key="example" type="button" @click="searchExample(example)">{{ example }}</button>
      </div>
    </section>

    <section class="process-section">
      <div class="process-section-title">
        <span>Manufacturing Flow</span>
        <h2>电芯制造全流程</h2>
      </div>

      <div v-if="stageLoading" class="process-empty">正在加载工序目录...</div>
      <div v-else class="process-stage-grid">
        <RouterLink v-for="stage in stages" :key="stage.slug" class="process-stage-card" :to="`/processes/${stage.slug}`">
          <strong>{{ stage.name }}</strong>
          <p>{{ stage.description }}</p>
          <span>{{ stage.item_count }} 条相关公开资料</span>
        </RouterLink>
      </div>
    </section>

    <section class="process-section">
      <div class="process-section-title with-action">
        <div>
          <span>Updated Stages</span>
          <h2>最近更新的工序资料</h2>
        </div>
        <el-button size="small" text @click="loadStages" :loading="stageLoading">刷新</el-button>
      </div>

      <div v-if="updatedStages.length" class="process-update-list">
        <RouterLink v-for="stage in updatedStages" :key="stage.slug" class="process-update-item" :to="`/processes/${stage.slug}`">
          <h3>{{ stage.name }}</h3>
          <p>{{ stage.description }}</p>
          <div class="process-meta">
            <span>{{ stage.item_count }} 条资料</span>
            <span>最新更新 {{ formatDateTime(stage.latest_crawled_at) }}</span>
          </div>
        </RouterLink>
      </div>
      <div v-else class="process-empty align-left">
        <strong>暂无工艺资料</strong>
        <p>等待抓取更新或管理员添加已通过 robots 审核的制造工艺公开来源。</p>
      </div>

      <RouterLink class="process-more" to="/processes">查看全部工序</RouterLink>
    </section>
  </article>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { listProcessStages } from "@/api/client";
import type { ProcessStage } from "@/api/types";
import { authStore } from "@/stores/auth";

const router = useRouter();
const stageLoading = ref(false);
const searchTerm = ref("");
const stages = ref<ProcessStage[]>([]);
const examples = ["涂布厚度", "辊压压实密度", "化成分容", "极片缺陷"];

const updatedStages = computed(() =>
  stages.value
    .filter((stage) => stage.item_count > 0)
    .sort((a, b) => Date.parse(b.latest_crawled_at || "") - Date.parse(a.latest_crawled_at || ""))
    .slice(0, 5)
);

async function loadStages() {
  stageLoading.value = true;
  try {
    stages.value = await listProcessStages();
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "工序目录加载失败");
  } finally {
    stageLoading.value = false;
  }
}

function submitSearch() {
  const q = searchTerm.value.trim();
  if (!q) return;
  router.push({ path: "/intelligence", query: { q, category: "制造工艺" } });
}

function searchExample(example: string) {
  searchTerm.value = example;
  submitSearch();
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "时间待确认";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

onMounted(loadStages);
</script>
