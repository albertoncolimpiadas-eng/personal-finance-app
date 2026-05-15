import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import type { Budget, BudgetMonthlySummary, Category } from "../types";

const now = new Date();

export function BudgetsPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [summary, setSummary] = useState<BudgetMonthlySummary[]>([]);
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ category_id: "", limit_amount: "" });

  const expenseCategories = useMemo(
    () => categories.filter((category) => category.type === "expense"),
    [categories],
  );

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [categoryData, budgetData, summaryData] = await Promise.all([
        api.listCategories(),
        api.listBudgets(),
        api.getBudgetSummary(year, month),
      ]);
      setCategories(categoryData);
      setBudgets(budgetData);
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load budgets");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [year, month]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await api.createBudget({
        category_id: Number(form.category_id),
        year,
        month,
        limit_amount: form.limit_amount,
      });
      setForm({ category_id: "", limit_amount: "" });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create budget");
    }
  }

  return (
    <div className="stack">
      <section className="panel">
        <div className="section-header">
          <h2>Month</h2>
          <div className="inline-controls">
            <input type="number" value={year} onChange={(event) => setYear(Number(event.target.value))} />
            <select value={month} onChange={(event) => setMonth(Number(event.target.value))}>
              {Array.from({ length: 12 }, (_, index) => index + 1).map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>Create monthly budget</h2>
        <form className="form-grid dense" onSubmit={handleSubmit}>
          <label>
            Expense category
            <select
              required
              value={form.category_id}
              onChange={(event) => setForm({ ...form, category_id: event.target.value })}
            >
              <option value="">Select category</option>
              {expenseCategories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Limit
            <input
              required
              min="0.01"
              step="0.01"
              type="number"
              value={form.limit_amount}
              onChange={(event) => setForm({ ...form, limit_amount: event.target.value })}
            />
          </label>
          <button type="submit">Create budget</button>
        </form>
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Budget summary</h2>
          <span>{budgets.length} total budgets</span>
        </div>
        {loading && <LoadingState label="Loading budgets" />}
        {error && <ErrorState message={error} />}
        {!loading && !error && summary.length === 0 && (
          <EmptyState message="No budgets for this month" />
        )}
        <div className="budget-list">
          {summary.map((item) => {
            const percent = Math.min(Number(item.percentage_used), 100);
            return (
              <div className="budget-row" key={item.category.id}>
                <div>
                  <strong>{item.category.name}</strong>
                  <p>
                    Limit {item.limit_amount} · Spent {item.spent_amount} · Remaining{" "}
                    {item.remaining_amount}
                  </p>
                </div>
                <div className="progress">
                  <div style={{ width: `${percent}%` }} />
                </div>
                <span>{Number(item.percentage_used).toFixed(1)}%</span>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
