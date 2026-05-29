<template>
  <el-tag :type="tagType" effect="dark" round>{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ status: string }>();

const labels: Record<string, string> = {
  active: "可用",
  blocked: "拦截",
  archived: "归档",
  enabled: "启用",
  disabled: "停用",
  manual_only: "手动",
  blocked_by_policy: "策略阻断",
  pending: "等待",
  running: "运行中",
  success: "成功",
  failed: "失败",
  skipped: "跳过"
};

const types: Record<string, "success" | "warning" | "danger" | "info" | "primary"> = {
  active: "success",
  enabled: "success",
  success: "success",
  running: "primary",
  pending: "warning",
  manual_only: "warning",
  archived: "info",
  disabled: "info",
  skipped: "info",
  blocked: "danger",
  failed: "danger",
  blocked_by_policy: "danger"
};

const label = computed(() => labels[props.status] || props.status);
const tagType = computed(() => types[props.status] || "info");
</script>
