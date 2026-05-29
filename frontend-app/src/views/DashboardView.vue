<template>
  <div class="page-stack">
    <PageHeader eyebrow="Overview" title="投研态势仪表盘" description="聚合今日抓取、风险拦截、来源健康度与最新摘要。">
      <el-button type="primary" @click="refresh" :loading="loading">刷新数据</el-button>
    </PageHeader>

    <div class="metric-grid">
      <MetricCard label="活跃情报" :value="metrics.active" hint="当前可阅读条目" tone="green" />
      <MetricCard label="风险拦截" :value="metrics.blocked" hint="需人工复核" tone="red" />
      <MetricCard label="精选来源" :value="metrics.sources" hint="启用或待启用" tone="blue" />
      <MetricCard label="每日摘要" :value="metrics.briefs" hint="已生成简报" tone="amber" />
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>最新情报</template>
          <el-table :data="latest" v-loading="loading" @row-click="openItem">
            <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column label="重要性" width="120">
              <template #default="{ row }">
                <el-progress :percentage="Math.round(row.importance_score * 100)" :show-text="false" />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }"><StatusPill :status="row.status" /></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card class="panel-card daily-focus" shadow="never">
          <template #header>最近每日摘要</template>
          <div v-if="briefs.length" class="brief-list">
            <RouterLink v-for="brief in briefs" :key="brief.id" to="/daily-briefs" class="brief-link">
              <strong>{{ brief.title }}</strong>
              <span>{{ brief.brief_date }} · {{ brief.status }}</span>
              <p>{{ brief.overview || "暂无总览" }}</p>
            </RouterLink>
          </div>
          <el-empty v-else description="暂无摘要" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { listDailyBriefs, listIntelligence, listSources } from "@/api/client";
import type { DailyBrief, IntelligenceItem } from "@/api/types";
import MetricCard from "@/components/MetricCard.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";

const router = useRouter();
const loading = ref(false);
const latest = ref<IntelligenceItem[]>([]);
const briefs = ref<DailyBrief[]>([]);
const metrics = reactive({ active: 0, blocked: 0, sources: 0, briefs: 0 });

async function refresh() {
  loading.value = true;
  try {
    const [active, blocked, allLatest, sources, briefPage] = await Promise.all([
      listIntelligence({ status: "active", page_size: 1 }),
      listIntelligence({ status: "blocked", page_size: 1 }),
      listIntelligence({ page_size: 6 }),
      listSources(1, 1),
      listDailyBriefs(1, 5)
    ]);
    metrics.active = active.total;
    metrics.blocked = blocked.total;
    metrics.sources = sources.total;
    metrics.briefs = briefPage.total;
    latest.value = allLatest.items;
    briefs.value = briefPage.items;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "仪表盘加载失败");
  } finally {
    loading.value = false;
  }
}

function openItem(row: IntelligenceItem) {
  router.push(`/intelligence/${row.id}`);
}

onMounted(refresh);
</script>
