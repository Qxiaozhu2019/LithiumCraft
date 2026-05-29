<template>
  <div class="page-stack">
    <PageHeader eyebrow="Crawler" title="抓取日志" description="查看抓取任务执行结果，并对启用来源进行手动触发。">
      <el-select v-model="selectedSource" placeholder="选择来源" filterable style="width: 240px">
        <el-option v-for="source in sources" :key="source.id" :label="source.name" :value="source.id" />
      </el-select>
      <el-button type="primary" :disabled="!selectedSource" :loading="triggering" @click="trigger">手动触发</el-button>
    </PageHeader>

    <el-card class="panel-card" shadow="never">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="task_type" label="任务类型" min-width="150" />
        <el-table-column prop="source_id" label="来源 ID" width="100" />
        <el-table-column label="状态" width="110"><template #default="{ row }"><StatusPill :status="row.status" /></template></el-table-column>
        <el-table-column prop="fetched_count" label="抓取" width="90" />
        <el-table-column prop="inserted_count" label="入库" width="90" />
        <el-table-column prop="blocked_count" label="拦截" width="90" />
        <el-table-column prop="duration_ms" label="耗时(ms)" width="110" />
        <el-table-column label="开始时间" width="180"><template #default="{ row }">{{ formatDate(row.started_at) }}</template></el-table-column>
        <el-table-column label="错误" min-width="220" show-overflow-tooltip><template #default="{ row }">{{ row.error_message || "-" }}</template></el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination layout="prev, pager, next, total" :total="total" :current-page="page" :page-size="pageSize" @current-change="loadTasks" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

import { listCrawlTasks, listSources, triggerCrawl } from "@/api/client";
import type { CrawlTask, Source } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";
import { formatDate } from "@/utils/format";

const loading = ref(false);
const triggering = ref(false);
const tasks = ref<CrawlTask[]>([]);
const sources = ref<Source[]>([]);
const selectedSource = ref<number>();
const total = ref(0);
const page = ref(1);
const pageSize = 20;

async function loadTasks(targetPage = page.value) {
  loading.value = true;
  try {
    page.value = targetPage;
    const result = await listCrawlTasks(page.value, pageSize);
    tasks.value = result.items;
    total.value = result.total;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "抓取日志加载失败");
  } finally {
    loading.value = false;
  }
}

async function trigger() {
  if (!selectedSource.value) return;
  triggering.value = true;
  try {
    await triggerCrawl(selectedSource.value);
    ElMessage.success("抓取任务已入队");
    await loadTasks(1);
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "触发失败");
  } finally {
    triggering.value = false;
  }
}

onMounted(async () => {
  await Promise.all([
    loadTasks(1),
    listSources(1, 100).then((result) => { sources.value = result.items; }).catch(() => { sources.value = []; })
  ]);
});
</script>
