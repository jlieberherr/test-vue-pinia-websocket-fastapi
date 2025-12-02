<script setup lang="ts">
import { onMounted } from 'vue';
import { useAppStore } from './stores/app';
import FullscreenToggle from './components/FullscreenToggle.vue';
import ClassesTable from './components/ClassesTable.vue';
import CoursesTable from './components/CoursesTable.vue';
import DraggableWindow from './components/DraggableWindow.vue';

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

    <main class="desktop">
      <div v-if="store.isLoading" class="overlay-msg">Loading data...</div>
      <div v-else-if="store.error" class="overlay-msg error">{{ store.error }}</div>

      <DraggableWindow
        v-else
        title="Classes"
        :initial-x="40"
        :initial-y="140"
      >
        <ClassesTable
          :classes="store.classes"
          :courses="store.courses"
          @update-alias="store.updateClassAlias"
        />
      </DraggableWindow>

      <DraggableWindow
        v-if="!store.isLoading && !store.error"
        title="Courses"
        :initial-x="520"
        :initial-y="180"
      >
        <CoursesTable
          :courses="store.courses"
          :classes="store.classes"
          @update-course-classes="store.updateCourseClassIds"
        />
      </DraggableWindow>
    </main>
  </div>
</template>

<style scoped>
.app {
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  padding: 1.2rem 1.5rem;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: radial-gradient(circle at top left, #eff6ff 0, #ffffff 45%, #e5e7eb 100%);
}

.header {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
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

/* "desktop" area where windows can move */
.desktop {
  position: relative;
  flex: 1;
  height: calc(100vh - 80px);
  margin-top: 0.75rem;
}

.overlay-msg {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  font-size: 0.95rem;
  z-index: 100;
  pointer-events: none;
}

.overlay-msg.error {
  color: #b91c1c;
}
</style>
