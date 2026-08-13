# 🆕 What's New in This Version

Your original `app.py`, `train_model.py`, and the ML logic are **completely unchanged**. Everything below is additive.

## 1. 👤 Accounts — Sign Up / Login (React + MongoDB)

New folders: `server/` (Node + Express + MongoDB) and `client/` (React, built with Vite).

- Passwords are hashed with **bcrypt** (never stored in plain text) and sessions use **JWT**.
- Click the **"Login"** button (top right of the app) → opens the React auth app in a new tab → after logging in/signing up, it sends your session back to the main app automatically and the button changes to show your name.
- Your **preferred language** is saved to your MongoDB profile and auto-applied next time you log in.
- This is a genuinely separate service from Flask — it runs on its own port (4000) so nothing about `app.py` had to change.

## 2. 🌐 Full-page translation (not just headings)

The app already had a 12-language dictionary for menus/labels. It also had a **broken** translation function for the dynamic scheme content (search results, eligibility results, chatbot replies, scheme cards) — it was calling `api.anthropic.com` directly from the browser with no API key, so it silently failed and quietly fell back to English. That's fixed:

- `translateReply()` / `translateText()` now use the **free MyMemory translation API** (no API key needed) with client-side caching, so scheme descriptions, search results, eligibility explanations, chatbot answers, and browse-page cards are now genuinely translated — not just the labels around them.
- ⚠️ MyMemory's free tier has a daily quota (~1000–5000 words/day depending on usage). If you hit the limit, translated text will silently fall back to English for the rest of that day. For heavy production use, swap in Google Cloud Translation API (just change the `fetch` URL/response parsing inside `translateText()` — the caching and call sites stay the same).

## 3. 🔊 Audio in every supported language

The Voice Guide tab previously only had English voice options. Now:

- `voiceLangSelect` includes Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Punjabi, and Urdu.
- Selecting a non-English language auto-translates the scheme script, then reads it aloud using any matching voice installed on the user's device/OS (via the browser's built-in `speechSynthesis`).
- ⚠️ Actual voice availability depends on the visitor's operating system/browser. Windows, Android, and Chrome OS ship several Indian-language voices out of the box; if a specific voice isn't installed, it gracefully falls back to a default voice reading the translated text (a toast tells the user this happened).
- A new 🔊 "Listen" button was also added inside the scheme details modal.

## 4. 🎬 YouTube videos playing in-app

Already implemented in the original file (Scheme Video tab, embedded `<iframe>` players) — left as-is and untouched.

## 5. 🗺️ Drag-and-drop office locator

New **"Office Locator"** tab:

- A Leaflet.js map with a **draggable pin** — click-and-drag it anywhere, or click the map to reposition it.
- **"Use My Location"** button uses the browser's Geolocation API.
- **"Find Offices Near Pin"** queries the free OpenStreetMap Overpass API for government offices, town halls, and post offices within 6km, plots them on the map, and lists them with distance + a "Directions" link.
- No API key needed for the map or the office search.

---

## 🖥️ How to Run Everything Together

You now run **three** things side by side (in three terminals):

### Terminal 1 — Flask ML backend (unchanged)
```bash
cd scheme_saathi
python train_model.py     # first time only
python app.py              # http://localhost:5000
```

### Terminal 2 — Auth server (Node + Express + MongoDB)
```bash
cd scheme_saathi/server
npm install
cp .env.example .env
# Edit .env and paste in your MongoDB Atlas connection string + a random JWT_SECRET
npm start                  # http://localhost:4000
```

### Terminal 3 — React auth app
```bash
cd scheme_saathi/client
npm install
npm run dev                 # http://localhost:5173
```

Then open **http://localhost:5000** as usual — that's still the main app (Flask serves `index.html`). Click **Login** to open the React account flow in a new tab; after logging in it hands control back automatically.

### Deploying for real users
For production you'd normally build the React app (`npm run build` inside `client/`) and either serve the static build from the Node server or a static host, then set `AUTH_CLIENT_URL`/`AUTH_BACKEND` in `index.html` to your real deployed URLs instead of `localhost`.
