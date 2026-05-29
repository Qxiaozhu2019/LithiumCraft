<template>
  <div class="home-page page-stack">
    <section class="home-hero">
      <div class="home-hero-copy">
        <p class="eyebrow">Lithium News</p>
        <h1>锂电资讯</h1>
        <p class="home-hero-summary">追踪公开来源中的产业政策、材料工艺、储能应用与企业动态，只展示经过合规检查的信息。</p>
        <div class="home-hero-actions">
          <RouterLink class="home-hero-link home-hero-link-primary" to="/intelligence">查看最新资讯</RouterLink>
          <RouterLink class="home-hero-link" to="/daily-briefs">阅读每日简报</RouterLink>
        </div>
      </div>

      <aside class="home-status-card" aria-label="更新状态">
        <span class="home-status-label">更新状态</span>
        <strong>每日 07:00</strong>
        <p>自动读取已确认的公开来源，管理员也可在后台手动更新。</p>
        <div class="home-status-meta">
          <span>公开来源</span>
          <span>合规过滤</span>
          <span>摘要优先</span>
        </div>
      </aside>
    </section>

    <section class="home-info-strip" aria-label="信息概览">
      <div>
        <span>更新节奏</span>
        <strong>每日 07:00</strong>
      </div>
      <div>
        <span>公开来源</span>
        <strong>已确认来源</strong>
      </div>
      <div>
        <span>合规过滤</span>
        <strong>robots 与规则检查</strong>
      </div>
      <div>
        <span>最近更新</span>
        <strong>{{ latestUpdatedText }}</strong>
      </div>
    </section>

    <section class="home-content-grid">
      <div class="home-main-column">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Latest Updates</p>
            <h2>最新资讯</h2>
          </div>
          <div class="section-actions">
            <el-button size="small" text @click="refresh" :loading="loading">刷新</el-button>
            <RouterLink class="section-link" to="/intelligence">查看全部</RouterLink>
          </div>
        </div>

        <div v-if="loading && !latest.length" class="home-loading-card">正在加载公开信息...</div>

        <template v-else-if="headline">
          <RouterLink class="headline-card" :to="`/intelligence/${headline.id}`">
            <span class="headline-kicker">头条</span>
            <h3>{{ displayText(headline.title) }}</h3>
            <p>{{ previewText(headline) }}</p>
            <div class="article-meta">
              <span>{{ displayText(headline.source_name) }}</span>
              <span>{{ displayText(headline.category || "综合") }}</span>
              <span>{{ formatDateTime(headline.source_published_at || headline.crawled_at) }}</span>
            </div>
          </RouterLink>

          <div class="headline-list">
            <RouterLink v-for="item in secondaryItems" :key="item.id" class="headline-list-item" :to="`/intelligence/${item.id}`">
              <div>
                <h3>{{ displayText(item.title) }}</h3>
                <p>{{ previewText(item) }}</p>
              </div>
              <span>{{ displayText(item.source_name) }}</span>
            </RouterLink>
          </div>
        </template>

        <div v-else class="home-empty-state">
          <strong>暂无资讯</strong>
          <p>等待每日 07:00 自动更新，或管理员登录后手动更新。</p>
        </div>
      </div>

      <aside class="home-side-column">
        <div class="section-heading compact">
          <div>
            <p class="eyebrow">Daily Brief</p>
            <h2>每日简报</h2>
          </div>
          <RouterLink class="section-link" to="/daily-briefs">更多</RouterLink>
        </div>

        <div v-if="briefs.length" class="home-brief-list">
          <RouterLink v-for="brief in briefs" :key="brief.id" to="/daily-briefs" class="home-brief-card">
            <span>{{ brief.brief_date }} · {{ brief.status }}</span>
            <strong>{{ displayText(brief.title) }}</strong>
            <p>{{ displayText(brief.overview || "暂无总览") }}</p>
          </RouterLink>
        </div>
        <div v-else class="home-empty-state compact">
          <strong>暂无简报</strong>
          <p>更新完成后将生成每日信息概览。</p>
        </div>

        <div class="home-compliance-card">
          <strong>内容边界</strong>
          <p>仅展示公开来源中的摘要、链接和必要说明，不绕过登录、付费墙、验证码或 robots 限制。</p>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import { listDailyBriefs, listIntelligence } from "@/api/client";
import type { DailyBrief, IntelligenceItem } from "@/api/types";

const loading = ref(false);
const latest = ref<IntelligenceItem[]>([]);
const briefs = ref<DailyBrief[]>([]);

const headline = computed(() => latest.value[0] ?? null);
const secondaryItems = computed(() => latest.value.slice(1, 7));
const latestUpdatedText = computed(() => {
  const first = latest.value[0];
  if (!first) {
    return "等待更新";
  }
  return formatDateTime(first.source_published_at || first.crawled_at);
});

async function refresh() {
  loading.value = true;
  try {
    const [allLatest, briefPage] = await Promise.all([
      listIntelligence({ page_size: 7 }),
      listDailyBriefs(1, 4)
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
