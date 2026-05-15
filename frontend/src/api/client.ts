import type {
  AccountCreate,
  AccountSummary,
  Budget,
  BudgetCreate,
  BudgetMonthlySummary,
  Category,
  CategoryCreate,
  DashboardMonthlySummary,
  HealthStatus,
  Transaction,
  TransactionCreate,
  TransactionFilters,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function buildApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item: { msg?: string }) => item.msg ?? JSON.stringify(item))
        .join("; ");
    }
  } catch {
    // Keep the fallback compact for users.
  }
  return `Request failed with status ${response.status}`;
}

function toQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : "";
}

export const api = {
  health: () => request<HealthStatus>("/health"),

  listAccounts: () => request<AccountSummary[]>("/accounts/summary"),
  createAccount: (payload: AccountCreate) =>
    request<AccountSummary>("/accounts", { method: "POST", body: JSON.stringify(payload) }),
  deleteAccount: (id: number) => request<void>(`/accounts/${id}`, { method: "DELETE" }),

  listCategories: () => request<Category[]>("/categories"),
  createCategory: (payload: CategoryCreate) =>
    request<Category>("/categories", { method: "POST", body: JSON.stringify(payload) }),
  deleteCategory: (id: number) => request<void>(`/categories/${id}`, { method: "DELETE" }),

  listTransactions: (filters: TransactionFilters = {}) =>
    request<Transaction[]>(`/transactions${toQuery(filters)}`),
  createTransaction: (payload: TransactionCreate) =>
    request<Transaction>("/transactions", { method: "POST", body: JSON.stringify(payload) }),

  listBudgets: () => request<Budget[]>("/budgets"),
  createBudget: (payload: BudgetCreate) =>
    request<Budget>("/budgets", { method: "POST", body: JSON.stringify(payload) }),
  getBudgetSummary: (year: number, month: number) =>
    request<BudgetMonthlySummary[]>(`/budgets/monthly-summary${toQuery({ year, month })}`),

  getDashboardSummary: (year: number, month: number) =>
    request<DashboardMonthlySummary>(
      `/dashboard/monthly-summary${toQuery({ year, month })}`,
    ),
};
