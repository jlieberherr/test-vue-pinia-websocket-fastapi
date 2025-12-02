<script setup lang="ts">
import { defineProps, defineEmits, ref, onUnmounted } from 'vue';
import BaseTable from './BaseTable.vue';
import type { Class, Course } from '../stores/app';

const props = defineProps<{
  courses: Course[];
  classes: Class[];
}>();

const emit = defineEmits<{
  (e: 'update-course-classes', courseId: string, classIds: string[]): void;
  (e: 'update-course-subject', courseId: string, subject: string): void;
}>();

// --- Excel-like editing for subject ---
const editingSubjectCourseId = ref<string | null>(null);
const subjectDraft = ref('');
const selectedSubjectCourseId = ref<string | null>(null);

function enterSubjectEdit(course: Course) {
  editingSubjectCourseId.value = course.id;
  subjectDraft.value = course.subject;
  selectedSubjectCourseId.value = course.id;
}

function exitSubjectEdit(commit: boolean) {
  const id = editingSubjectCourseId.value;
  if (!id) return;

  const original = props.courses.find(c => c.id === id);
  if (!original) {
    editingSubjectCourseId.value = null;
    return;
  }

  if (commit && subjectDraft.value !== original.subject) {
    emit('update-course-subject', id, subjectDraft.value.trim());
  }

  editingSubjectCourseId.value = null;
}

function onSubjectCellClick(course: Course) {
  selectedSubjectCourseId.value = course.id;
}

function onSubjectCellDblClick(course: Course) {
  enterSubjectEdit(course);
}

function onSubjectInputKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault();
    exitSubjectEdit(true);
  } else if (e.key === 'Escape') {
    e.preventDefault();
    exitSubjectEdit(false);
  }
}

// --- Classes aliases (same as before) ---
const editingCourseId = ref<string | null>(null);

function startEditingClasses(courseId: string) {
  editingCourseId.value = courseId;
}

function stopEditingClasses() {
  editingCourseId.value = null;
}

function onCourseClassesChange(event: Event, courseId: string) {
  const target = event.target as HTMLSelectElement;
  const selectedIds = Array.from(target.selectedOptions).map(opt => opt.value);
  emit('update-course-classes', courseId, selectedIds);
}

function getClassAliases(course: Course): string {
  return course.class_ids
    .map(id => props.classes.find(c => c.id === id)?.alias)
    .filter((alias): alias is string => !!alias)
    .join(', ');
}

// ---- Column resizing ----
type ColumnKey = 'subject' | 'aliases';

const columnWidths = ref<Record<ColumnKey, number>>({
  subject: 80,
  aliases: 200,
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
    <template #title>Courses</template>

    <template #head>
      <tr>
        <th>ID</th>

        <th
          class="resizable-th"
          :style="{ width: columnWidths.subject + 'px' }"
        >
          <div class="th-inner">
            <span>Subject</span>
            <span
              class="col-resizer"
              @mousedown.stop="onMouseDownResizer('subject', $event)"
            />
          </div>
        </th>

        <th
          class="resizable-th"
          :style="{ width: columnWidths.aliases + 'px' }"
        >
          <div class="th-inner">
            <span>Classes (aliases)</span>
            <span
              class="col-resizer"
              @mousedown.stop="onMouseDownResizer('aliases', $event)"
            />
          </div>
        </th>
      </tr>
    </template>

    <template #body>
      <tr v-for="course in courses" :key="course.id">
        <td>{{ course.id }}</td>

        <!-- Subject cell, Excel-like edit -->
        <td
          :style="{ width: columnWidths.subject + 'px' }"
          class="subject-cell"
          :class="{
            'cell-selected': selectedSubjectCourseId === course.id && editingSubjectCourseId !== course.id
          }"
          @click="onSubjectCellClick(course)"
          @dblclick.stop="onSubjectCellDblClick(course)"
        >
          <template v-if="editingSubjectCourseId === course.id">
            <input
              v-model="subjectDraft"
              class="subject-input"
              @keydown="onSubjectInputKeydown"
              @blur="exitSubjectEdit(true)"
              autofocus
            />
          </template>
          <template v-else>
            <div class="cell-display">
              {{ course.subject }}
            </div>
          </template>
        </td>

        <!-- Aliases cell with inline edit button as before -->
        <td
          class="aliases-cell"
          :style="{ width: columnWidths.aliases + 'px' }"
        >
          <!-- display mode -->
          <div
            v-if="editingCourseId !== course.id"
            class="aliases-view"
          >
            <span>{{ getClassAliases(course) || '—' }}</span>
            <button
              class="edit-classes-btn"
              type="button"
              @click.stop="startEditingClasses(course.id)"
              title="Edit classes"
            >
              ✎
            </button>
          </div>

          <!-- edit mode -->
          <div
            v-else
            class="aliases-edit"
          >
            <select
              multiple
              :value="course.class_ids"
              @change="onCourseClassesChange($event, course.id)"
              class="class-multiselect"
            >
              <option
                v-for="cls in classes"
                :key="cls.id"
                :value="cls.id"
              >
                {{ cls.alias }}
              </option>
            </select>
            <button
              class="done-btn"
              type="button"
              @click="stopEditingClasses"
            >
              Done
            </button>
          </div>
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

/* Excel-like cell styling */
.subject-cell {
  padding: 0;
  box-sizing: border-box;
}

.cell-display {
  padding: 0.15rem 0.3rem;
  border: 1px solid transparent;
  border-radius: 3px;
  min-height: 1.6rem;
  display: flex;
  align-items: center;
}

.subject-cell:hover .cell-display {
  border-color: #e5e7eb;
}

.cell-selected .cell-display {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.subject-input {
  width: 100%;
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
  border: 1px solid #2563eb;
  font-size: 0.85rem;
  outline: none;
  box-sizing: border-box;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.aliases-cell {
  color: #334155;
  font-size: 0.85rem;
}

.aliases-view {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
}

.edit-classes-btn {
  border: none;
  background: transparent;
  padding: 0.1rem 0.25rem;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.8rem;
  line-height: 1;
  color: #4b5563;
  transition: background 0.15s, color 0.15s;
}

.edit-classes-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.aliases-edit {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.class-multiselect {
  width: 100%;
  min-height: 2.4rem;
  padding: 0.25rem;
  border-radius: 6px;
  border: 1px solid #cbd5f5;
  font-size: 0.85rem;
  outline: none;
  background-color: #ffffff;
}

.class-multiselect:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.done-btn {
  border: none;
  background: #2563eb;
  color: #f9fafb;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.done-btn:hover {
  background: #1d4ed8;
}
</style>
