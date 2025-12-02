<script setup lang="ts">
import { defineProps, defineEmits, ref, onUnmounted } from 'vue';
import BaseTable from './BaseTable.vue';
import type { Class, Course } from '../stores/app';

const props = defineProps<{
  classes: Class[];
  courses: Course[];
}>();

const emit = defineEmits<{
  (e: 'update-alias', id: string, alias: string): void;
}>();

function getCourseSubjectsForClass(classId: string): string {
  return props.courses
    .filter(course => course.class_ids.includes(classId))
    .map(course => course.subject)
    .join(', ');
}

// ---- Excel-like editing state ----
const editingClassId = ref<string | null>(null);
const editingAliasDraft = ref('');
const selectedClassId = ref<string | null>(null);

function enterEditMode(cls: Class) {
  editingClassId.value = cls.id;
  editingAliasDraft.value = cls.alias;
  selectedClassId.value = cls.id;
}

function exitEditMode(commit: boolean) {
  if (!editingClassId.value) return;
  const id = editingClassId.value;
  const original = props.classes.find(c => c.id === id);
  if (!original) {
    editingClassId.value = null;
    return;
  }

  if (commit && editingAliasDraft.value !== original.alias) {
    emit('update-alias', id, editingAliasDraft.value.trim());
  }

  editingClassId.value = null;
}

function onAliasCellClick(cls: Class) {
  selectedClassId.value = cls.id;
}

function onAliasCellDblClick(cls: Class) {
  enterEditMode(cls);
}

function onAliasInputKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault();
    exitEditMode(true);
  } else if (e.key === 'Escape') {
    e.preventDefault();
    exitEditMode(false);
  }
}

// ---- Column resizing ----
type ColumnKey = 'alias' | 'courses';

const columnWidths = ref<Record<ColumnKey, number>>({
  alias: 90,
  courses: 160,
});

const resizingColumn = ref<ColumnKey | null>(null);
let startX = 0;
let startWidth = 0;

const MIN_WIDTH = 60;

function onMouseDownResizer(column: ColumnKey, e: MouseEvent) {
  resizingColumn.value = column;
  startX = e.clientX;
  startWidth = columnWidths.value[column];

  document.addEventListener('mousemove', onMouseMoveResize);
  document.addEventListener('mouseup', onMouseUpResize);
}

function onMouseMoveResize(e: MouseEvent) {
  if (!resizingColumn.value) return;

  const deltaX = e.clientX - startX;
  const newWidth = Math.max(MIN_WIDTH, startWidth + deltaX);
  columnWidths.value[resizingColumn.value] = newWidth;
}

function onMouseUpResize() {
  resizingColumn.value = null;
  document.removeEventListener('mousemove', onMouseMoveResize);
  document.removeEventListener('mouseup', onMouseUpResize);
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMoveResize);
  document.removeEventListener('mouseup', onMouseUpResize);
});
</script>

<template>
  <BaseTable>
    <template #title>Classes</template>

    <template #head>
      <tr>
        <th>ID</th>

        <th
          class="resizable-th"
          :style="{ width: columnWidths.alias + 'px' }"
        >
          <div class="th-inner">
            <span>Alias</span>
            <span
              class="col-resizer"
              @mousedown.stop="onMouseDownResizer('alias', $event)"
            />
          </div>
        </th>

        <th
          class="resizable-th"
          :style="{ width: columnWidths.courses + 'px' }"
        >
          <div class="th-inner">
            <span>Courses</span>
            <span
              class="col-resizer"
              @mousedown.stop="onMouseDownResizer('courses', $event)"
            />
          </div>
        </th>
      </tr>
    </template>

    <template #body>
      <tr v-for="cls in classes" :key="cls.id">
        <td>{{ cls.id }}</td>

        <!-- Alias cell, Excel-like edit -->
        <td
          class="alias-cell"
          :style="{ width: columnWidths.alias + 'px' }"
          :class="{
            'cell-selected': selectedClassId === cls.id && editingClassId !== cls.id
          }"
          @click="onAliasCellClick(cls)"
          @dblclick.stop="onAliasCellDblClick(cls)"
        >
          <template v-if="editingClassId === cls.id">
            <input
              v-model="editingAliasDraft"
              class="alias-input editing"
              @keydown="onAliasInputKeydown"
              @blur="exitEditMode(true)"
              autofocus
            />
          </template>
          <template v-else>
            <div class="cell-display">
              {{ cls.alias }}
            </div>
          </template>
        </td>

        <!-- Courses subjects -->
        <td
          class="courses-cell"
          :style="{ width: columnWidths.courses + 'px' }"
        >
          {{ getCourseSubjectsForClass(cls.id) || '—' }}
        </td>
      </tr>
    </template>
  </BaseTable>
</template>

<style scoped>
.resizable-th {
  position: relative;
}

.th-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
}

.col-resizer {
  width: 5px;
  align-self: stretch;
  cursor: col-resize;
  display: inline-block;
  margin-left: 4px;
  border-radius: 999px;
}

.col-resizer::before {
  content: '';
  display: block;
  width: 2px;
  height: 100%;
  background: #cbd5f5;
}

.col-resizer:hover::before {
  background: #2563eb;
}

/* Excel-like cells */
.alias-cell,
.courses-cell {
  box-sizing: border-box;
  padding: 0;
}

.cell-display {
  padding: 0.15rem 0.3rem;
  border: 1px solid transparent;
  border-radius: 3px;
  min-height: 1.6rem;
  display: flex;
  align-items: center;
}

.alias-cell:hover .cell-display {
  border-color: #e5e7eb;
}

.cell-selected .cell-display {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.alias-input {
  width: 100%;
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
  border: 1px solid #2563eb;
  font-size: 0.8rem;
  outline: none;
  box-sizing: border-box;
}

.alias-input.editing {
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.courses-cell {
  padding: 0.15rem 0.3rem;
  color: #475569;
  font-size: 0.85rem;
}
</style>
