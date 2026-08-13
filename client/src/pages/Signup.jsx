import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { apiPost, deliverSession } from "../api.js";

const LANGUAGES = [
  "English", "Hindi", "Tamil", "Telugu", "Kannada", "Bengali",
  "Marathi", "Gujarati", "Malayalam", "Punjabi", "Odia", "Urdu",
];

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("English");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const returnTo = params.get("returnTo");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      const data = await apiPost("/api/auth/signup", { name, email, password, preferredLanguage });
      deliverSession(data.token, data.user);
      if (returnTo) {
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
      <h1 className="auth-title">Create your account</h1>
      <p className="auth-sub">Join SchemeSaathi — free forever</p>
      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
        <label>Email</label>
        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <label>Password</label>
        <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
        <label>Preferred Language</label>
        <select value={preferredLanguage} onChange={(e) => setPreferredLanguage(e.target.value)}>
          {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
        {error && <div className="error-box">{error}</div>}
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Sign Up"}
        </button>
      </form>
      <p className="switch-link">
        Already have an account? <Link to={`/${returnTo ? `?returnTo=${encodeURIComponent(returnTo)}` : ""}`}>Log in</Link>
      </p>
    </div>
  );
}
