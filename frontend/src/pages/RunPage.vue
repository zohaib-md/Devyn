<template>
  <div>
    <router-link to="/" class="text-sm text-blue-600 hover:underline">← New research</router-link>
    <div v-if="loading && !run" class="mt-6">Loading…</div>
    <div v-else-if="run">
      <h1 class="mt-2 text-2xl font-bold">{{ run.topic }}</h1>
      <p v-if="isRunning" class="mt-2 text-gray-600 dark:text-gray-400">{{ stepText }}</p>

      <div v-if="run.status === 'failed'" class="mt-6 rounded-lg border border-red-300 p-4">
        <p class="font-medium text-red-700">Research failed</p>
        <p class="mt-1 text-sm">{{ run.error || "Unknown error" }}</p>
        <button
          @click="retry"
          :disabled="retrying"
          class="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {{ retrying ? "Retrying…" : "Try again" }}
        </button>
      </div>

      <div v-if="run.status === 'done' && run.report" class="mt-6 space-y-8">
        <section>
          <h2 class="text-xl font-semibold">Trends</h2>
          <div v-for="t in run.report.trends" :key="t.title" class="mt-3 rounded-lg border border-gray-200 p-4 dark:border-gray-800">
            <p class="font-medium">{{ t.title }}</p>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{{ t.why_now }}</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <CiteChip v-for="id in t.source_ids" :key="id" :id="id" :sources="run.sources" />
            </div>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-semibold">What to learn</h2>
          <div v-for="l in run.report.learn" :key="l.skill" class="mt-3 rounded-lg border border-gray-200 p-4 dark:border-gray-800">
            <p class="font-medium">{{ l.skill }}</p>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{{ l.why }}</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <CiteChip v-for="id in l.source_ids" :key="id" :id="id" :sources="run.sources" />
            </div>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-semibold">Roadmap</h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="w in run.report.roadmap" :key="w.week" class="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
              <p class="font-medium">Week {{ w.week }} — {{ w.goal }}</p>
              <ul class="mt-2 list-disc pl-5 text-sm">
                <li v-for="task in w.tasks" :key="task">{{ task }}</li>
              </ul>
              <div class="mt-2 flex flex-wrap gap-2">
                <CiteChip v-for="id in w.resource_ids" :key="id" :id="id" :sources="run.sources" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { createRun, getRun } from "../api.js";
import CiteChip from "../components/CiteChip.vue";

const props = defineProps({ id: String });
const run = ref(null);
const loading = ref(true);
const retrying = ref(false);
const router = useRouter();
let timer = null;

const isRunning = computed(() => run.value && !["done", "failed"].includes(run.value.status));
const stepText = computed(() => {
  const s = run.value?.status;
  if (s === "queued" || s === "planning") return "Planning searches…";
  if (s === "researching") return "Researching sources…";
  if (s === "writing") return "Writing your roadmap…";
  return "Working…";
});

async function fetchRun() {
  try {
    run.value = await getRun(props.id);
  } catch {
    // keep polling; run may not exist yet
  } finally {
    loading.value = false;
  }
  if (run.value && ["done", "failed"].includes(run.value.status) && timer) {
    clearInterval(timer);
    timer = null;
  }
}

async function retry() {
  retrying.value = true;
  try {
    const r = await createRun(run.value.topic);
    router.push(`/runs/${r.id}`);
  } finally {
    retrying.value = false;
  }
}

function startPolling() {
  if (timer) clearInterval(timer);
  timer = setInterval(fetchRun, 2000);
}

watch(
  () => props.id,
  async () => {
    run.value = null;
    loading.value = true;
    await fetchRun();
    startPolling();
  }
);

onMounted(async () => {
  await fetchRun();
  startPolling();
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
