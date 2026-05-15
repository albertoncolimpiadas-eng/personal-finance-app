import type { ReactNode } from "react";
import type { HealthStatus } from "../types";

export type PageKey =
  | "dashboard"
  | "accounts"
  | "transactions"
  | "categories"
  | "budgets"
  | "import";

type LayoutProps = {
  activePage: PageKey;
  backendStatus: HealthStatus | null;
  backendError: string | null;
  children: ReactNode;
  onNavigate: (page: PageKey) => void;
};

const navItems: Array<{ key: PageKey; label: string }> = [
  { key: "dashboard", label: "Dashboard" },
  { key: "accounts", label: "Accounts" },
  { key: "transactions", label: "Transactions" },
  { key: "categories", label: "Categories" },
  { key: "budgets", label: "Budgets" },
  { key: "import", label: "Import" },
];

export function Layout({
  activePage,
  backendStatus,
  backendError,
  children,
  onNavigate,
}: LayoutProps) {
  const activeLabel = navItems.find((item) => item.key === activePage)?.label ?? "Dashboard";
  const isReachable = backendStatus?.status === "ok";

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <span>Finance</span>
          <small>Local-first</small>
        </div>
        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map((item) => (
            <button
              className={item.key === activePage ? "nav-item active" : "nav-item"}
              key={item.key}
              onClick={() => onNavigate(item.key)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Personal finance</p>
            <h1>{activeLabel}</h1>
          </div>
          <div className={isReachable ? "status ok" : "status error"}>
            <span className="status-dot" />
            {isReachable ? backendStatus.service : backendError ?? "Backend unavailable"}
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
