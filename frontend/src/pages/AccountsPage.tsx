import { FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import type { AccountSummary, AccountType } from "../types";

const accountTypes: AccountType[] = ["cash", "current_account", "savings", "credit_card"];

export function AccountsPage() {
  const [accounts, setAccounts] = useState<AccountSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: "",
    type: "current_account" as AccountType,
    currency: "EUR",
    initial_balance: "0",
  });

  async function loadAccounts() {
    setLoading(true);
    setError(null);
    try {
      setAccounts(await api.listAccounts());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load accounts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAccounts();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createAccount(form);
      setForm({ name: "", type: "current_account", currency: "EUR", initial_balance: "0" });
      await loadAccounts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await api.deleteAccount(id);
      await loadAccounts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete account");
    }
  }

  return (
    <div className="page-grid">
      <section className="panel">
        <h2>Create account</h2>
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
              onChange={(event) => setForm({ ...form, type: event.target.value as AccountType })}
            >
              {accountTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
          <label>
            Currency
            <input
              required
              value={form.currency}
              onChange={(event) => setForm({ ...form, currency: event.target.value })}
            />
          </label>
          <label>
            Initial balance
            <input
              required
              type="number"
              step="0.01"
              value={form.initial_balance}
              onChange={(event) => setForm({ ...form, initial_balance: event.target.value })}
            />
          </label>
          <button disabled={submitting} type="submit">
            {submitting ? "Creating..." : "Create account"}
          </button>
        </form>
      </section>

      <section className="panel wide">
        <div className="section-header">
          <h2>Accounts</h2>
          <button type="button" onClick={() => void loadAccounts()}>
            Refresh
          </button>
        </div>
        {loading && <LoadingState label="Loading accounts" />}
        {error && <ErrorState message={error} />}
        {!loading && !error && accounts.length === 0 && <EmptyState message="No accounts yet" />}
        {!loading && accounts.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Currency</th>
                  <th>Initial</th>
                  <th>Current</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {accounts.map((account) => (
                  <tr key={account.id}>
                    <td>{account.name}</td>
                    <td>{account.type}</td>
                    <td>{account.currency}</td>
                    <td>{account.initial_balance}</td>
                    <td>{account.current_balance}</td>
                    <td>
                      <button type="button" onClick={() => void handleDelete(account.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
