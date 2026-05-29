<template>
  <div class="page-stack">
    <PageHeader eyebrow="Intelligence" title="情报列表" description="按关键词、分类与状态筛选公开来源沉淀的内部情报。" />

    <el-card class="panel-card" shadow="never">
      <el-form class="filter-bar" :model="filters" inline>
        <el-form-item label="关键词">
          <el-input v-model="filters.q" placeholder="标题或摘要" clearable @keyup.enter="load(1)" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" clearable placeholder="全部分类" style="width: 180px">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="authStore.isAuthenticated.value" label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部状态" style="width: 150px">
            <el-option label="可用" value="active" />
            <el-option label="拦截" value="blocked" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load(1)">搜索</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="items" v-loading="loading" class="clickable-table" @row-click="openDetail">
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
        <el-table-column prop="source_name" label="来源" width="150" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column label="标签" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="tag in splitTags(row.tags)" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="重要性" width="120">
          <template #default="{ row }">{{ Math.round(row.importance_score * 100) }}%</template>
        </el-table-column>
        <el-table-column v-if="authStore.isAuthenticated.value" label="状态" width="100">
          <template #default="{ row }"><StatusPill :status="row.status" /></template>
        </el-table-column>
        <el-table-column label="抓取时间" width="180">
          <template #default="{ row }">{{ formatDate(row.crawled_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination layout="prev, pager, next, total" :total="total" :current-page="page" :page-size="pageSize" @current-change="load" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { listCategories, listIntelligence } from "@/api/client";
import type { Category, IntelligenceItem, IntelligenceStatus } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";
import { authStore } from "@/stores/auth";
import { formatDate, splitTags } from "@/utils/format";

const router = useRouter();
const loading = ref(false);
const items = ref<IntelligenceItem[]>([]);
const categories = ref<Category[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const filters = reactive<{ q: string; category: string; status: IntelligenceStatus | "" }>({ q: "", category: "", status: "" });
const dateRange = ref<[string, string] | null>(null);

async function load(targetPage = page.value) {
  loading.value = true;
  try {
    page.value = targetPage;
    const result = await listIntelligence({
      ...filters,
      date_from: dateRange.value?.[0],
      date_to: dateRange.value?.[1],
      page: page.value,
      page_size: pageSize
    });
    items.value = result.items;
    total.value = result.total;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "情报列表加载失败");
  } finally {
    loading.value = false;
  }
}

function reset() {
  filters.q = "";
  filters.category = "";
  filters.status = "";
  dateRange.value = null;
  load(1);
}

function openDetail(row: IntelligenceItem) {
  router.push(`/intelligence/${row.id}`);
}

onMounted(async () => {
  await Promise.all([
    load(1),
    listCategories().then((result) => { categories.value = result; }).catch(() => { categories.value = []; })
  ]);
});
</script>
