import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Item {
  id: string;
  title: string;
  completed: boolean;
}

interface ItemsMessage {
  type: string;
  payload: Item[];
}

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

export const useItemsStore = defineStore('items', () => {
  const items = ref<Item[]>([]);
  const isWsConnected = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  let socket: WebSocket | null = null;
  let reconnectTimeout: number | null = null;

  async function fetchItems() {
    isLoading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/items`);
      if (!res.ok) {
        throw new Error(`Failed to fetch items: ${res.statusText}`);
      }
      const data: Item[] = await res.json();
      items.value = data;
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    } finally {
      isLoading.value = false;
    }
  }

  function connectWebSocket() {
    if (socket || isWsConnected.value) return;

    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      isWsConnected.value = true;
      error.value = null;
      console.log('WebSocket connected');
    };

    socket.onmessage = (event: MessageEvent) => {
      try {
        const msg: ItemsMessage = JSON.parse(event.data);
        if (msg.type === 'items_updated') {
          items.value = msg.payload;
        }
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    socket.onclose = () => {
      isWsConnected.value = false;
      socket = null;
      console.warn('WebSocket closed, will try to reconnect...');
      if (reconnectTimeout !== null) {
        window.clearTimeout(reconnectTimeout);
      }
      reconnectTimeout = window.setTimeout(() => connectWebSocket(), 2000);
    };

    socket.onerror = (event) => {
      console.error('WebSocket error', event);
      error.value = 'WebSocket error';
    };
  }

  function disconnectWebSocket() {
    if (socket) {
      socket.close();
      socket = null;
      isWsConnected.value = false;
    }
  }

  async function addItem(title: string) {
    const trimmed = title.trim();
    if (!trimmed) return;

    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: trimmed, completed: false }),
      });
      if (!res.ok) {
        throw new Error(`Failed to add item: ${res.statusText}`);
      }
      // The actual list will be updated via WebSocket broadcast
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    }
  }

  async function toggleItem(item: Item) {
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/items/${item.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !item.completed }),
      });
      if (!res.ok) {
        throw new Error(`Failed to update item: ${res.statusText}`);
      }
      // WebSocket will push the new list
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    }
  }

  async function deleteItem(itemId: string) {
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/items/${itemId}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        throw new Error(`Failed to delete item: ${res.statusText}`);
      }
      // WebSocket will push the new list
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    }
  }

  return {
    items,
    isWsConnected,
    isLoading,
    error,
    fetchItems,
    connectWebSocket,
    disconnectWebSocket,
    addItem,
    toggleItem,
    deleteItem,
  };
});
