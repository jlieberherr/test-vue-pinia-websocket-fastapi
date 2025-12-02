<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useAppStore } from './stores/app';
import FullscreenToggle from './components/FullscreenToggle.vue'; // if you still use it

const store = useAppStore();

onMounted(() => {
  store.fetchData();
  store.connectWebSocket();
});

// Map course.class_ids -> "C1, C2" etc.
const coursesWithClassAliases = computed(() =>
  store.courses.map(course => {
    const aliases = course.class_ids
      .map(id => store.classes.find(c => c.id === id)?.alias)
      .filter((a): a is string => !!a);
    return {
      ...course,
      classAliases: aliases.join(', '),
    };
  })
);

// handle multiselect change
function onCourseClassesChange(event: Event, courseId: string) {
  const target = event.target as HTMLSelectElement;
  const selectedIds = Array.from(target.selectedOptions).map(opt => opt.value);
  store.updateCourseClassIds(courseId, selectedIds);
}

// handle alias change (on blur or change)
function onAliasChange(classId: string, alias: string) {
  store.updateClassAlias(classId, alias);
}
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

      <section class="tables" v-else>
        <!-- Classes table -->
        <div class="table-wrapper">
          <h2>Classes</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Alias</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cls in store.classes" :key="cls.id">
                <td>{{ cls.id }}</td>
                <td>
                  <input
                    v-model="cls.alias"
                    @change="onAliasChange(cls.id, cls.alias)"
                    class="alias-input"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Courses table -->
        <div class="table-wrapper">
          <h2>Courses</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Subject</th>
                <th>Classes (aliases)</th>
                <th>Edit classes</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in coursesWithClassAliases" :key="course.id">
                <td>{{ course.id }}</td>
                <td>{{ course.subject }}</td>
                <td>{{ course.classAliases }}</td>
                <td>
                  <select
                    multiple
                    :value="course.class_ids"
                    @change="onCourseClassesChange($event, course.id)"
                    class="class-multiselect"
                  >
                    <option v-for="cls in store.classes" :key="cls.id" :value="cls.id">
                      {{ cls.alias }}
                    </option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.app {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  border-radius: 8px;
  border: 1px solid #ddd;
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

.status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
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

.table-wrapper h2 {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th, td {
  border: 1px solid #eee;
  padding: 0.4rem 0.5rem;
  text-align: left;
}

.alias-input {
  width: 100%;
  padding: 0.2rem 0.3rem;
}

.class-multiselect {
  width: 100%;
  min-height: 2.5rem;
}
</style>
