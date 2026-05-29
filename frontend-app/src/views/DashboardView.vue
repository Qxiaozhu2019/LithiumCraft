<template>
  <div class="page-stack">
    <PageHeader eyebrow="Overview" title="锂电情报公开首页" description="聚合真实公开来源抓取后的最新情报与每日摘要。">
      <el-button type="primary" @click="refresh" :loading="loading">刷新数据</el-button>
    </PageHeader>

    <div class="metric-grid">
      <MetricCard label="活跃情报" :value="metrics.active" hint="当前可阅读条目" tone="green" />
      <MetricCard label="最新展示" :value="latest.length" hint="首页最新条目" tone="blue" />
      <MetricCard label="每日摘要" :value="metrics.briefs" hint="已生成简报" tone="amber" />
      <MetricCard label="抓取节奏" value="07:00" hint="每日早晨自动抓取" tone="red" />
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>最新情报</template>
          <el-table v-if="latest.length || loading" :data="latest" v-loading="loading" @row-click="openItem">
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
          <el-empty v-else description="暂无真实抓取结果，等待每日 7 点自动抓取或管理员手动抓取。" />
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

import { listDailyBriefs, listIntelligence } from "@/api/client";
import type { DailyBrief, IntelligenceItem } from "@/api/types";
import MetricCard from "@/components/MetricCard.vue";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";

const router = useRouter();
const loading = ref(false);
const latest = ref<IntelligenceItem[]>([]);
const briefs = ref<DailyBrief[]>([]);
const metrics = reactive({ active: 0, briefs: 0 });

async function refresh() {
  loading.value = true;
  try {
    const [active, allLatest, briefPage] = await Promise.all([
      listIntelligence({ status: "active", page_size: 1 }),
      listIntelligence({ page_size: 6 }),
      listDailyBriefs(1, 5)
    ]);
    metrics.active = active.total;
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
