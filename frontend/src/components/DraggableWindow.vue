<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const props = defineProps<{
  title: string;
  initialX?: number;
  initialY?: number;
  initialWidth?: number;
  initialHeight?: number;
}>();

const x = ref(props.initialX ?? 40);
const y = ref(props.initialY ?? 140);
const width = ref(props.initialWidth ?? 420);
const height = ref(props.initialHeight ?? 260);

const isDragging = ref(false);
const isResizing = ref(false);

let dragOffsetX = 0;
let dragOffsetY = 0;
let resizeStartX = 0;
let resizeStartY = 0;
let startWidth = 0;
let startHeight = 0;

const MIN_WIDTH = 260;
const MIN_HEIGHT = 160;

// --- drag logic ---

function onMouseDownHeader(e: MouseEvent) {
  // ignore if a resize is active
  if (isResizing.value) return;

  isDragging.value = true;
  dragOffsetX = e.clientX - x.value;
  dragOffsetY = e.clientY - y.value;

  document.addEventListener('mousemove', onMouseMoveDrag);
  document.addEventListener('mouseup', onMouseUpDrag);
}

function onMouseMoveDrag(e: MouseEvent) {
  if (!isDragging.value) return;
  x.value = e.clientX - dragOffsetX;
  y.value = e.clientY - dragOffsetY;
}

function onMouseUpDrag() {
  isDragging.value = false;
  document.removeEventListener('mousemove', onMouseMoveDrag);
  document.removeEventListener('mouseup', onMouseUpDrag);
}

// --- resize logic (bottom-right corner) ---

function onMouseDownResize(e: MouseEvent) {
  e.stopPropagation();
  isResizing.value = true;

  resizeStartX = e.clientX;
  resizeStartY = e.clientY;
  startWidth = width.value;
  startHeight = height.value;

  document.addEventListener('mousemove', onMouseMoveResize);
  document.addEventListener('mouseup', onMouseUpResize);
}

function onMouseMoveResize(e: MouseEvent) {
  if (!isResizing.value) return;

  const deltaX = e.clientX - resizeStartX;
  const deltaY = e.clientY - resizeStartY;

  const newWidth = Math.max(MIN_WIDTH, startWidth + deltaX);
  const newHeight = Math.max(MIN_HEIGHT, startHeight + deltaY);

  width.value = newWidth;
  height.value = newHeight;
}

function onMouseUpResize() {
  isResizing.value = false;
  document.removeEventListener('mousemove', onMouseMoveResize);
  document.removeEventListener('mouseup', onMouseUpResize);
}

// --- cleanup ---

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMoveDrag);
  document.removeEventListener('mouseup', onMouseUpDrag);
  document.removeEventListener('mousemove', onMouseMoveResize);
  document.removeEventListener('mouseup', onMouseUpResize);
});
</script>

<template>
  <div
    class="window"
    :style="{
      left: x + 'px',
      top: y + 'px',
      width: width + 'px',
      height: height + 'px'
    }"
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
    <div
      class="resize-handle"
      @mousedown="onMouseDownResize"
    />
  </div>
</template>

<style scoped>
.window {
  position: absolute;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(148, 163, 184, 0.4);
  overflow: hidden;
  cursor: default;
  display: flex;
  flex-direction: column;
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
  flex: 1;
  padding: 0.7rem;
  background: #f9fafb;
  overflow: auto; /* scroll if table content gets larger than window */
}

/* bottom-right resize handle */
.resize-handle {
  position: absolute;
  width: 14px;
  height: 14px;
  right: 4px;
  bottom: 4px;
  border-radius: 3px;
  border: 1px solid #9ca3af;
  background: linear-gradient(135deg, #e5e7eb, #ffffff);
  cursor: se-resize;
  box-shadow: 0 0 0 1px #e5e7eb;
}
</style>
