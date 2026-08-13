# 🪷 SchemeSaathi – ML-Powered Government Scheme Simplifier
## Complete Setup Guide for VS Code

> 🆕 **New in this version:** accounts (React + MongoDB), full dynamic-content translation, multi-language audio, and a drag-and-drop office locator. See **[WHATS_NEW.md](./WHATS_NEW.md)** for details and the full run instructions for all three services (Flask + Node/Mongo + React).

---

## 📁 Project File Structure

```
scheme_saathi/
│
├── train_model.py      ← ML model training (run FIRST) — unchanged
├── app.py              ← Flask backend server — unchanged
├── index.html          ← Frontend (linked to Flask) — extended with new features
├── requirements.txt    ← Python packages
├── README.md           ← This file
├── WHATS_NEW.md         ← 🆕 New features + full run instructions
│
├── server/             ← 🆕 Node + Express + MongoDB auth backend
│   └── src/
│       ├── server.js
│       ├── models/User.js
│       ├── routes/auth.js
│       └── middleware/auth.js
│
├── client/             ← 🆕 React login/signup/account app (Vite)
│   └── src/
│       ├── main.jsx
│       ├── api.js
│       └── pages/ (Login.jsx, Signup.jsx, Account.jsx)
│
└── models/             ← Auto-created after training
    ├── search_vectorizer.pkl
    ├── tfidf_matrix.pkl
    ├── schemes.pkl
    ├── elig_model.pkl
    ├── intent_vectorizer.pkl
    ├── intent_clf.pkl
    ├── intent_le.pkl
    └── encoding_maps.pkl
```

---

## 🖥️ How to Open & Run in VS Code (Step by Step)

### STEP 1 — Open the project folder in VS Code

1. Open **VS Code**
2. Click **File → Open Folder**
3. Navigate to your `scheme_saathi` folder and click **Select Folder**
4. You will see all the files on the left sidebar

---

### STEP 2 — Open the Terminal inside VS Code

- Press **Ctrl + ` ** (backtick key, below Escape)  
  OR go to **Terminal → New Terminal** from the top menu bar

---

### STEP 3 — Create a Python virtual environment (recommended)

Paste this in the terminal:

```bash
python -m venv venv
```

Then activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line.

---

### STEP 4 — Install required Python packages

```bash
pip install -r requirements.txt
```

Wait for all packages to install (takes 1–2 minutes).

---

### STEP 5 — Train the ML Models

```bash
python train_model.py
```

**Expected output:**
```
✅ Loaded 30 government schemes
📚 Training Search Model (TF-IDF)...
   TF-IDF Matrix: (30, 3456)
   ✅ Search model ready
🌲 Training Eligibility Model (Random Forest)...
   Training samples: 5000
   Mean label accuracy: 0.956
   ✅ Eligibility model trained
💬 Training Chatbot Intent Classifier...
   Intent classes: ['check_eligibility', 'documents_needed', ...]
   ✅ Chatbot intent model trained
💾 Saving models...
   ✅ All models saved in /models/
✅ TRAINING COMPLETE!
```

A `models/` folder will be created automatically with 8 `.pkl` files.

---

### STEP 6 — Start the Flask Backend Server

```bash
python app.py
```

**Expected output:**
```
=======================================================
  🪷  SchemeSaathi ML Backend
=======================================================
  Schemes loaded: 30
  Endpoints ready:
    GET  /               → HTML frontend
    POST /api/search     → Search schemes
    POST /api/eligibility → Eligibility check
    POST /api/chat       → Chatbot
=======================================================
  ▶  Open browser: http://localhost:5000
=======================================================
```

---

### STEP 7 — Open the App in your Browser

Open your browser (Chrome recommended) and go to:

```
http://localhost:5000
```

The full app will load with all features working:
- 🔍 **Search** → ML-powered scheme search
- ✅ **Eligibility** → Random Forest eligibility checker
- 📋 **Browse** → All 30 schemes with details
- 💬 **Ask AI** → Intent-based chatbot
- 🎙️ **Voice Guide** → Scheme explanations read aloud, in 11 Indian languages
- 🎬 **Scheme Video** → Official YouTube videos playing in-app
- 🗺️ **Office Locator** → Drag-and-drop pin + nearby government offices
- 👤 **Login/Account** → Sign up and log in (see WHATS_NEW.md to start the auth server + React app too)

---

## 🧠 How the ML Models Work

| Feature | ML Technique | Library |
|---------|-------------|---------|
| Search | TF-IDF + Cosine Similarity | scikit-learn |
| Eligibility | Random Forest Classifier (Multi-output) | scikit-learn |
| Chatbot | TF-IDF + Random Forest Intent Classifier | scikit-learn |
| Training Data | 5000 synthetic samples (rule-generated) | pandas + numpy |

---

## 🔧 Troubleshooting

**Port already in use?**
```bash
python app.py --port 5001
```
Then change `BACKEND = "http://localhost:5001"` in `index.html` (line ~942)

**Module not found?**
```bash
pip install flask flask-cors scikit-learn pandas numpy
```

**Models not found error?**
Make sure you ran `python train_model.py` first!

**CORS error in browser?**
Open `http://localhost:5000` (not by opening the HTML file directly)

---

## 📌 Quick Commands Summary

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Train models (first time only)
python train_model.py

# 3. Start server (every time)
python app.py

# 4. Open browser
# http://localhost:5000
```
