const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">Local-first finance</p>
        <h1>Personal Finance</h1>
        <p>
          Initial React, Vite, and TypeScript scaffold is ready. Business
          features will be added in small steps.
        </p>
        <a href={`${apiBaseUrl}/health`}>Backend health check</a>
      </section>
    </main>
  );
}

export default App;
