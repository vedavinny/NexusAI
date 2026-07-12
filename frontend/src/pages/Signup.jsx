import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, signup } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup({ email, password, fullName });
      const { access_token } = await login({ email, password });
      signIn(access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Couldn't create your account. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15 font-display text-lg font-semibold text-accent">
            N
          </div>
          <h1 className="font-display text-2xl font-semibold text-slate-50">Create your account</h1>
          <p className="mt-1 text-sm text-muted">Start asking questions across your documents</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-surface p-6">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Full name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface2 px-3 py-2 text-sm text-slate-100 outline-none focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder="Jane Doe"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface2 px-3 py-2 text-sm text-slate-100 outline-none focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface2 px-3 py-2 text-sm text-slate-100 outline-none focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder="At least 8 characters"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-accent py-2 text-sm font-medium text-ink transition hover:bg-accent/90 disabled:opacity-60"
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-muted">
          Already have an account?{" "}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
