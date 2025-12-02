import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Class {
  id: string;
  alias: string;
}

export interface Course {
  id: string;
  subject: string;
  class_ids: string[]; // references Class.id
}

interface DataPayload {
  classes: Class[];
  courses: Course[];
}

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

export const useAppStore = defineStore('app', () => {
  const classes = ref<Class[]>([]);
  const courses = ref<Course[]>([]);

  const isWsConnected = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  let socket: WebSocket | null = null;
  let reconnectTimeout: number | null = null;

  // --- REST: fetch all data ---

  async function fetchData() {
    isLoading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/data`);
      if (!res.ok) throw new Error(`Failed to fetch data: ${res.statusText}`);
      const data: DataPayload = await res.json();
      classes.value = data.classes;
      courses.value = data.courses;
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    } finally {
      isLoading.value = false;
    }
  }

  // --- update operations ---

  async function updateClassAlias(classId: string, alias: string) {
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/classes/${classId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alias }),
      });
      if (!res.ok) throw new Error(`Failed to update class: ${res.statusText}`);
      // new data will come via WebSocket broadcast
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    }
  }

  async function updateCourseClassIds(courseId: string, classIds: string[]) {
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/courses/${courseId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_ids: classIds }),
      });
      if (!res.ok) throw new Error(`Failed to update course: ${res.statusText}`);
      // new data will come via WebSocket broadcast
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error';
    }
  }

  // --- WebSocket ---

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
        const msg = JSON.parse(event.data) as {
          type: string;
          payload: DataPayload;
        };

        if (msg.type === 'data_updated') {
          classes.value = msg.payload.classes;
          courses.value = msg.payload.courses;
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

  return {
    classes,
    courses,
    isWsConnected,
    isLoading,
    error,
    fetchData,
    updateClassAlias,
    updateCourseClassIds,
    connectWebSocket,
    disconnectWebSocket,
  };
});
