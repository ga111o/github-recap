<script setup lang="ts">
import { ref } from "vue";

interface Repository {
  name: string;
  html_url: string;
  private: boolean;
  updated_at: string;
}

interface Progress {
  type: string;
  current?: number;
  total?: number;
  repository?: string;
  message?: string;
  success?: boolean;
  commit_sha?: string;
  current_commit?: number;
  total_commits?: number;
  total_commits_found?: number;
}

const repository = ref<Repository>({
  name: "langchain",
  html_url: "https://github.com/ga111o/langchain",
  private: true,
  updated_at: "2024-06-01T12:10:23Z",
});

const progress = ref<Progress | null>(null);
const isLoading = ref(false);

const saveRepository = async () => {
  isLoading.value = true;
  progress.value = null;

  try {
    const response = await fetch(
      `http://localhost:8000/save/ga111o/specific/2023/12`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-GitHub-Token": import.meta.env.VITE_GITHUB_TOKEN,
        },
        body: JSON.stringify({ repository: repository.value }),
      }
    );

    const reader = response.body?.getReader();
    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = new TextDecoder().decode(value);
      const lines = text.split("\n").filter((line) => line);

      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          console.log("Received progress:", data);
          progress.value = data;
        } catch (e) {
          console.error("Failed to parse progress data:", e, line);
        }
      }
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="container">
    <div class="form">
      <div class="form-group">
        <label>Repository Name:</label>
        <input v-model="repository.name" type="text" />
      </div>

      <div class="form-group">
        <label>Repository URL:</label>
        <input v-model="repository.html_url" type="text" />
      </div>

      <div class="form-group">
        <label>Private:</label>
        <input v-model="repository.private" type="checkbox" />
      </div>

      <div class="form-group">
        <label>Updated At:</label>
        <input v-model="repository.updated_at" type="text" />
      </div>

      <button @click="saveRepository" :disabled="isLoading">
        {{ isLoading ? "Processing..." : "Save Repository" }}
      </button>
    </div>

    <div v-if="progress" class="progress-container">
      <div v-if="progress.type === 'progress'" class="progress-bar">
        <div class="progress-info">
          <span>Repository: {{ progress.repository }}</span>
          <span>{{ progress.message }}</span>
          <span>Progress: {{ progress.current }}/{{ progress.total }}</span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="`width: ${(progress.current! / progress.total! * 100)}%`"
          ></div>
        </div>
      </div>

      <div
        v-else-if="progress.type === 'processing_commit'"
        class="progress-bar"
      >
        <div class="progress-info">
          <span>Repository: {{ progress.repository }}</span>
          <span>Commit: {{ progress.commit_sha }}</span>
          <span
            >Progress: {{ progress.current_commit }}/{{
              progress.total_commits
            }}</span
          >
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="`width: ${(progress.current_commit! / progress.total_commits! * 100)}%`"
          ></div>
        </div>
      </div>

      <div v-else-if="progress.type === 'fetching_commits'" class="status info">
        Found {{ progress.total_commits_found }} commits in
        {{ progress.repository }}
      </div>

      <div v-else-if="progress.type === 'complete'" class="status success">
        {{ progress.message }}
      </div>

      <div v-else-if="progress.type === 'error'" class="status error">
        {{ progress.message }}
      </div>

      <div v-else-if="progress.type === 'skip'" class="status skip">
        {{ progress.message }}
      </div>
    </div>
  </div>
</template>

<style scoped></style>
