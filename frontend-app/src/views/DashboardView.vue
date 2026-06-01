<template>
  <article class="news-home">
    <header class="news-masthead">
      <div>
        <p class="news-brand">LithiumCraft</p>
        <h1>锂电资讯</h1>
        <p>追踪公开来源中的产业政策、材料工艺、储能应用与企业动态，只展示经过合规检查的信息。</p>
      </div>
      <RouterLink v-if="!authStore.isAuthenticated.value" class="news-login-link" to="/login">管理登录</RouterLink>
    </header>

    <section class="news-section">
      <div class="news-section-title">
        <div>
          <span>Latest Updates</span>
          <h2>最新资讯</h2>
        </div>
        <el-button size="small" text @click="refresh" :loading="loading">刷新</el-button>
      </div>

      <div v-if="loading && !latest.length" class="news-empty">正在加载公开信息...</div>

      <template v-else-if="headline">
        <RouterLink class="news-lead" :to="`/intelligence/${headline.id}`">
          <span class="news-kicker">头条</span>
          <h3>{{ displayText(headline.title) }}</h3>
          <p>{{ previewText(headline) }}</p>
          <div class="news-meta">
            <span>{{ displayText(headline.source_name) }}</span>
            <span>{{ displayText(headline.category || "综合") }}</span>
            <span>{{ formatDateTime(headline.source_published_at || headline.crawled_at) }}</span>
          </div>
        </RouterLink>

        <div class="news-list">
          <RouterLink v-for="item in secondaryItems" :key="item.id" class="news-list-item" :to="`/intelligence/${item.id}`">
            <div>
              <h3>{{ displayText(item.title) }}</h3>
              <p>{{ previewText(item) }}</p>
              <div class="news-meta">
                <span>{{ displayText(item.source_name) }}</span>
                <span>{{ displayText(item.category || "综合") }}</span>
                <span>{{ formatDateTime(item.source_published_at || item.crawled_at) }}</span>
              </div>
            </div>
          </RouterLink>
        </div>

        <RouterLink class="news-more" to="/intelligence">查看全部资讯</RouterLink>
      </template>

      <div v-else class="news-empty">
        <strong>暂无资讯</strong>
        <p>等待每日 07:00 自动更新，或管理员登录后手动更新。</p>
      </div>
    </section>

    <section class="news-section">
      <div class="news-section-title">
        <div>
          <span>Daily Brief</span>
          <h2>每日简报</h2>
        </div>
      </div>

      <div v-if="briefs.length" class="brief-paper-list">
        <RouterLink v-for="brief in briefs" :key="brief.id" to="/daily-briefs" class="brief-paper-item">
          <span>{{ brief.brief_date }} · {{ brief.status }}</span>
          <strong>{{ displayText(brief.title) }}</strong>
          <p>{{ displayText(brief.overview || "暂无总览") }}</p>
        </RouterLink>
      </div>
      <div v-else class="news-empty align-left">
        <strong>暂无简报</strong>
        <p>更新完成后将生成每日简报。</p>
      </div>

      <RouterLink class="news-more" to="/daily-briefs">更多简报</RouterLink>
    </section>

    <footer class="news-footnote">
      <strong>内容边界</strong>
      <span>仅展示公开来源中的摘要、链接和必要说明，不绕过登录、付费墙、验证码或 robots 限制。</span>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import { listDailyBriefs, listIntelligence } from "@/api/client";
import type { DailyBrief, IntelligenceItem } from "@/api/types";
import { authStore } from "@/stores/auth";

const loading = ref(false);
const latest = ref<IntelligenceItem[]>([]);
const briefs = ref<DailyBrief[]>([]);

const headline = computed(() => latest.value[0] ?? null);
const secondaryItems = computed(() => latest.value.slice(1, 10));

async function refresh() {
  loading.value = true;
  try {
    const [allLatest, briefPage] = await Promise.all([
      listIntelligence({ page_size: 10 }),
      listDailyBriefs(1, 5)
    ]);
    latest.value = allLatest.items;
    briefs.value = briefPage.items;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "信息加载失败");
  } finally {
    loading.value = false;
  }
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

onMounted(refresh);
</script>
