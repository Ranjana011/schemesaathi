import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { apiPost, deliverSession } from "../api.js";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const returnTo = params.get("returnTo");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await apiPost("/api/auth/login", { email, password });
      deliverSession(data.token, data.user);
      if (returnTo) {
        // Give the opener tab a moment to receive postMessage, then close or redirect
        setTimeout(() => {
          if (window.opener) window.close();
          else window.location.href = returnTo;
        }, 400);
      } else {
        navigate("/account");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      <div className="auth-logo">🪷</div>
      <h1 className="auth-title">Welcome back</h1>
      <p className="auth-sub">Log in to your SchemeSaathi account</p>
      <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <label>Password</label>
        <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
        {error && <div className="error-box">{error}</div>}
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Log In"}
        </button>
      </form>
      <p className="switch-link">
        Don't have an account? <Link to={`/signup${returnTo ? `?returnTo=${encodeURIComponent(returnTo)}` : ""}`}>Sign up</Link>
      </p>
    </div>
  );
}
