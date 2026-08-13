# Deploying SchemeSaathi to the Cloud

You have 3 services. Each one becomes its own deployment:

| Service | What it is | Where to deploy | Free tier? |
|---|---|---|---|
| Flask ML backend (`app.py` + `index.html`) | Serves the main site + ML APIs | **Render** (Web Service) | Yes |
| Node/Express auth server (`server/`) | Login/signup, talks to MongoDB | **Render** (Web Service) | Yes |
| MongoDB | User accounts DB | **MongoDB Atlas** | Yes (M0 cluster) |
| React auth app (`client/`) | Login/signup/account UI | **Render Static Site** or **Vercel** | Yes |

Render is the easiest single place to host all of them, and it's what the app's code already assumes (see the `Render/production` comment in `index.html`). Everything below uses Render + MongoDB Atlas + Vercel, but swap in Railway/Fly.io if you prefer — the steps are nearly identical.

---

## 0. What I already changed in your files

- **`app.py`** — now reads the port from the `PORT` environment variable and binds to `0.0.0.0` (required by every cloud host — the old `app.run(debug=True, port=5000)` only listens on localhost and won't be reachable from outside the container). Debug mode is off unless you set `FLASK_DEBUG=true`.
- **`requirements.txt`** — added `gunicorn`, the production server Render will actually run (not Flask's built-in dev server).
- **`Procfile`** — tells Render/Railway how to start the app: `gunicorn app:app`.
- **`index.html`** — the old code guessed the auth server's URL as `yourdomain:4000`. That only works on a VPS where you control raw ports. On Render/Vercel each service gets its own HTTPS domain, so I replaced it with two constants (`PROD_AUTH_BACKEND`, `PROD_AUTH_CLIENT_URL`) near the top of the auth section — **you'll paste your real deployed URLs into those** once you have them (step 4 below).

---

## 1. Push to GitHub

Cloud hosts deploy from a git repo. If you haven't already:

```bash
cd scheme_saathi
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/<you>/scheme_saathi.git
git push -u origin main
```

Your `.gitignore` already excludes `models/`, `node_modules/`, and `.env` — good, keep it that way. Models get regenerated at build time (next step), and secrets get set as environment variables on the host, never committed.

---

## 2. Deploy the Flask ML backend (Render Web Service)

1. Go to **render.com → New → Web Service**, connect your GitHub repo.
2. **Root directory:** leave blank (repo root, where `app.py` lives).
3. **Build command:**
   ```
   pip install -r requirements.txt && python train_model.py
   ```
   (Running `train_model.py` here regenerates the `models/*.pkl` files during the build, since they're gitignored.)
4. **Start command:**
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
   ```
5. **Environment variables:** none required for this service unless you want `FLASK_DEBUG=true` temporarily for debugging.
6. Deploy. Render gives you a URL like `https://schemesaathi.onrender.com` — that's your main site.

---

## 3. Set up MongoDB Atlas

1. [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) → create a free **M0** cluster.
2. **Database Access** → add a user with a password.
3. **Network Access** → add `0.0.0.0/0` (allow from anywhere — needed since Render's IPs aren't fixed on the free tier).
4. **Connect → Drivers** → copy the connection string, e.g.
   `mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/schemesaathi`

---

## 4. Deploy the Node/Express auth server (Render Web Service)

1. **New → Web Service**, same repo.
2. **Root directory:** `server`
3. **Build command:** `npm install`
4. **Start command:** `npm start` (or `node src/server.js` if that's your entry point)
5. **Environment variables:**
   | Key | Value |
   |---|---|
   | `MONGO_URI` | your Atlas connection string from step 3 |
   | `JWT_SECRET` | any long random string |
   | `PORT` | Render sets this automatically — don't hardcode 4000 in production |
   | `CLIENT_URL` / `CORS_ORIGIN` | your Flask site's URL from step 2, e.g. `https://schemesaathi.onrender.com` (whatever env var your `server.js` CORS config actually reads — check it and match the name) |
6. Deploy → you get a URL like `https://schemesaathi-auth.onrender.com`.
7. **Check `server/src/server.js`'s CORS setup** allows requests from your Flask domain — by default Express CORS is locked to `localhost`, unlike the Flask side which already has `CORS(app)` wide open.

---

## 5. Deploy the React client (`client/`)

Easiest option — **Vercel**:

1. [vercel.com](https://vercel.com) → New Project → import the repo.
2. **Root directory:** `client`
3. Framework preset: Vite (auto-detected).
4. **Environment variables:** whatever your `client/src/api.js` uses for the auth backend base URL — set it to your Render auth URL from step 4 (e.g. `https://schemesaathi-auth.onrender.com`).
5. Deploy → you get a URL like `https://schemesaathi-account.vercel.app`.

(Render Static Site works the same way if you'd rather keep everything on one platform: build command `npm install && npm run build`, publish directory `dist`.)

---

## 6. Wire the three URLs together

Open `index.html` and update the two constants I added:

```js
const PROD_AUTH_BACKEND = "https://schemesaathi-auth.onrender.com";     // from step 4
const PROD_AUTH_CLIENT_URL = "https://schemesaathi-account.vercel.app"; // from step 5
```

Commit and push — Render auto-redeploys the Flask service on every push to `main`.

---

## 7. Test end to end

- Open your Flask URL → search/eligibility/chat/voice/office locator should all work (they only ever talked to Flask, nothing to change there).
- Click **Login** → should open the deployed React app in a new tab, not localhost.
- Sign up → check the MongoDB Atlas collection to confirm a user document was created.
- Log in → back on the main tab, the button should switch to your name.

---

## Notes / gotchas

- **Render free tier sleeps** after 15 min of no traffic — the first request after idle takes ~30–50s to wake up. Fine for a student project/demo, worth mentioning if you're presenting live.
- **MyMemory translation API** (used for scheme content translation) has a daily word quota — nothing to configure, just know translations silently fall back to English if you hit it.
- If you'd rather run all three services on a **single VM** (e.g. a college server or a DigitalOcean droplet) instead of three separate PaaS deployments, the original `hostname:4000` trick in `index.html` actually works there — you'd only need to revert that one change and put Flask, Node, and a built React app behind nginx on one box. Happy to write that version too if that's your setup instead.
