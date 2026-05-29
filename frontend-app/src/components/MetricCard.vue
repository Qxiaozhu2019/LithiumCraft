<template>
  <section class="metric-card" :class="tone">
    <div>
      <p>{{ label }}</p>
      <strong>{{ value }}</strong>
    </div>
    <span>{{ hint }}</span>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  hint: string;
  tone?: "amber" | "green" | "red" | "blue";
}>();
</script>
