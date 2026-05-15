import { useEffect, useState } from "react";

import { api } from "./api/client";
import { Layout, type PageKey } from "./components/Layout";
import { AccountsPage } from "./pages/AccountsPage";
import { BudgetsPage } from "./pages/BudgetsPage";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ImportPage } from "./pages/ImportPage";
import { TransactionsPage } from "./pages/TransactionsPage";
import type { HealthStatus } from "./types";

function App() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");
  const [backendStatus, setBackendStatus] = useState<HealthStatus | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        setBackendStatus(await api.health());
        setBackendError(null);
      } catch (err) {
        setBackendStatus(null);
        setBackendError(err instanceof Error ? err.message : "Backend unavailable");
      }
    }

    void checkHealth();
  }, []);

  return (
    <Layout
      activePage={activePage}
      backendError={backendError}
      backendStatus={backendStatus}
      onNavigate={setActivePage}
    >
      {activePage === "dashboard" && <DashboardPage />}
      {activePage === "accounts" && <AccountsPage />}
      {activePage === "transactions" && <TransactionsPage />}
      {activePage === "categories" && <CategoriesPage />}
      {activePage === "budgets" && <BudgetsPage />}
      {activePage === "import" && <ImportPage />}
    </Layout>
  );
}

export default App;
