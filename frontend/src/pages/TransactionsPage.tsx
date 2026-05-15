import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import type {
  AccountSummary,
  Category,
  Transaction,
  TransactionCreate,
  TransactionFilters,
  TransactionType,
} from "../types";

const today = new Date().toISOString().slice(0, 10);

export function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<AccountSummary[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    transaction_type: "expense" as TransactionType,
    amount: "",
    date: today,
    description: "",
    account_id: "",
    category_id: "",
    target_account_id: "",
    notes: "",
  });

  const visibleCategories = useMemo(() => {
    if (form.transaction_type === "income") {
      return categories.filter((category) => category.type === "income");
    }
    if (form.transaction_type === "expense") {
      return categories.filter((category) => category.type === "expense");
    }
    return categories;
  }, [categories, form.transaction_type]);

  async function loadBaseData() {
    setLoading(true);
    setError(null);
    try {
      const [accountData, categoryData] = await Promise.all([
        api.listAccounts(),
        api.listCategories(),
      ]);
      setAccounts(accountData);
      setCategories(categoryData);
      setTransactions(await api.listTransactions(filters));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load transactions");
    } finally {
      setLoading(false);
    }
  }

  async function loadTransactions(nextFilters = filters) {
    setLoading(true);
    setError(null);
    try {
      setTransactions(await api.listTransactions(nextFilters));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load transactions");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadBaseData();
  }, []);

  async function handleFilter(event: FormEvent) {
    event.preventDefault();
    await loadTransactions(filters);
  }

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError(null);
    const payload: TransactionCreate = {
      transaction_type: form.transaction_type,
      amount: form.amount,
      date: form.date,
      description: form.description,
      account_id: Number(form.account_id),
      notes: form.notes || undefined,
    };

    if (form.transaction_type === "transfer") {
      payload.target_account_id = Number(form.target_account_id);
    } else {
      payload.category_id = Number(form.category_id);
    }

    try {
      await api.createTransaction(payload);
      setForm({
        transaction_type: "expense",
        amount: "",
        date: today,
        description: "",
        account_id: "",
        category_id: "",
        target_account_id: "",
        notes: "",
      });
      await loadTransactions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create transaction");
    }
  }

  function categoryName(id: number | null) {
    return categories.find((category) => category.id === id)?.name ?? "-";
  }

  function accountName(id: number | null) {
    return accounts.find((account) => account.id === id)?.name ?? "-";
  }

  return (
    <div className="stack">
      <section className="panel">
        <h2>Create transaction</h2>
        <form className="form-grid dense" onSubmit={handleCreate}>
          <label>
            Type
            <select
              value={form.transaction_type}
              onChange={(event) =>
                setForm({
                  ...form,
                  transaction_type: event.target.value as TransactionType,
                  category_id: "",
                  target_account_id: "",
                })
              }
            >
              <option value="income">income</option>
              <option value="expense">expense</option>
              <option value="transfer">transfer</option>
            </select>
          </label>
          <label>
            Amount
            <input
              required
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(event) => setForm({ ...form, amount: event.target.value })}
            />
          </label>
          <label>
            Date
            <input
              required
              type="date"
              value={form.date}
              onChange={(event) => setForm({ ...form, date: event.target.value })}
            />
          </label>
          <label>
            Description
            <input
              required
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </label>
          <label>
            Account
            <select
              required
              value={form.account_id}
              onChange={(event) => setForm({ ...form, account_id: event.target.value })}
            >
              <option value="">Select account</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </label>
          {form.transaction_type === "transfer" ? (
            <label>
              Target account
              <select
                required
                value={form.target_account_id}
                onChange={(event) => setForm({ ...form, target_account_id: event.target.value })}
              >
                <option value="">Select target</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <label>
              Category
              <select
                required
                value={form.category_id}
                onChange={(event) => setForm({ ...form, category_id: event.target.value })}
              >
                <option value="">Select category</option>
                {visibleCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label>
            Notes
            <input
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
            />
          </label>
          <button type="submit">Create transaction</button>
        </form>
      </section>

      <section className="panel">
        <h2>Filters</h2>
        <form className="form-grid dense" onSubmit={handleFilter}>
          <label>
            From
            <input
              type="date"
              value={filters.date_from ?? ""}
              onChange={(event) => setFilters({ ...filters, date_from: event.target.value })}
            />
          </label>
          <label>
            To
            <input
              type="date"
              value={filters.date_to ?? ""}
              onChange={(event) => setFilters({ ...filters, date_to: event.target.value })}
            />
          </label>
          <label>
            Account
            <select
              value={filters.account_id ?? ""}
              onChange={(event) =>
                setFilters({ ...filters, account_id: event.target.value ? Number(event.target.value) : undefined })
              }
            >
              <option value="">All</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Category
            <select
              value={filters.category_id ?? ""}
              onChange={(event) =>
                setFilters({ ...filters, category_id: event.target.value ? Number(event.target.value) : undefined })
              }
            >
              <option value="">All</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Type
            <select
              value={filters.transaction_type ?? ""}
              onChange={(event) =>
                setFilters({
                  ...filters,
                  transaction_type: event.target.value ? (event.target.value as TransactionType) : undefined,
                })
              }
            >
              <option value="">All</option>
              <option value="income">income</option>
              <option value="expense">expense</option>
              <option value="transfer">transfer</option>
            </select>
          </label>
          <label>
            Search
            <input
              value={filters.text ?? ""}
              onChange={(event) => setFilters({ ...filters, text: event.target.value })}
            />
          </label>
          <button type="submit">Apply filters</button>
        </form>
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Transactions</h2>
          <button type="button" onClick={() => void loadTransactions()}>
            Refresh
          </button>
        </div>
        {loading && <LoadingState label="Loading transactions" />}
        {error && <ErrorState message={error} />}
        {!loading && !error && transactions.length === 0 && <EmptyState message="No transactions found" />}
        {!loading && transactions.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Type</th>
                  <th>Account</th>
                  <th>Category</th>
                  <th>Target</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>{transaction.date}</td>
                    <td>{transaction.description}</td>
                    <td>{transaction.transaction_type}</td>
                    <td>{accountName(transaction.account_id)}</td>
                    <td>{categoryName(transaction.category_id)}</td>
                    <td>{accountName(transaction.target_account_id)}</td>
                    <td>{transaction.amount}</td>
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
