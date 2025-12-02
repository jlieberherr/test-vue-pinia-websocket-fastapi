<template>
  <section class="table-card">
    <header class="table-header">
      <h2 class="table-title">
        <slot name="title" />
      </h2>
      <div class="table-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="table-scroll">
      <table class="table">
        <thead>
          <slot name="head" />
        </thead>
        <tbody>
          <slot name="body" />
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.table-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.3);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.table-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-scroll {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.table thead {
  background: #f8fafc;
}

.table th,
.table td {
  padding: 0.5rem 0.6rem;
  text-align: left;
  white-space: nowrap;
}

.table th {
  font-weight: 600;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
}

.table tbody tr:nth-child(even) {
  background: #f9fafb;
}

.table tbody tr:hover {
  background: #eff6ff;
}

.table td {
  border-bottom: 1px solid #e5e7eb;
}
</style>
