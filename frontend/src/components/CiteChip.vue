<template>
  <a
    v-if="source"
    :href="source.url"
    target="_blank"
    rel="noopener noreferrer"
    class="inline-block rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
    :title="source.title"
  >
    {{ source.domain || source.source }}
  </a>
  <span v-else class="inline-block rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500">
    #{{ id }}
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ id: [Number, String], sources: Object });
const source = computed(() => props.sources?.[String(props.id)]);
</script>
