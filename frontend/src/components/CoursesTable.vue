<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue';
import BaseTable from './BaseTable.vue';
import type { Class, Course } from '../stores/app';

const props = defineProps<{
  courses: Course[];
  classes: Class[];
}>();

const emit = defineEmits<{
  (e: 'update-course-classes', courseId: string, classIds: string[]): void;
}>();

// which course is currently being edited
const editingCourseId = ref<string | null>(null);

function startEditing(courseId: string) {
  editingCourseId.value = courseId;
}

function stopEditing() {
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
</script>

<template>
  <BaseTable>
    <template #title>Courses</template>

    <template #head>
      <tr>
        <th>ID</th>
        <th>Subject</th>
        <th>Classes (aliases)</th>
      </tr>
    </template>

    <template #body>
      <tr v-for="course in courses" :key="course.id">
        <td>{{ course.id }}</td>
        <td>{{ course.subject }}</td>
        <td class="aliases-cell">
          <!-- display mode -->
          <div
            v-if="editingCourseId !== course.id"
            class="aliases-view"
          >
            <span>{{ getClassAliases(course) || '—' }}</span>
            <button
              class="edit-classes-btn"
              type="button"
              @click.stop="startEditing(course.id)"
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
              @click="stopEditing"
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
