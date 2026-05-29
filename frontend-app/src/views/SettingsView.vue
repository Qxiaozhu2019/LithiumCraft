<template>
  <div class="page-stack">
    <PageHeader eyebrow="Settings" title="系统设置" description="维护抓取、摘要与运行参数；修改会直接写入后端系统配置。">
      <el-button @click="load" :loading="loading">刷新</el-button>
    </PageHeader>

    <el-card class="panel-card" shadow="never">
      <el-table :data="settings" v-loading="loading">
        <el-table-column prop="key" label="键" min-width="180" />
        <el-table-column label="值" min-width="240">
          <template #default="{ row }">
            <el-input v-model="row.value" type="textarea" :rows="2" />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="260" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }"><el-button type="primary" size="small" @click="save(row)">保存</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

import { listSettings, updateSetting } from "@/api/client";
import type { Setting } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";

const loading = ref(false);
const settings = ref<Setting[]>([]);

async function load() {
  loading.value = true;
  try {
    settings.value = await listSettings();
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "设置加载失败");
  } finally {
    loading.value = false;
  }
}

async function save(row: Setting) {
  try {
    const updated = await updateSetting(row.key, row.value);
    const index = settings.value.findIndex((item) => item.key === row.key);
    if (index >= 0) settings.value[index] = updated;
    ElMessage.success("设置已保存");
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "设置保存失败");
  }
}

onMounted(load);
</script>
