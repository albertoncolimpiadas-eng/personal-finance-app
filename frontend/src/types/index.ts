export type AccountType = "cash" | "current_account" | "savings" | "credit_card";
export type CategoryType = "income" | "expense";
export type TransactionType = "income" | "expense" | "transfer";

export type HealthStatus = {
  status: string;
  service: string;
};

export type AccountSummary = {
  id: number;
  name: string;
  type: AccountType;
  currency: string;
  initial_balance: string;
  current_balance: string;
};

export type AccountCreate = {
  name: string;
  type: AccountType;
  currency: string;
  initial_balance: string;
};

export type Category = {
  id: number;
  name: string;
  type: CategoryType;
  color: string;
  created_at: string;
};

export type CategoryCreate = {
  name: string;
  type: CategoryType;
  color?: string;
};

export type Transaction = {
  id: number;
  transaction_type: TransactionType;
  amount: string;
  date: string;
  description: string;
  account_id: number;
  category_id: number | null;
  target_account_id: number | null;
  notes: string | null;
  created_at: string;
};

export type TransactionCreate = {
  transaction_type: TransactionType;
  amount: string;
  date: string;
  description: string;
  account_id: number;
  category_id?: number;
  target_account_id?: number;
  notes?: string;
};

export type TransactionFilters = {
  account_id?: number;
  category_id?: number;
  transaction_type?: TransactionType;
  date_from?: string;
  date_to?: string;
  text?: string;
};

export type Budget = {
  id: number;
  category_id: number;
  year: number;
  month: number;
  limit_amount: string;
  created_at: string;
};

export type BudgetCreate = {
  category_id: number;
  year: number;
  month: number;
  limit_amount: string;
};

export type BudgetMonthlySummary = {
  category: Category;
  limit_amount: string;
  spent_amount: string;
  remaining_amount: string;
  percentage_used: string;
};

export type CategoryAggregate = {
  category: Category;
  amount: string;
};

export type DashboardMonthlySummary = {
  total_income: string;
  total_expense: string;
  net_savings: string;
  savings_rate: string;
  expenses_by_category: CategoryAggregate[];
  income_by_category: CategoryAggregate[];
  account_balances: AccountSummary[];
};
