<template>
  <div class="page-stack">
    <PageHeader eyebrow="Sources" title="来源管理" description="维护精选公开来源、抓取频率、域名限频与合规状态。">
      <el-button type="primary" @click="openCreate">新增来源</el-button>
    </PageHeader>

    <el-card class="panel-card" shadow="never">
      <el-table :data="sources" v-loading="loading">
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="type" label="类型" width="110" />
        <el-table-column prop="domain" label="域名" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="130">
          <template #default="{ row }"><StatusPill :status="row.status" /></template>
        </el-table-column>
        <el-table-column prop="crawl_interval_minutes" label="间隔(分钟)" width="120" />
        <el-table-column prop="failure_count" label="失败" width="80" />
        <el-table-column label="最近成功" width="180">
          <template #default="{ row }">{{ formatDate(row.last_success_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="toggleSource(row)">{{ row.status === "enabled" ? "停用" : "启用" }}</el-button>
            <el-button size="small" type="primary" plain @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination layout="prev, pager, next, total" :total="total" :current-page="page" :page-size="pageSize" @current-change="load" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑来源' : '新增来源'" width="680px">
      <el-form :model="form" label-position="top">
        <el-row :gutter="14">
          <el-col :span="12"><el-form-item label="名称"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="类型"><el-select v-model="form.type"><el-option v-for="type in sourceTypes" :key="type" :label="type" :value="type" /></el-select></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="入口 URL"><el-input v-model="form.entry_url" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="域名"><el-input v-model="form.domain" placeholder="example.com" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status"><el-option v-for="status in sourceStatuses" :key="status" :label="status" :value="status" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="抓取间隔"><el-input-number v-model="form.crawl_interval_minutes" :min="30" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="域名延迟"><el-input-number v-model="form.domain_delay_seconds" :min="1" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="每日上限"><el-input-number v-model="form.daily_limit" :min="1" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="解析器"><el-input v-model="form.parser_key" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="每次页数"><el-input-number v-model="form.max_pages_per_run" :min="1" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, reactive, ref } from "vue";

import { createSource, listSources, updateSource } from "@/api/client";
import type { Source, SourcePayload, SourceStatus, SourceType } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";
import StatusPill from "@/components/StatusPill.vue";
import { formatDate } from "@/utils/format";

const sourceTypes: SourceType[] = ["announcement", "policy", "media", "paper", "patent", "rss", "webpage"];
const sourceStatuses: SourceStatus[] = ["enabled", "disabled", "manual_only", "blocked_by_policy"];
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editing = ref<Source | null>(null);
const sources = ref<Source[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const form = reactive<SourcePayload>(defaultForm());

function defaultForm(): SourcePayload {
  return {
    name: "",
    type: "rss",
    entry_url: "",
    domain: "",
    status: "disabled",
    crawl_interval_minutes: 360,
    parser_key: "generic",
    domain_delay_seconds: 3,
    max_pages_per_run: 20,
    daily_limit: 100,
    notes: ""
  };
}

function assignForm(payload: SourcePayload) {
  Object.assign(form, payload);
}

async function load(targetPage = page.value) {
  loading.value = true;
  try {
    page.value = targetPage;
    const result = await listSources(page.value, pageSize);
    sources.value = result.items;
    total.value = result.total;
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "来源加载失败");
  } finally {
    loading.value = false;
  }
}

function openEdit(row: Source) {
  editing.value = row;
  assignForm({
    name: row.name,
    type: row.type,
    entry_url: row.entry_url,
    domain: row.domain,
    status: row.status,
    crawl_interval_minutes: row.crawl_interval_minutes,
    parser_key: row.parser_key,
    domain_delay_seconds: row.domain_delay_seconds,
    max_pages_per_run: row.max_pages_per_run,
    daily_limit: row.daily_limit,
    notes: row.notes
  });
  dialogVisible.value = true;
}

function openCreate() {
  editing.value = null;
  assignForm(defaultForm());
  dialogVisible.value = true;
}

async function toggleSource(row: Source) {
  try {
    await updateSource(row.id, { status: row.status === "enabled" ? "disabled" : "enabled" });
    ElMessage.success("来源状态已更新");
    await load();
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "来源状态更新失败");
  }
}

async function save() {
  saving.value = true;
  try {
    if (editing.value) {
      await updateSource(editing.value.id, form);
    } else {
      await createSource(form);
    }
    ElMessage.success("来源已保存");
    dialogVisible.value = false;
    editing.value = null;
    assignForm(defaultForm());
    await load(1);
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "来源保存失败");
  } finally {
    saving.value = false;
  }
}

onMounted(() => load(1));
</script>
