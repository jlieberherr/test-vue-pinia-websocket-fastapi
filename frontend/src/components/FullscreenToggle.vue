<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";

const isFullscreen = ref(false);

function toggleFullscreen() {
  const doc = window.document;
  const docEl = doc.documentElement;

  const requestFullScreen =
    docEl.requestFullscreen ||
    (docEl as any).webkitRequestFullScreen ||
    (docEl as any).mozRequestFullScreen ||
    (docEl as any).msRequestFullscreen;

  const cancelFullScreen =
    doc.exitFullscreen ||
    (doc as any).webkitExitFullscreen ||
    (doc as any).mozCancelFullScreen ||
    (doc as any).msExitFullscreen;

  if (!doc.fullscreenElement &&
      !(doc as any).webkitFullscreenElement &&
      !(doc as any).mozFullScreenElement &&
      !(doc as any).msFullscreenElement) {
    requestFullScreen.call(docEl);
  } else {
    cancelFullScreen.call(doc);
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement;
}

onMounted(() => {
  document.addEventListener("fullscreenchange", onFullscreenChange);
});

onUnmounted(() => {
  document.removeEventListener("fullscreenchange", onFullscreenChange);
});
</script>

<template>
  <button class="fullscreen-btn" @click="toggleFullscreen">
    <span v-if="isFullscreen">🔳 Exit Fullscreen</span>
    <span v-else>⛶ Fullscreen</span>
  </button>
</template>

<style scoped>
.fullscreen-btn {
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.fullscreen-btn:hover {
  background: #1d4ed8;
}
</style>
