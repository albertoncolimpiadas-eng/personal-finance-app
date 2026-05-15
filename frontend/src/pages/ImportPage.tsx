import { FormEvent, useState } from "react";

import { api } from "../api/client";
import { EmptyState, ErrorState } from "../components/States";
import type { TransactionCsvImportResult, TransactionCsvPreview } from "../types";

export function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<TransactionCsvPreview | null>(null);
  const [result, setResult] = useState<TransactionCsvImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handlePreview(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Choose a CSV file first");
      return;
    }

    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setPreview(await api.previewTransactionsCsv(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not preview CSV");
    } finally {
      setBusy(false);
    }
  }

  async function handleConfirm() {
    if (!file) {
      setError("Choose a CSV file first");
      return;
    }

    setBusy(true);
    setError(null);
    try {
      setResult(await api.confirmTransactionsCsv(file));
      setPreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not import CSV");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stack">
      <section className="panel">
        <div className="section-header">
          <h2>CSV import</h2>
          <a className="button-link" href={api.getTransactionsCsvUrl()}>
            Download transactions CSV
          </a>
        </div>
        <form className="form-grid" onSubmit={handlePreview}>
          <label>
            CSV file
            <input
              accept=".csv,text/csv"
              type="file"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button disabled={busy} type="submit">
            {busy ? "Working..." : "Preview CSV"}
          </button>
        </form>
        {error && <ErrorState message={error} />}
      </section>

      {preview && (
        <section className="panel">
          <div className="section-header">
            <h2>Preview</h2>
            <div className="inline-controls">
              <span>{preview.valid_count} valid</span>
              <span>{preview.invalid_count} invalid</span>
              <button disabled={busy || preview.valid_count === 0} type="button" onClick={() => void handleConfirm()}>
                Confirm import
              </button>
            </div>
          </div>
          {preview.rows.length === 0 && <EmptyState message="No rows found" />}
          {preview.rows.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Account</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((row) => (
                    <tr key={row.row_number}>
                      <td>{row.row_number}</td>
                      <td>{row.date}</td>
                      <td>{row.description}</td>
                      <td>{row.amount}</td>
                      <td>{row.account_name}</td>
                      <td>{row.category_name ?? "-"}</td>
                      <td>{row.transaction_type}</td>
                      <td>{row.valid ? "Ready" : row.errors.join("; ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {result && (
        <section className="panel">
          <h2>Import result</h2>
          <p>
            Imported {result.imported_count} rows. Skipped {result.skipped_count} rows.
          </p>
        </section>
      )}
    </div>
  );
}
