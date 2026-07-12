import { useEffect, useRef, useState } from "react";
import {
  listDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documents";

const STATUS_STYLES = {
  ready: "text-accent2",
  processing: "text-amber-400",
  failed: "text-red-400",
};

export default function DocumentPanel() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  async function refresh() {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch {
      // Ignore list loading errors
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setUploading(true);

    try {
      await uploadDocument(file);
      await refresh();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Upload failed. Please try a different PDF."
      );
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmed) return;

    try {
      await deleteDocument(id);
      await refresh();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to delete document."
      );
    }
  }

  return (
    <div className="flex h-full flex-col border-r border-border bg-surface">
      <div className="border-b border-border p-4">
        <h2 className="font-display text-sm font-semibold text-slate-100">
          Knowledge base
        </h2>

        <p className="mt-0.5 text-xs text-muted">
          PDFs available for question answering
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {documents.length === 0 ? (
          <p className="mt-6 text-center text-xs text-muted">
            No documents yet. Upload a PDF to start asking questions about it.
          </p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="rounded-lg border border-border bg-surface2 px-3 py-2 text-sm"
              >
                <p className="truncate text-slate-200">
                  {doc.filename}
                </p>

                <div className="mt-2 flex items-center justify-between text-xs">
                  <span
                    className={
                      STATUS_STYLES[doc.status] || "text-muted"
                    }
                  >
                    {doc.status}
                  </span>

                  <div className="flex items-center gap-3">
                    <span className="text-muted">
                      {doc.num_chunks} chunks
                    </span>

                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-400 hover:text-red-300 transition"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="border-t border-border p-3">
        {error && (
          <p className="mb-2 text-xs text-red-400">
            {error}
          </p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full rounded-lg border border-border bg-surface2 py-2 text-sm font-medium text-slate-200 transition hover:border-accent hover:text-accent disabled:opacity-60"
        >
          {uploading ? "Processing PDF…" : "Upload PDF"}
        </button>
      </div>
    </div>
  );
}