<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import BaseTable from './BaseTable.vue';
import type { Class, Course } from '../stores/app';

const props = defineProps<{
  courses: Course[];
  classes: Class[];
}>();

const emit = defineEmits<{
  (e: 'update-course-classes', courseId: string, classIds: string[]): void;
}>();

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
        <th>Edit classes</th>
      </tr>
    </template>

    <template #body>
      <tr v-for="course in courses" :key="course.id">
        <td>{{ course.id }}</td>
        <td>{{ course.subject }}</td>
        <td class="aliases-cell">
          {{ getClassAliases(course) || '—' }}
        </td>
        <td>
          <select
            multiple
            :value="course.class_ids"
            @change="onCourseClassesChange($event, course.id)"
            class="class-multiselect"
          >
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.alias }}
            </option>
          </select>
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
</style>
