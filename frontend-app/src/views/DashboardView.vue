<template>
  <article class="process-home">
    <header class="process-masthead">
      <div>
        <p class="process-brand">LithiumCraft</p>
        <h1>锂电池制造工艺知识库</h1>
        <p>围绕电芯制造全流程聚合公开资料，优先检索制浆、涂布、辊压、化成、分容等工艺内容。</p>
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
          <span>Process Updates</span>
          <h2>工艺相关最新资料</h2>
        </div>
        <el-button size="small" text @click="refresh" :loading="loading">刷新</el-button>
      </div>

      <div v-if="loading && !latest.length" class="process-empty">正在加载公开资料...</div>
      <div v-else-if="latest.length" class="process-update-list">
        <RouterLink v-for="item in latest" :key="item.id" class="process-update-item" :to="`/intelligence/${item.id}`">
          <h3>{{ displayText(item.title) }}</h3>
          <p>{{ previewText(item) }}</p>
          <div class="process-meta">
            <span>{{ displayText(item.source_name) }}</span>
            <span>{{ displayText(item.category || "综合") }}</span>
            <span>{{ formatDateTime(item.source_published_at || item.crawled_at) }}</span>
          </div>
        </RouterLink>
      </div>
      <div v-else class="process-empty align-left">
        <strong>暂无工艺相关资料</strong>
        <p>等待抓取更新或管理员添加更聚焦制造工艺的公开来源。</p>
      </div>

      <RouterLink class="process-more" to="/intelligence">查看全部公开资料</RouterLink>
    </section>

    <section class="process-section process-brief-section">
      <div class="process-section-title">
        <span>Brief</span>
        <h2>每日简报</h2>
      </div>
      <div v-if="briefs.length" class="process-brief-list">
        <RouterLink v-for="brief in briefs" :key="brief.id" to="/daily-briefs" class="process-brief-item">
          <strong>{{ displayText(brief.title) }}</strong>
          <span>{{ brief.brief_date }} · {{ brief.status }}</span>
        </RouterLink>
      </div>
      <RouterLink class="process-more" to="/daily-briefs">查看简报</RouterLink>
    </section>
  </article>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { listDailyBriefs, listIntelligence, listProcessStages } from "@/api/client";
import type { DailyBrief, IntelligenceItem, ProcessStage } from "@/api/types";
import { authStore } from "@/stores/auth";

const router = useRouter();
const loading = ref(false);
const stageLoading = ref(false);
const searchTerm = ref("");
const stages = ref<ProcessStage[]>([]);
const latest = ref<IntelligenceItem[]>([]);
const briefs = ref<DailyBrief[]>([]);
const examples = ["涂布厚度", "辊压压实密度", "化成分容", "极片缺陷"];

async function refresh() {
  loading.value = true;
  try {
    const [processItems, briefPage] = await Promise.all([
      listIntelligence({ category: "制造工艺", page_size: 6 }),
      listDailyBriefs(1, 3)
    ]);
    latest.value = processItems.items;
    briefs.value = briefPage.items;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "工艺资料加载失败");
  } finally {
    loading.value = false;
  }
}

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
  router.push({ path: "/intelligence", query: { q } });
}

function searchExample(example: string) {
  searchTerm.value = example;
  submitSearch();
}

function displayText(value: string) {
  return value
    .replace(new RegExp("\\u60c5\\u62a5", "g"), "信息")
    .replace(new RegExp("\\u5de5\\u4f5c\\u53f0", "g"), "")
    .replace(new RegExp("\\u95e8\\u6237", "g"), "");
}

function previewText(item: IntelligenceItem) {
  return displayText(item.summary || item.content_excerpt || "暂无摘要，点击查看来源信息。");
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

onMounted(() => {
  loadStages();
  refresh();
});
</script>
