<template>
  <div class="page-stack">
    <PageHeader
      eyebrow="Process Stage"
      :title="stage?.name || '制造工序'"
      :description="stage?.description || '查看该工序下的公开资料。'"
    >
      <el-button @click="router.push('/processes')">返回工序目录</el-button>
    </PageHeader>

    <el-card v-if="stage" class="panel-card" shadow="never">
      <template #header>工序概览</template>
      <div class="process-detail-grid">
        <div class="process-diagram" :aria-label="stage.images[0]?.alt || `${stage.name}工艺示意图`">
          <div class="process-diagram-title">{{ stage.name }}流程示意</div>
          <div class="process-diagram-steps">
            <span v-for="step in stage.diagram_steps" :key="step">{{ step }}</span>
          </div>
          <p>{{ stage.images[0]?.source_name || "LithiumCraft 站内示意图" }}，用于辅助理解工序关系。</p>
        </div>
        <div>
          <h3>匹配关键词</h3>
          <div class="process-keywords">
            <el-tag v-for="keyword in visibleKeywords" :key="keyword" effect="plain">{{ keyword }}</el-tag>
          </div>
          <p class="process-detail-meta">
            共 {{ stage.item_count }} 条相关公开资料；涉及 {{ stage.source_count }} 个来源；最新更新
            {{ formatDate(stage.latest_crawled_at) }}
          </p>
        </div>
      </div>
    </el-card>

    <el-card class="panel-card" shadow="never">
      <template #header>相关工艺资料</template>
      <div v-if="loading" class="process-empty">正在加载相关资料...</div>
      <div v-else-if="stage?.items.length" class="process-update-list">
        <RouterLink v-for="item in stage.items" :key="item.id" class="process-update-item" :to="`/intelligence/${item.id}`">
          <h3>{{ displayText(item.title) }}</h3>
          <p>{{ previewText(item) }}</p>
          <div class="process-meta">
            <span>{{ displayText(item.source_name) }}</span>
            <span>{{ displayText(item.category || "综合") }}</span>
            <span>{{ formatDate(item.source_published_at || item.crawled_at) }}</span>
          </div>
        </RouterLink>
      </div>
      <el-empty v-else description="暂无相关公开资料，等待抓取更新或管理员添加来源。" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { getProcessStage } from "@/api/client";
import type { IntelligenceItem, ProcessStageDetail } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";

const props = defineProps<{ slug: string }>();
const router = useRouter();
const loading = ref(false);
const stage = ref<ProcessStageDetail | null>(null);
const visibleKeywords = computed(() => stage.value?.keywords.filter((keyword) => /[\u4e00-\u9fff]/.test(keyword)) || []);

async function load() {
  loading.value = true;
  try {
    stage.value = await getProcessStage(props.slug, 30);
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "工序资料加载失败");
    stage.value = null;
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

function formatDate(value: string | null) {
  if (!value) {
    return "时间待确认";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

watch(() => props.slug, load);
onMounted(load);
</script>
