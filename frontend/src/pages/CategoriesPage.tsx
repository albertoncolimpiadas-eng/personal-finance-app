import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import type { Category, CategoryType } from "../types";

export function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", type: "expense" as CategoryType, color: "#0f766e" });

  const grouped = useMemo(
    () => ({
      income: categories.filter((category) => category.type === "income"),
      expense: categories.filter((category) => category.type === "expense"),
    }),
    [categories],
  );

  async function loadCategories() {
    setLoading(true);
    setError(null);
    try {
      setCategories(await api.listCategories());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load categories");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadCategories();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await api.createCategory(form);
      setForm({ name: "", type: "expense", color: "#0f766e" });
      await loadCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create category");
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await api.deleteCategory(id);
      await loadCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete category");
    }
  }

  return (
    <div className="page-grid">
      <section className="panel">
        <h2>Create category</h2>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              required
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
            />
          </label>
          <label>
            Type
            <select
              value={form.type}
              onChange={(event) => setForm({ ...form, type: event.target.value as CategoryType })}
            >
              <option value="expense">expense</option>
              <option value="income">income</option>
            </select>
          </label>
          <label>
            Color
            <input
              value={form.color}
              onChange={(event) => setForm({ ...form, color: event.target.value })}
            />
          </label>
          <button type="submit">Create category</button>
        </form>
      </section>

      <section className="panel wide">
        <div className="section-header">
          <h2>Categories</h2>
          <button type="button" onClick={() => void loadCategories()}>
            Refresh
          </button>
        </div>
        {loading && <LoadingState label="Loading categories" />}
        {error && <ErrorState message={error} />}
        {!loading && !error && categories.length === 0 && <EmptyState message="No categories" />}
        {!loading && categories.length > 0 && (
          <div className="split-list">
            <CategoryGroup categories={grouped.income} title="Income categories" onDelete={handleDelete} />
            <CategoryGroup categories={grouped.expense} title="Expense categories" onDelete={handleDelete} />
          </div>
        )}
      </section>
    </div>
  );
}

function CategoryGroup({
  categories,
  title,
  onDelete,
}: {
  categories: Category[];
  title: string;
  onDelete: (id: number) => Promise<void>;
}) {
  return (
    <div>
      <h3>{title}</h3>
      {categories.length === 0 && <EmptyState message="Nothing here yet" />}
      <div className="item-list">
        {categories.map((category) => (
          <div className="list-row" key={category.id}>
            <span className="swatch" style={{ background: category.color }} />
            <strong>{category.name}</strong>
            <button type="button" onClick={() => void onDelete(category.id)}>
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
