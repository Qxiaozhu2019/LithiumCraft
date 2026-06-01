<template>
  <div class="page-stack">
    <PageHeader eyebrow="Manufacturing Process" title="制造工艺知识库" description="按电芯制造全流程查看公开资料自动归类结果。" />

    <div v-if="loading" class="process-empty">正在加载工序目录...</div>
    <div v-else class="process-stage-grid">
      <RouterLink v-for="stage in stages" :key="stage.slug" class="process-stage-card" :to="`/processes/${stage.slug}`">
        <strong>{{ stage.name }}</strong>
        <p>{{ stage.description }}</p>
        <span>{{ stage.item_count }} 条相关公开资料</span>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onMounted, ref } from "vue";

import { listProcessStages } from "@/api/client";
import type { ProcessStage } from "@/api/types";
import PageHeader from "@/components/PageHeader.vue";

const loading = ref(false);
const stages = ref<ProcessStage[]>([]);

async function load() {
  loading.value = true;
  try {
    stages.value = await listProcessStages();
  } catch (err) {
    ElMessage.error(err instanceof Error ? err.message : "工序目录加载失败");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
