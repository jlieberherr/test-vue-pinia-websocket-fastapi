<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const props = defineProps<{
  title: string;
  initialX?: number;
  initialY?: number;
}>();

const x = ref(props.initialX ?? 40);
const y = ref(props.initialY ?? 140);

const isDragging = ref(false);
let offsetX = 0;
let offsetY = 0;

function onMouseDownHeader(e: MouseEvent) {
  isDragging.value = true;
  offsetX = e.clientX - x.value;
  offsetY = e.clientY - y.value;

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
}

function onMouseMove(e: MouseEvent) {
  if (!isDragging.value) return;
  x.value = e.clientX - offsetX;
  y.value = e.clientY - offsetY;
}

function onMouseUp() {
  isDragging.value = false;
  document.removeEventListener('mousemove', onMouseMove);
  document.removeEventListener('mouseup', onMouseUp);
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove);
  document.removeEventListener('mouseup', onMouseUp);
});
</script>

<template>
  <div
    class="window"
    :style="{ left: x + 'px', top: y + 'px' }"
  >
    <div
      class="window-header"
      @mousedown="onMouseDownHeader"
    >
      <span class="window-title">{{ title }}</span>
      <span class="window-drag-hint">⇕ drag</span>
    </div>
    <div class="window-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.window {
  position: absolute;
  min-width: 280px;
  max-width: 460px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(148, 163, 184, 0.4);
  overflow: hidden;
  cursor: default;
}

.window-header {
  padding: 0.45rem 0.7rem;
  background: linear-gradient(135deg, #1d4ed8, #22c55e);
  color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  user-select: none;
  cursor: grab;
}

.window-header:active {
  cursor: grabbing;
}

.window-title {
  font-weight: 600;
}

.window-drag-hint {
  opacity: 0.8;
  font-size: 0.75rem;
}

.window-body {
  padding: 0.7rem;
  background: #f9fafb;
}
</style>
