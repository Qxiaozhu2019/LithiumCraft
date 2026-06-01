<template>
  <div class="page-stack">
    <PageHeader
      eyebrow="Material Topic"
      :title="topic?.name || '材料专题'"
      :description="topic?.description || '查看材料特性与制造工艺之间的关系。'"
    >
      <el-button @click="router.push('/topics')">返回专题目录</el-button>
    </PageHeader>

    <el-card v-if="topic" class="panel-card" shadow="never">
      <template #header>专题概览</template>
      <div class="topic-detail-grid">
        <section>
          <h3>关键特性</h3>
          <div class="process-keywords">
            <el-tag v-for="property in topic.key_properties" :key="property" effect="plain">{{ property }}</el-tag>
          </div>
        </section>
        <section>
          <h3>关联工序</h3>
          <div class="topic-process-links">
            <RouterLink v-for="slug in topic.related_process_slugs" :key="slug" :to="`/processes/${slug}`">
              {{ processName(slug) }}
            </RouterLink>
          </div>
        </section>
      </div>
    </el-card>

    <el-card v-if="topic" class="panel-card" shadow="never">
      <template #header>材料-工艺-性能关系</template>
      <div class="topic-impact-list">
        <p v-for="impact in topic.process_impacts" :key="impact">{{ impact }}</p>
      </div>
    </el-card>

    <el-card v-if="topic" class="panel-card" shadow="never">
      <template #header>匹配关键词</template>
      <div class="process-keywords">
        <el-tag v-for="keyword in topic.keywords" :key="keyword" effect="plain">{{ keyword }}</el-tag>
      </div>
      <p class="process-detail-meta">
        共 {{ topic.item_count }} 条相关公开资料；涉及 {{ topic.source_count }} 个来源；最新更新
        {{ formatDate(topic.latest_crawled_at) }}
      </p>
    </el-card>

    <el-card class="panel-card" shadow="never">
      <template #header>相关公开资料</template>
      <div v-if="loading" class="process-empty">正在加载相关资料...</div>
      <div v-else-if="topic?.items.length" class="process-update-list">
        <RouterLink v-for="item in topic.items" :key="item.id" class="process-update-item" :to="`/intelligence/${item.id}`">
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
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { getTopic } from "@/api/client";
import type { IntelligenceItem, TopicDetail } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";

const props = defineProps<{ slug: string }>();
const router = useRouter();
const loading = ref(false);
const topic = ref<TopicDetail | null>(null);

const processNames: Record<string, string> = {
  slurry: "制浆",
  coating: "涂布",
  calendering: "辊压",
  slitting: "分切",
  "winding-stacking": "卷绕/叠片",
  assembly: "装配",
  "electrolyte-filling": "注液",
  formation: "化成",
  grading: "分容",
  inspection: "检测"
};

async function load() {
  loading.value = true;
  try {
    topic.value = await getTopic(props.slug, 30);
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "专题资料加载失败");
    topic.value = null;
  } finally {
    loading.value = false;
  }
}

function processName(slug: string) {
  return processNames[slug] || slug;
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
