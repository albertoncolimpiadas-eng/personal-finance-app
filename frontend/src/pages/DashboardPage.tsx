import { useEffect, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import type { DashboardMonthlySummary } from "../types";

const now = new Date();

export function DashboardPage() {
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [summary, setSummary] = useState<DashboardMonthlySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadSummary() {
    setLoading(true);
    setError(null);
    try {
      setSummary(await api.getDashboardSummary(year, month));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadSummary();
  }, [year, month]);

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

      {loading && <LoadingState label="Loading dashboard" />}
      {error && <ErrorState message={error} />}
      {!loading && summary && (
        <>
          <section className="metric-grid">
            <Metric label="Total income" value={summary.total_income} />
            <Metric label="Total expense" value={summary.total_expense} />
            <Metric label="Net savings" value={summary.net_savings} />
            <Metric label="Savings rate" value={`${Number(summary.savings_rate).toFixed(1)}%`} />
          </section>

          <section className="page-grid">
            <div className="panel">
              <h2>Account balances</h2>
              {summary.account_balances.length === 0 && <EmptyState message="No accounts yet" />}
              <div className="item-list">
                {summary.account_balances.map((account) => (
                  <div className="list-row" key={account.id}>
                    <strong>{account.name}</strong>
                    <span>{account.current_balance} {account.currency}</span>
                  </div>
                ))}
              </div>
            </div>
            <CategoryBreakdown
              emptyMessage="No expenses this month"
              items={summary.expenses_by_category}
              title="Expenses by category"
            />
            <CategoryBreakdown
              emptyMessage="No income this month"
              items={summary.income_by_category}
              title="Income by category"
            />
          </section>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CategoryBreakdown({
  emptyMessage,
  items,
  title,
}: {
  emptyMessage: string;
  items: DashboardMonthlySummary["expenses_by_category"];
  title: string;
}) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      {items.length === 0 && <EmptyState message={emptyMessage} />}
      <div className="item-list">
        {items.map((item) => (
          <div className="list-row" key={item.category.id}>
            <span className="swatch" style={{ background: item.category.color }} />
            <strong>{item.category.name}</strong>
            <span>{item.amount}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
