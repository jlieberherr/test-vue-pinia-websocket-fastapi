<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useItemsStore } from './stores/items';

const store = useItemsStore();
const newItemTitle = ref('');

const sortedItems = computed(() =>
  [...store.items].sort((a, b) => a.title.localeCompare(b.title))
);

function onAddItem() {
  if (!newItemTitle.value.trim()) return;
  store.addItem(newItemTitle.value);
  newItemTitle.value = '';
}

onMounted(() => {
  store.fetchItems();
  store.connectWebSocket();
});
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>Realtime Todo (Vue 3 + FastAPI + MongoDB)</h1>
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

    <main>
      <section class="add-item">
        <input
          v-model="newItemTitle"
          type="text"
          placeholder="Add a new todo..."
          @keyup.enter="onAddItem"
        />
        <button @click="onAddItem">Add</button>
      </section>

      <section class="content">
        <div v-if="store.isLoading">Loading items...</div>
        <div v-else-if="store.error" class="error">
          {{ store.error }}
        </div>
        <ul v-else class="items">
          <li
            v-for="item in sortedItems"
            :key="item.id"
            :class="{ completed: item.completed }"
          >
            <label>
              <input
                type="checkbox"
                :checked="item.completed"
                @change="store.toggleItem(item)"
              />
              <span>{{ item.title }}</span>
            </label>
            <button class="delete" @click="store.deleteItem(item.id)">✕</button>
          </li>
        </ul>
      </section>
    </main>
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

.add-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.add-item input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.add-item button {
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  border: none;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

.add-item button:hover {
  background: #1d4ed8;
}

.content .error {
  color: #b91c1c;
}

.items {
  list-style: none;
  margin: 0;
  padding: 0;
}

.items li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0;
  border-bottom: 1px solid #eee;
}

.items li.completed span {
  text-decoration: line-through;
  color: #6b7280;
}

.items label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.delete {
  background: transparent;
  border: none;
  color: #b91c1c;
  cursor: pointer;
}
</style>
