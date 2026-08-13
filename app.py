"""
╔══════════════════════════════════════════════════════════════╗
║   SchemeSaathi - Flask Backend  (app.py)                    ║
║   Serves the ML model endpoints for the HTML frontend       ║
║   Endpoints:                                                ║
║     POST /api/search       → Search schemes by query        ║
║     POST /api/eligibility  → Check eligibility              ║
║     POST /api/chat         → Chatbot intent + response      ║
║     GET  /api/schemes      → All schemes list               ║
║     GET  /                 → Serve the HTML frontend        ║
╚══════════════════════════════════════════════════════════════╝
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import re

app = Flask(__name__, static_folder=".")
CORS(app)  # Allow HTML file to call this server

# ─────────────────────────────────────────────────────────────────
# LOAD MODELS
# ─────────────────────────────────────────────────────────────────
print("⏳ Loading ML models...")

with open("models/search_vectorizer.pkl", "rb") as f:
    search_vectorizer = pickle.load(f)
with open("models/tfidf_matrix.pkl", "rb") as f:
    tfidf_matrix = pickle.load(f)
with open("models/schemes.pkl", "rb") as f:
    SCHEMES = pickle.load(f)
with open("models/elig_model.pkl", "rb") as f:
    elig_model = pickle.load(f)
with open("models/intent_vectorizer.pkl", "rb") as f:
    intent_vectorizer = pickle.load(f)
with open("models/intent_clf.pkl", "rb") as f:
    intent_clf = pickle.load(f)
with open("models/intent_le.pkl", "rb") as f:
    intent_le = pickle.load(f)
with open("models/encoding_maps.pkl", "rb") as f:
    enc = pickle.load(f)

print(f"✅ Models loaded. {len(SCHEMES)} schemes available.")

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def build_scheme_response(s, score=None):
    """Return a clean dict for JSON response"""
    d = {
        "id": s["id"],
        "name": s["name"],
        "full": s["full"],
        "cat": s["cat"],
        "desc": s["desc"],
        "eligibility": s["eligibility"],
        "ministry": s["ministry"],
        "benefit": s["benefit"],
        "link": s.get("link", ""),
    }
    if score is not None:
        d["score"] = round(float(score), 3)
    return d

def generate_simple_explanation(scheme, lang="English"):
    """Generate a plain-text explanation from scheme data (no API needed)"""
    s = scheme
    text = f"""📋 {s['full']}

🏛️ Ministry: {s['ministry']}

✅ What is this scheme?
{s['desc']}

👥 Who can apply?
{s['eligibility']}

🎁 What do you get?
{s['benefit']}

📝 How to apply?
1. Visit your nearest Common Service Centre (CSC) or government office.
2. Carry Aadhaar card, bank passbook, income certificate, and caste certificate (if applicable).
3. Fill the application form and submit documents.
4. After verification you will receive the benefit in your bank account or as specified.
{f"5. Visit the official website: {s['link']}" if s.get("link") else ""}

📄 Documents usually needed:
• Aadhaar Card
• Bank Passbook / Account number
• Income Certificate
• Caste Certificate (if applicable)
• Residence Proof
• Passport-size photograph
"""
    return text

def generate_eligibility_explanation(eligible_schemes, profile):
    """Generate a friendly text listing eligible schemes"""
    if not eligible_schemes:
        return "Based on your profile, no specific schemes were matched. Please check with your local government office or try adjusting your profile details."

    lines = [f"Based on your profile, here are the schemes you are likely eligible for:\n"]

    by_cat = {}
    for s in eligible_schemes:
        by_cat.setdefault(s["cat"], []).append(s)

    cat_emoji = {"farmer":"🌾","health":"🏥","housing":"🏠","employment":"💼","women":"👩","education":"📚","social":"🛡️"}
    cat_label = {"farmer":"Farmer Schemes","health":"Health Schemes","housing":"Housing Schemes",
                 "employment":"Employment & Business","women":"Women Schemes","education":"Education Scholarships","social":"Social Security"}

    for cat, schemes in by_cat.items():
        lines.append(f"\n{cat_emoji.get(cat,'📋')} {cat_label.get(cat, cat.title())}")
        lines.append("─" * 40)
        for s in schemes:
            lines.append(f"✅ {s['full']}")
            lines.append(f"   Benefit: {s['benefit']}")
            lines.append(f"   Why you qualify: {s['eligibility']}")
            lines.append("")

    lines.append(f"\nTotal schemes matched: {len(eligible_schemes)}")
    lines.append("Visit your nearest CSC or government portal to apply.")
    return "\n".join(lines)

def chatbot_response(query, intent):
    """Generate response based on detected intent"""
    query_lower = query.lower()

    if intent == "greeting":
        return "Namaste! 🙏 I'm SchemeSaathi. I can help you find government welfare schemes, check eligibility, explain how schemes work, and tell you how to apply. What would you like to know?"

    if intent == "search_scheme":
        # Find relevant schemes using TF-IDF
        vec = search_vectorizer.transform([query])
        sims = cosine_similarity(vec, tfidf_matrix).flatten()
        top_indices = sims.argsort()[-3:][::-1]
        top = [SCHEMES[i] for i in top_indices if sims[i] > 0.05]
        if not top:
            return "I could not find schemes matching your query. Try searching for 'farmer schemes', 'health schemes', 'education scholarship', or 'housing scheme'."
        lines = [f"Here are relevant schemes I found:\n"]
        for s in top:
            lines.append(f"🔹 {s['full']}")
            lines.append(f"   {s['desc'][:120]}...")
            lines.append(f"   Benefit: {s['benefit']}")
            lines.append("")
        return "\n".join(lines)

    if intent == "explain_scheme":
        # Find the most mentioned scheme
        vec = search_vectorizer.transform([query])
        sims = cosine_similarity(vec, tfidf_matrix).flatten()
        best_idx = sims.argmax()
        if sims[best_idx] > 0.05:
            s = SCHEMES[best_idx]
            return generate_simple_explanation(s)
        return "Please specify the scheme name. For example: 'Explain PM Kisan' or 'What is Ayushman Bharat'."

    if intent == "how_to_apply":
        vec = search_vectorizer.transform([query])
        sims = cosine_similarity(vec, tfidf_matrix).flatten()
        best_idx = sims.argmax()
        if sims[best_idx] > 0.05:
            s = SCHEMES[best_idx]
            return f"""How to apply for {s['full']}:

Step 1: Visit your nearest Common Service Centre (CSC) or gram panchayat office.
Step 2: Collect the application form for {s['name']}.
Step 3: Fill the form with your personal details.
Step 4: Attach required documents (Aadhaar, bank passbook, income proof, caste certificate if needed).
Step 5: Submit the form to the concerned officer.
Step 6: Get an acknowledgement receipt with application number.
Step 7: Track status online or at the local office.
{f"Official website: {s['link']}" if s.get("link") else ""}

Tip: You can also apply online at the official government portal or through the Umang app."""
        return "Please specify the scheme you want to apply for. For example: 'How to apply for PM Kisan?'"

    if intent == "documents_needed":
        return """Common documents needed for most government schemes:

📄 Identity Proof:
• Aadhaar Card (most important)
• Voter ID Card
• PAN Card (for financial schemes)

🏠 Address/Residence Proof:
• Aadhaar Card
• Electricity Bill / Ration Card

💰 Income Proof:
• Income Certificate from Tehsildar
• BPL Card (if applicable)

📚 Category Certificate:
• Caste Certificate (for OBC/SC/ST schemes)
• Disability Certificate (for disability schemes)

🏦 Bank Details:
• Bank Passbook (account linked to Aadhaar)

📸 Photograph:
• Passport-size photographs

Note: Exact documents vary by scheme. Always confirm with the local government office before applying."""

    if intent == "check_eligibility":
        return "To check your eligibility, please click the '✅ Eligibility' tab at the top and fill in your details like age, gender, category, income, and occupation. I will then match you with all schemes you qualify for!"

    # Default: search
    vec = search_vectorizer.transform([query])
    sims = cosine_similarity(vec, tfidf_matrix).flatten()
    top_indices = sims.argsort()[-3:][::-1]
    top = [SCHEMES[i] for i in top_indices if sims[i] > 0.05]
    if top:
        lines = ["Here's what I found:\n"]
        for s in top:
            lines.append(f"🔹 {s['full']}: {s['benefit']}")
        lines.append("\nAsk me to explain any of these in detail!")
        return "\n".join(lines)
    return "I'm not sure about that. You can ask me about specific government schemes, eligibility criteria, application process, or required documents."

# ─────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    """Return all schemes for Browse panel"""
    return jsonify({
        "success": True,
        "schemes": [build_scheme_response(s) for s in SCHEMES],
        "count": len(SCHEMES)
    })

@app.route("/api/search", methods=["POST"])
def search():
    """Search schemes using TF-IDF cosine similarity"""
    data = request.get_json()
    query = data.get("query", "").strip()
    top_n = data.get("top_n", 4)
    lang = data.get("lang", "English")

    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400

    # TF-IDF search
    query_vec = search_vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = sims.argsort()[-top_n:][::-1]

    results = []
    for idx in top_indices:
        if sims[idx] > 0.02:
            scheme = SCHEMES[idx]
            explanation = generate_simple_explanation(scheme, lang)
            result = build_scheme_response(scheme, sims[idx])
            result["explanation"] = explanation
            results.append(result)

    if not results:
        return jsonify({
            "success": True,
            "results": [],
            "message": "No matching schemes found. Try different keywords like 'farmer', 'health', 'education', 'housing'."
        })

    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "count": len(results)
    })

@app.route("/api/eligibility", methods=["POST"])
def eligibility():
    """Check eligibility using Random Forest model"""
    data = request.get_json()

    try:
        age = int(data.get("age", 30))
        gender = enc["gender_map"].get(data.get("gender", "Male"), 0)
        category = enc["category_map"].get(data.get("category", "General"), 0)
        income_raw = data.get("income", "1 to 2.5 lakh")
        income = enc["income_map"].get(income_raw, 175000)
        occupation = enc["occupation_map"].get(data.get("occupation", "Unemployed"), 3)
        residence = enc["residence_map"].get(data.get("residence", "Rural"), 0)
        bpl = int(data.get("bpl", False))
        marital = enc["marital_map"].get(data.get("marital", "Single"), 0)
        education = enc["edu_map"].get(data.get("education", "No Formal Education"), 0)
    except (ValueError, KeyError) as e:
        return jsonify({"success": False, "error": f"Invalid input: {str(e)}"}), 400

    # Feature vector
    X = np.array([[age, gender, category, income, occupation, residence, bpl, marital, education]])

    # ML prediction
    Y_pred = elig_model.predict(X)[0]
    eligible_indices = np.where(Y_pred == 1)[0]
    eligible_ids = [enc["scheme_ids"][i] for i in eligible_indices]

    # Also run rule-based check for accuracy
    gender_str = data.get("gender", "Male")
    occupation_str = data.get("occupation", "Unemployed")
    residence_str = data.get("residence", "Rural")
    category_str = data.get("category", "General")
    bpl_bool = bool(data.get("bpl", False))

    rule_eligible_ids = []
    for s in SCHEMES:
        if age < s["age_min"] or age > s["age_max"]:
            continue
        if gender_str not in s["gender"]:
            continue
        if category_str not in s["category"]:
            continue
        if income > s["income_max"]:
            continue
        if occupation_str not in s["occupation"]:
            continue
        if residence_str not in s["residence"]:
            continue
        if s["bpl_required"] and not bpl_bool:
            continue
        rule_eligible_ids.append(s["id"])

    # Combine ML + rule-based (union for maximum coverage)
    combined_ids = list(set(eligible_ids) | set(rule_eligible_ids))

    eligible_schemes = [s for s in SCHEMES if s["id"] in combined_ids]
    explanation = generate_eligibility_explanation(eligible_schemes, data)

    return jsonify({
        "success": True,
        "eligible_count": len(eligible_schemes),
        "eligible_schemes": [build_scheme_response(s) for s in eligible_schemes],
        "explanation": explanation,
        "profile_summary": {
            "age": age,
            "gender": data.get("gender"),
            "category": data.get("category"),
            "income": income_raw,
            "occupation": data.get("occupation"),
            "residence": data.get("residence"),
            "bpl": bpl_bool
        }
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chatbot endpoint with intent classification"""
    data = request.get_json()
    message = data.get("message", "").strip()
    lang = data.get("lang", "English")

    if not message:
        return jsonify({"success": False, "error": "Message required"}), 400

    # Classify intent
    msg_vec = intent_vectorizer.transform([message.lower()])
    intent_pred = intent_clf.predict(msg_vec)[0]
    intent = intent_le.inverse_transform([intent_pred])[0]
    intent_proba = intent_clf.predict_proba(msg_vec)[0].max()

    # Generate response
    response = chatbot_response(message, intent)

    return jsonify({
        "success": True,
        "response": response,
        "intent": intent,
        "confidence": round(float(intent_proba), 3)
    })

@app.route("/api/scheme/<int:scheme_id>", methods=["GET"])
def get_scheme(scheme_id):
    """Get single scheme with full explanation"""
    scheme = next((s for s in SCHEMES if s["id"] == scheme_id), None)
    if not scheme:
        return jsonify({"success": False, "error": "Scheme not found"}), 404
    result = build_scheme_response(scheme)
    result["explanation"] = generate_simple_explanation(scheme)
    return jsonify({"success": True, "scheme": result})

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  🪷  SchemeSaathi ML Backend  ")
    print("="*55)
    print(f"  Schemes loaded: {len(SCHEMES)}")
    print("  Endpoints ready:")
    print("    GET  /                   → HTML frontend")
    print("    GET  /api/schemes        → All schemes")
    print("    POST /api/search         → Search schemes")
    print("    POST /api/eligibility    → Eligibility check")
    print("    POST /api/chat           → Chatbot")
    print("="*55)
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"  ▶  Open browser: http://localhost:{port}")
    print("="*55 + "\n")
    # host=0.0.0.0 is required on cloud hosts (Render/Railway/etc.) so the
    # platform's proxy can actually reach the app. debug is OFF unless
    # FLASK_DEBUG=true is set, since Flask's debug/reloader mode is unsafe
    # to expose publicly.
    app.run(host="0.0.0.0", debug=debug_mode, port=port)
