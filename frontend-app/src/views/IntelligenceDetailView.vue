<template>
  <div class="page-stack">
    <PageHeader eyebrow="Intelligence Detail" :title="item?.title || '情报详情'" description="查看摘要、来源、风控原因并执行归档或恢复。">
      <el-button @click="router.back()">返回</el-button>
      <el-button v-if="item" type="primary" plain @click="openSource">打开原文</el-button>
    </PageHeader>

    <el-skeleton v-if="loading" :rows="8" animated />
    <template v-else-if="item">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="16">
          <el-card class="panel-card article-card" shadow="never">
            <div class="detail-meta">
              <StatusPill :status="item.status" />
              <span>{{ item.source_name }}</span>
              <span>{{ formatDate(item.source_published_at || item.crawled_at) }}</span>
            </div>
            <h2>AI 摘要</h2>
            <p>{{ item.summary || "暂无摘要" }}</p>
            <h2>内容摘录</h2>
            <p class="excerpt">{{ item.content_excerpt || "暂无摘录" }}</p>
            <el-alert v-if="item.block_reason" title="拦截原因" :description="item.block_reason" type="warning" show-icon :closable="false" />
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="panel-card" shadow="never">
            <template #header>操作与属性</template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="分类">{{ item.category }}</el-descriptions-item>
              <el-descriptions-item label="标签">{{ splitTags(item.tags).join(" / ") || "无" }}</el-descriptions-item>
              <el-descriptions-item label="重要性">{{ Math.round(item.importance_score * 100) }}%</el-descriptions-item>
              <el-descriptions-item label="抓取时间">{{ formatDate(item.crawled_at) }}</el-descriptions-item>
            </el-descriptions>
            <div class="action-stack">
              <el-button v-if="item.status !== 'archived'" type="warning" @click="changeStatus('archived')">归档</el-button>
              <el-button v-if="item.status !== 'active'" type="success" @click="changeStatus('active')">恢复可用</el-button>
              <el-button v-if="item.status !== 'blocked'" type="danger" plain @click="changeStatus('blocked')">标记拦截</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
    <el-empty v-else description="情报不存在" />
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { getIntelligence, updateIntelligence } from "@/api/client";
import type { IntelligenceItem, IntelligenceStatus } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";
import { formatDate, splitTags } from "@/utils/format";

const props = defineProps<{ id: string }>();
const router = useRouter();
const loading = ref(false);
const item = ref<IntelligenceItem | null>(null);

async function load() {
  loading.value = true;
  try {
    item.value = await getIntelligence(Number(props.id));
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "情报详情加载失败");
  } finally {
    loading.value = false;
  }
}

async function changeStatus(status: IntelligenceStatus) {
  if (!item.value) return;
  try {
    item.value = await updateIntelligence(item.value.id, { status });
    ElMessage.success("状态已更新");
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "状态更新失败");
  }
}

function openSource() {
  if (item.value?.source_url) {
    window.open(item.value.source_url, "_blank", "noopener,noreferrer");
  }
}

onMounted(load);
</script>
