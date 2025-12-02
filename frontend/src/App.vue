<script setup lang="ts">
import { onMounted } from 'vue';
import { useAppStore } from './stores/app';
import FullscreenToggle from './components/FullscreenToggle.vue';
import ClassesTable from './components/ClassesTable.vue';
import CoursesTable from './components/CoursesTable.vue';

const store = useAppStore();

onMounted(() => {
  store.fetchData();
  store.connectWebSocket();
});
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-top">
        <h1>Classes & Courses (Realtime)</h1>
        <FullscreenToggle />
      </div>
      <div class="status">
        <span class="dot" :class="store.isWsConnected ? 'dot--online' : 'dot--offline'" />
        <span>WebSocket: {{ store.isWsConnected ? 'Connected' : 'Disconnected' }}</span>
      </div>
    </header>

    <main>
      <div v-if="store.isLoading">Loading data...</div>
      <div v-else-if="store.error" class="error">{{ store.error }}</div>

      <section v-else class="tables">
        <ClassesTable
          :classes="store.classes"
          :courses="store.courses"
          @update-alias="store.updateClassAlias"
        />
        <CoursesTable
          :courses="store.courses"
          :classes="store.classes"
          @update-course-classes="store.updateCourseClassIds"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.app {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  background: radial-gradient(circle at top left, #eff6ff 0, #ffffff 45%);
}

.header {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1.5rem;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-top h1 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #0f172a;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #6b7280;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}
.dot--online {
  background: #16a34a;
}
.dot--offline {
  background: #b91c1c;
}

.error {
  color: #b91c1c;
}

.tables {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .tables {
    grid-template-columns: 1fr;
  }
}
</style>
