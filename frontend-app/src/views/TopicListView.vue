<template>
  <div class="page-stack">
    <PageHeader
      eyebrow="Materials & Properties"
      title="材料与特性"
      description="围绕正极、负极、电解液、隔膜和干法电极，查看它们如何影响制造工艺窗口、良率与性能。"
    />

    <div v-if="loading" class="process-empty">正在加载专题目录...</div>
    <div v-else class="topic-grid">
      <RouterLink v-for="topic in topics" :key="topic.slug" class="topic-card" :to="`/topics/${topic.slug}`">
        <span class="topic-card-label">{{ topic.key_properties.slice(0, 3).join(" / ") }}</span>
        <strong>{{ topic.name }}</strong>
        <p>{{ topic.summary }}</p>
        <div class="process-meta">
          <span>{{ topic.item_count }} 条相关资料</span>
          <span>{{ topic.related_process_slugs.length }} 个关联工序</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

import { listTopics } from "@/api/client";
import type { Topic } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";

const loading = ref(false);
const topics = ref<Topic[]>([]);

async function load() {
  loading.value = true;
  try {
    topics.value = await listTopics();
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "专题目录加载失败");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
