<template>
  <div class="page-stack">
    <PageHeader eyebrow="Material Summary" title="工艺资料摘要" description="按日期查看公开制造工艺资料的聚合摘要。">
      <template v-if="authStore.isAuthenticated.value">
        <el-date-picker v-model="targetDate" value-format="YYYY-MM-DD" type="date" placeholder="选择日期" />
        <el-button type="primary" :loading="generating" @click="generate">生成摘要</el-button>
      </template>
    </PageHeader>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="9">
        <el-card class="panel-card" shadow="never">
          <template #header>摘要列表</template>
          <el-table :data="briefs" v-loading="loading" highlight-current-row @row-click="selectBrief">
            <el-table-column prop="brief_date" label="日期" width="120" />
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><StatusPill :status="row.status" /></template>
            </el-table-column>
          </el-table>
          <div class="pagination-row">
            <el-pagination layout="prev, pager, next" :total="total" :current-page="page" :page-size="pageSize" @current-change="load" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="15">
        <el-card class="panel-card brief-reader" shadow="never">
          <template #header>{{ selected?.title || "请选择摘要" }}</template>
          <template v-if="selected">
            <p class="brief-date">{{ selected.brief_date }} · {{ selected.generated_at ? formatDate(selected.generated_at) : "未生成" }}</p>
            <h3>总览</h3>
            <p>{{ selected.overview || "暂无总览" }}</p>
            <h3>重点条目</h3>
            <ul>
              <li v-for="highlight in parseList(selected.highlights)" :key="highlight">{{ highlight }}</li>
            </ul>
            <h3>分类摘要</h3>
            <div class="category-summary">
              <div v-for="entry in parseCategorySummary(selected.category_summary)" :key="entry.name">
                <strong>{{ entry.name }}</strong>
                <p>{{ entry.value }}</p>
              </div>
            </div>
            <el-alert v-if="selected.error_message" :title="selected.error_message" type="error" show-icon :closable="false" />
          </template>
          <el-empty v-else description="暂无选中摘要" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

import { generateDailyBrief, listDailyBriefs } from "@/api/client";
import type { DailyBrief } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";
import { authStore } from "@/stores/auth";
import { formatDate } from "@/utils/format";

const loading = ref(false);
const generating = ref(false);
const briefs = ref<DailyBrief[]>([]);
const selected = ref<DailyBrief | null>(null);
const targetDate = ref<string>();
const total = ref(0);
const page = ref(1);
const pageSize = 12;

function parseList(raw: string) {
  try {
    const value = JSON.parse(raw);
    return Array.isArray(value) ? value.map(String) : [raw];
  } catch {
    return raw ? raw.split(/\n+/).filter(Boolean) : [];
  }
}

function parseCategorySummary(raw: string) {
  try {
    const value = JSON.parse(raw) as Record<string, unknown>;
    return Object.entries(value).map(([name, item]) => ({ name, value: String(item) }));
  } catch {
    return raw ? [{ name: "摘要", value: raw }] : [];
  }
}

async function load(targetPage = page.value) {
  loading.value = true;
  try {
    page.value = targetPage;
    const result = await listDailyBriefs(page.value, pageSize);
    briefs.value = result.items;
    total.value = result.total;
    selected.value = selected.value || result.items[0] || null;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "工艺资料摘要加载失败");
  } finally {
    loading.value = false;
  }
}

async function generate() {
  generating.value = true;
  try {
    selected.value = await generateDailyBrief(targetDate.value);
    ElMessage.success("摘要生成任务已完成");
    await load(1);
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "摘要生成失败");
  } finally {
    generating.value = false;
  }
}

function selectBrief(row: DailyBrief) {
  selected.value = row;
}

onMounted(() => load(1));
</script>
