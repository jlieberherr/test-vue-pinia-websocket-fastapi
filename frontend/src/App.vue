<script setup lang="ts">
import { onMounted } from 'vue';
import { useItemsStore } from './stores/items';
import TodoList from './components/TodoList.vue';

const store = useItemsStore();

onMounted(() => {
  store.fetchItems();
  store.connectWebSocket();
});
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>Realtime Todo (Vue 3 + FastAPI + MongoDB)!</h1>
      <div class="status">
        <span
          class="dot"
          :class="store.isWsConnected ? 'dot--online' : 'dot--offline'"
        ></span>
        <span>
          WebSocket: {{ store.isWsConnected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
    </header>

    <TodoList />
    <br />
    <TodoList />
  </div>
</template>

<style scoped>
.app {
  max-width: 640px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
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
</style>