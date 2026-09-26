<template>
  <div>
    <h1 class="text-3xl font-bold">Devyn</h1>
    <p class="mt-2 text-gray-600 dark:text-gray-400">
      Research what's trending in any tech topic, and get a learning roadmap.
    </p>
    <form @submit.prevent="submit" class="mt-6 flex flex-col gap-3 sm:flex-row">
      <input
        v-model="topic"
        type="text"
        placeholder="e.g. Android + AI"
        maxlength="200"
        class="flex-1 rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-700 dark:bg-gray-900"
      />
      <button
        type="submit"
        :disabled="loading"
        class="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white disabled:opacity-50"
      >
        {{ loading ? "Starting…" : "Research" }}
      </button>
    </form>
    <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { createRun } from "../api.js";

const topic = ref("");
const loading = ref(false);
const error = ref("");
const router = useRouter();

async function submit() {
  error.value = "";
  const t = topic.value.trim();
  if (t.length < 2 || t.length > 200) {
    error.value = "Topic must be 2–200 characters.";
    return;
  }
  loading.value = true;
  try {
    const run = await createRun(t);
    router.push(`/runs/${run.id}`);
  } catch (e) {
    error.value = e.body ? JSON.stringify(e.body) : e.message;
  } finally {
    loading.value = false;
  }
}
</script>
