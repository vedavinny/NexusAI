import { useState } from "react";

export default function MessageBubble({ role, content, sources }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-2xl ${isUser ? "items-end" : "items-start"} flex flex-col gap-1.5`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-accent text-ink"
              : "border border-border bg-surface text-slate-100"
          }`}
        >
          {content}
        </div>

        {!isUser && sources?.length > 0 && (
          <div>
            <button
              onClick={() => setShowSources((s) => !s)}
              className="text-xs text-muted transition hover:text-accent"
            >
              {showSources ? "Hide sources" : `View ${sources.length} source${sources.length > 1 ? "s" : ""}`}
            </button>

            {showSources && (
              <div className="mt-2 space-y-2">
                {sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-border bg-surface2 px-3 py-2 text-xs"
                  >
                    <div className="mb-1 flex items-center justify-between">
                      <span className="font-mono text-accent2">{source.document_name}</span>
                      <span className="text-muted">{(source.score * 100).toFixed(0)}% match</span>
                    </div>
                    <p className="text-muted line-clamp-3">{source.chunk_text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
