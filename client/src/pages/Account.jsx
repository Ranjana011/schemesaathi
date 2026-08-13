import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiGet, apiPatch, getSession, clearSession } from "../api.js";

const LANGUAGES = [
  "English", "Hindi", "Tamil", "Telugu", "Kannada", "Bengali",
  "Marathi", "Gujarati", "Malayalam", "Punjabi", "Odia", "Urdu",
];

export default function Account() {
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("English");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const returnTo = params.get("returnTo");

  useEffect(() => {
    const { token } = getSession();
    if (!token) { navigate(`/${returnTo ? `?returnTo=${encodeURIComponent(returnTo)}` : ""}`); return; }
    apiGet("/api/auth/me", token)
      .then((data) => { setUser(data.user); setLang(data.user.preferredLanguage || "English"); })
      .catch(() => { clearSession(); navigate("/"); });
  }, []);

  async function handleSaveLanguage() {
    const { token } = getSession();
    try {
      const data = await apiPatch("/api/auth/me", { preferredLanguage: lang }, token);
      setUser(data.user);
      localStorage.setItem("ss_user", JSON.stringify(data.user));
      if (window.opener) window.opener.postMessage({ type: "SS_AUTH", token, user: data.user }, "*");
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    clearSession();
    if (window.opener) window.opener.postMessage({ type: "SS_LOGOUT" }, "*");
    navigate("/");
  }

  if (!user) return <div className="auth-card"><p className="auth-sub">Loading...</p></div>;

  return (
    <div className="auth-card">
      <div className="auth-logo">👤</div>
      <h1 className="auth-title">My Account</h1>
      <p className="auth-sub">{user.email}</p>

      <div className="account-row"><span>Name</span><span>{user.name}</span></div>
      <div className="account-row"><span>Member since</span><span>{new Date(user.createdAt).toLocaleDateString()}</span></div>

      <label>Preferred Language</label>
      <select value={lang} onChange={(e) => setLang(e.target.value)}>
        {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
      </select>
      {error && <div className="error-box">{error}</div>}
      {saved && <div className="success-box">Saved! This will sync back to SchemeSaathi.</div>}
      <button className="btn" onClick={handleSaveLanguage}>Save Preferences</button>
      <button className="btn btn-outline" onClick={handleLogout}>Log Out</button>
    </div>
  );
}
