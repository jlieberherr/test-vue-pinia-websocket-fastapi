<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import BaseTable from './BaseTable.vue';
import type { Class, Course } from '../stores/app';

const props = defineProps<{
  classes: Class[];
  courses: Course[];
}>();

const emit = defineEmits<{
  (e: 'update-alias', id: string, alias: string): void;
}>();

function onAliasChange(classId: string, alias: string) {
  emit('update-alias', classId, alias);
}

function getCourseSubjectsForClass(classId: string): string {
  return props.courses
    .filter(course => course.class_ids.includes(classId))
    .map(course => course.subject)
    .join(', ');
}
</script>

<template>
  <BaseTable>
    <template #title>Classes</template>

    <template #head>
      <tr>
        <th>ID</th>
        <th>Alias</th>
        <th>Courses</th>
      </tr>
    </template>

    <template #body>
      <tr v-for="cls in classes" :key="cls.id">
        <td>{{ cls.id }}</td>
        <td>
          <input
            v-model="cls.alias"
            @change="onAliasChange(cls.id, cls.alias)"
            class="alias-input"
          />
        </td>
        <td class="courses-cell">
          {{ getCourseSubjectsForClass(cls.id) || '—' }}
        </td>
      </tr>
    </template>
  </BaseTable>
</template>

<style scoped>
.alias-input {
  width: 100%;
  padding: 0.25rem 0.4rem;
  border-radius: 6px;
  border: 1px solid #cbd5f5;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.alias-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.25);
}

.courses-cell {
  color: #475569;
  font-size: 0.85rem;
}
</style>
