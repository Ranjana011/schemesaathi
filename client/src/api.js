// Base URL of the Node/Express + MongoDB auth server (see /server)
export const AUTH_BACKEND = "http://localhost:4000";

export async function apiPost(path, body, token) {
  const res = await fetch(`${AUTH_BACKEND}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

export async function apiGet(path, token) {
  const res = await fetch(`${AUTH_BACKEND}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

export async function apiPatch(path, body, token) {
  const res = await fetch(`${AUTH_BACKEND}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

// Sends the freshly-issued session back to the main SchemeSaathi tab
// (index.html) that opened this window, and stores it locally too.
export function deliverSession(token, user) {
  localStorage.setItem("ss_token", token);
  localStorage.setItem("ss_user", JSON.stringify(user));
  if (window.opener) {
    window.opener.postMessage({ type: "SS_AUTH", token, user }, "*");
  }
}

export function getSession() {
  const token = localStorage.getItem("ss_token");
  const user = JSON.parse(localStorage.getItem("ss_user") || "null");
  return { token, user };
}

export function clearSession() {
  localStorage.removeItem("ss_token");
  localStorage.removeItem("ss_user");
}
