import { buildApiUrl } from "../api/client";

function HomePage() {
  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">Local-first finance</p>
        <h1>Personal Finance</h1>
        <p>
          Initial React, Vite, and TypeScript scaffold is ready. Business
          features will be added in small steps.
        </p>
        <a href={buildApiUrl("/health")}>Backend health check</a>
      </section>
    </main>
  );
}

export default HomePage;
