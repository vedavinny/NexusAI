import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api/chat";
import DocumentPanel from "../components/DocumentPanel";
import MessageBubble from "../components/MessageBubble";
import { useAuth } from "../context/AuthContext";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signOut } = useAuth();
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const result = await askQuestion({ sessionId, question });
      setSessionId(result.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err.response?.data?.detail ||
            "Something went wrong answering that. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen bg-ink">
      <aside className="w-72 shrink-0">
        <DocumentPanel />
      </aside>

      <main className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border px-6 py-4">
          <div>
            <h1 className="font-display text-base font-semibold text-slate-50">NexusAI</h1>
            <p className="text-xs text-muted">Ask questions grounded in your documents</p>
          </div>
          <button
            onClick={signOut}
            className="rounded-lg border border-border px-3 py-1.5 text-xs text-muted transition hover:border-accent hover:text-accent"
          >
            Sign out
          </button>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15 font-display text-xl font-semibold text-accent">
                N
              </div>
              <p className="text-sm text-muted">
                Upload a PDF on the left, then ask a question about it here.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <MessageBubble key={idx} role={msg.role} content={msg.content} sources={msg.sources} />
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-border bg-surface px-4 py-2.5 text-sm text-muted">
                Thinking…
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSend} className="border-t border-border px-6 py-4">
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something about your documents…"
              className="flex-1 rounded-lg border border-border bg-surface2 px-4 py-2.5 text-sm text-slate-100 outline-none focus:border-accent focus:ring-1 focus:ring-accent"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-ink transition hover:bg-accent/90 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
