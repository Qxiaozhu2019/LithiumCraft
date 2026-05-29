<template>
  <div class="page-stack">
    <PageHeader eyebrow="Lithium News" title="锂电资讯" description="聚合公开来源中的产业政策、材料工艺、储能应用与企业动态，只展示经过合规检查的信息。">
      <el-button type="primary" @click="refresh" :loading="loading">刷新信息</el-button>
    </PageHeader>

    <div class="metric-grid">
      <MetricCard label="可读资讯" :value="metrics.active" hint="当前公开条目" tone="green" />
      <MetricCard label="最新展示" :value="latest.length" hint="首页最新内容" tone="blue" />
      <MetricCard label="每日简报" :value="metrics.briefs" hint="已生成简报" tone="amber" />
      <MetricCard label="更新节奏" value="07:00" hint="每日早晨自动更新" tone="red" />
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="15">
        <el-card class="panel-card" shadow="never">
          <template #header>最新资讯</template>
          <el-table v-if="latest.length || loading" :data="latest" v-loading="loading" @row-click="openItem">
            <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
            <el-table-column prop="source_name" label="来源" width="150" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column label="热度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="Math.round(row.importance_score * 100)" :show-text="false" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无公开资讯，等待每日 7 点自动更新或管理员手动更新。" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="9">
        <el-card class="panel-card daily-focus" shadow="never">
          <template #header>最近每日简报</template>
          <div v-if="briefs.length" class="brief-list">
            <RouterLink v-for="brief in briefs" :key="brief.id" to="/daily-briefs" class="brief-link">
              <strong>{{ brief.title }}</strong>
              <span>{{ brief.brief_date }} · {{ brief.status }}</span>
              <p>{{ brief.overview || "暂无总览" }}</p>
            </RouterLink>
          </div>
          <el-empty v-else description="暂无简报" />
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
      listIntelligence({ page_size: 8 }),
      listDailyBriefs(1, 5)
    ]);
    metrics.active = active.total;
    metrics.briefs = briefPage.total;
    latest.value = allLatest.items;
    briefs.value = briefPage.items;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "信息加载失败");
  } finally {
    loading.value = false;
  }
}

function openItem(row: IntelligenceItem) {
  router.push(`/intelligence/${row.id}`);
}

onMounted(refresh);
</script>
